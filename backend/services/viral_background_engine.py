import os
import random
import logging
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = getattr(PIL.Image, 'Resampling', PIL.Image).LANCZOS

from moviepy.editor import VideoFileClip
import moviepy.video.fx.all as vfx

logger = logging.getLogger("ViralBackgroundEngine")

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
VIRAL_DIR = os.path.join(ASSETS_DIR, "viral_backgrounds")
os.makedirs(VIRAL_DIR, exist_ok=True)

# Curated list of high-retention, satisfying gameplay compilations using search queries
VIRAL_SOURCES = {
    "subway_surfers": "ytsearch1:subway surfers gameplay no copyright 4k 60fps",
    "minecraft_parkour": "ytsearch1:minecraft parkour gameplay no copyright 4k 60fps",
    "gta_v_ramps": "ytsearch1:gta 5 ramp jump gameplay no copyright 4k 60fps",
    "satisfying_compilation": "ytsearch1:satisfying video compilation no copyright kinetic sand 4k 60fps"
}

def init_backgrounds():
    """
    Downloads the base compilations via yt-dlp if they do not exist locally.
    This should be run once during setup or deployment.
    """
    logger.info("Initializing Viral Background Engine...")
    import yt_dlp
    
    for name, url in VIRAL_SOURCES.items():
        file_path_template = os.path.join(VIRAL_DIR, f"{name}.%(ext)s")
        # Check if any file starting with name exists (could be .webm, .mp4, .mkv)
        existing_files = [f for f in os.listdir(VIRAL_DIR) if f.startswith(name) and not f.endswith('.part')]
        if existing_files:
            logger.info(f"[OK] Background '{name}' already exists.")
            continue
            
        logger.info(f"Downloading Viral Background: {name} from {url}")
        
        ydl_opts = {
            'format': 'bestvideo/best', 
            'outtmpl': file_path_template,
            'quiet': True,
            'no_warnings': True,
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            logger.info(f"[SUCCESS] Downloaded {name}")
        except Exception as e:
            logger.error(f"[FAIL] Could not download {name}: {e}")

def get_random_background_clip(duration: float, width: int = 1080, height: int = 1920) -> VideoFileClip:
    """
    Selects a random downloaded compilation, picks a random timestamp, and returns a VideoFileClip
    of the specified duration, perfectly cropped to 9:16 aspect ratio.
    """
    available_files = [f for f in os.listdir(VIRAL_DIR) if f.endswith(('.mp4', '.webm', '.mkv'))]
    
    if not available_files:
        logger.warning("No viral backgrounds found locally! Falling back to solid gradient.")
        return None
        
    selected_file = random.choice(available_files)
    video_path = os.path.join(VIRAL_DIR, selected_file)
    logger.info(f"Viral Engine selected background: {selected_file}")
    
    try:
        clip = VideoFileClip(video_path)
        
        speed_factor = 1.75
        required_source_duration = duration * speed_factor

        # Calculate random start time
        if clip.duration <= required_source_duration:
            start_time = 0.0
            end_time = clip.duration
        else:
            max_start = clip.duration - required_source_duration
            start_time = random.uniform(0.0, max_start)
            end_time = start_time + required_source_duration
            
        logger.info(f"Slicing clip from {start_time:.1f}s to {end_time:.1f}s (Speed: {speed_factor}x)")
        subclip = clip.subclip(start_time, end_time)
        
        # Apply speedup
        subclip = subclip.fx(vfx.speedx, speed_factor)
        
        # Resize vertically and crop horizontally for 9:16
        subclip = subclip.resize(height=height)
        if subclip.w > width:
            x_center = subclip.w / 2
            subclip = subclip.crop(x1=x_center - width/2, y1=0, x2=x_center + width/2, y2=height)
            
        # Strip original audio
        if getattr(subclip, "audio", None):
            subclip = subclip.without_audio()
        return subclip
        
    except Exception as e:
        logger.error(f"Error processing viral background clip: {e}")
        return None
