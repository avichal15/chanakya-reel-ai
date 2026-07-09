"""
Pexels Video Engine — Fetches stock footage dynamically based on search queries.
Uses the Pexels Video API to download 9:16 portrait videos.
"""
import requests
import os
import hashlib
import logging
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

# Load .env from project root
env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

PEXELS_API_KEY = os.getenv("PEXELS_API_KEY")
PEXELS_BASE_URL = "https://api.pexels.com/videos/search"

# Cache directory for downloaded videos
PEXELS_CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "pexels")
os.makedirs(PEXELS_CACHE_DIR, exist_ok=True)

def search_and_download_video(query: str, min_duration: int = 5) -> str | None:
    """
    Searches Pexels for a portrait video matching the query and downloads it.
    Uses basic MD5 hashing of the query for caching to avoid API limits.
    
    Args:
        query: Search term (e.g. "dark ocean", "chess board")
        min_duration: Minimum required duration in seconds
        
    Returns:
        Absolute filepath to the downloaded MP4, or None if failed.
    """
    if not PEXELS_API_KEY:
        logger.error("PEXELS_API_KEY missing from environment variables.")
        return None
        
    if not query or not query.strip():
        return None
        
    query = query.strip()
    # Create simple cache key based on query to avoid re-downloading identical concepts
    query_hash = hashlib.md5(query.lower().encode()).hexdigest()
    cache_path = os.path.join(PEXELS_CACHE_DIR, f"{query_hash}.mp4")
    
    # Return immediately if we already have a cached video for this exact query
    if os.path.exists(cache_path):
        logger.info(f"Pexels Engine: Using cached video for query '{query}'")
        return cache_path
        
    logger.info(f"Pexels Engine: Searching for '{query}'...")
    
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    # Request vertical (portrait) videos
    params = {
        "query": query,
        "orientation": "portrait",
        "size": "medium", # medium usually targets robust ~HD quality for social media (1080x1920)
        "per_page": 10 # Request a few options to find one long enough
    }
    
    try:
        response = requests.get(PEXELS_BASE_URL, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        videos = data.get("videos", [])
        
        # Fallback query strategies if nothing found
        if not videos:
            logger.warning(f"Pexels Engine: No vertical videos found for query '{query}'")
            if " " in query:
                # Try just the first word (usually the broad theme)
                broad_query = query.split()[0]
                logger.info(f"Pexels Engine: Retrying with broader query '{broad_query}'")
                params["query"] = broad_query
                response = requests.get(PEXELS_BASE_URL, headers=headers, params=params, timeout=10)
                videos = response.json().get("videos", [])
                
            if not videos:
                # Ultimate safe fallback
                logger.info(f"Pexels Engine: Retrying with safe fallback 'cinematic'")
                params["query"] = "cinematic"
                response = requests.get(PEXELS_BASE_URL, headers=headers, params=params, timeout=10)
                videos = response.json().get("videos", [])
                
        if not videos:
            logger.error("Pexels Engine: Complete failure to find any suitable videos, even with fallbacks.")
            return None
            
        # Find the first video that is long enough and has a valid file link
        target_video = None
        target_link = None
        
        for video in videos:
            if video.get("duration", 0) >= min_duration:
                # Find the highest quality HD link
                video_files = video.get("video_files", [])
                hd_files = [f for f in video_files if f.get("quality") == "hd" and f.get("file_type") == "video/mp4"]
                
                if hd_files:
                    # Sort by height to get the true vertical 1080x1920 or best match
                    best_match = sorted(hd_files, key=lambda x: x.get("height", 0), reverse=True)[0]
                    target_video = video
                    target_link = best_match.get("link")
                    break
                    
        if not target_link:
            logger.warning(f"Pexels Engine: No suitable video files found for query '{query}'")
            return None
            
        logger.info(f"Pexels Engine: Downloading video ID {target_video.get('id')} for query '{query}'")
        
        # Download the video chunked
        vid_response = requests.get(target_link, stream=True, timeout=30)
        vid_response.raise_for_status()
        
        with open(cache_path, "wb") as f:
            for chunk in vid_response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    
        return cache_path
        
    except Exception as e:
        logger.error(f"Pexels Engine: Failed to search or download video ({e})")
        return None
