import time
import os
import sys
import json
import random
import glob
import logging
import traceback
from datetime import datetime, timedelta

# Force UTF-8 encoding for Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure the backend directory is on sys.path for imports
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BACKEND_DIR)
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

import schedule
import httpx
from sqlmodel import Session, select
from database import engine, Quote

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(), logging.FileHandler(os.path.join(BACKEND_DIR, "scheduler.log"))]
)
logger = logging.getLogger("ChronosScheduler")

API_BASE = "http://127.0.0.1:8000"
OFFSET_FILE = os.path.join(BACKEND_DIR, "last_quote_id.txt")
UPLOADS_DIR = os.path.join(BACKEND_DIR, "assets", "uploads")
RUN_LOG_FILE = os.path.join(BACKEND_DIR, "scheduler_runs.json")

# ── Schedule Configuration ──────────────────────────────────────
SCHEDULED_TIMES = ["09:00", "17:00"]

# ══════════════════════════════════════════════════════════════════
# UTILITY: Backend Health Check with Retry
# ══════════════════════════════════════════════════════════════════
def wait_for_backend(max_retries=30, interval=10):
    """Wait until the backend API is alive. Retries up to max_retries times."""
    logger.info("Waiting for backend to become available...")
    for attempt in range(1, max_retries + 1):
        try:
            resp = httpx.get(f"{API_BASE}/docs", timeout=5.0)
            if resp.status_code == 200:
                logger.info(f"[OK] Backend is ALIVE (attempt {attempt}/{max_retries})")
                return True
        except Exception:
            pass
        logger.info(f"   Backend not ready yet... (attempt {attempt}/{max_retries}, retrying in {interval}s)")
        time.sleep(interval)
    
    logger.error("[FAIL] Backend did not start within the timeout period!")
    return False

# ══════════════════════════════════════════════════════════════════
# UTILITY: Persistent Run Tracking
# ══════════════════════════════════════════════════════════════════
def load_run_log():
    """Load the record of completed runs."""
    if os.path.exists(RUN_LOG_FILE):
        try:
            with open(RUN_LOG_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {"completed_runs": []}
    return {"completed_runs": []}

def save_run_log(log_data):
    """Save the record of completed runs."""
    with open(RUN_LOG_FILE, "w") as f:
        json.dump(log_data, f, indent=2)

def record_completed_run(scheduled_time_str):
    """Record that a specific scheduled run has been completed for today."""
    log = load_run_log()
    today = datetime.now().strftime("%Y-%m-%d")
    run_key = f"{today}_{scheduled_time_str}"
    if run_key not in log["completed_runs"]:
        log["completed_runs"].append(run_key)
    # Prune entries older than 7 days to keep the file small
    cutoff = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
    log["completed_runs"] = [r for r in log["completed_runs"] if r >= cutoff]
    save_run_log(log)

def was_run_completed(scheduled_time_str, date_str=None):
    """Check if a specific scheduled run was already completed."""
    log = load_run_log()
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    run_key = f"{date_str}_{scheduled_time_str}"
    return run_key in log["completed_runs"]

# ══════════════════════════════════════════════════════════════════
# UTILITY: Smart Missed-Run Detection
# ══════════════════════════════════════════════════════════════════
def get_missed_runs():
    """Determine which scheduled runs for TODAY have been missed and not yet completed."""
    now = datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    missed = []
    
    for time_str in SCHEDULED_TIMES:
        hour, minute = map(int, time_str.split(":"))
        scheduled_dt = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Only consider runs whose time has already passed today
        if now > scheduled_dt:
            if not was_run_completed(time_str, today_str):
                missed.append(time_str)
    
    return missed

# ══════════════════════════════════════════════════════════════════
# CORE: Quote Selection
# ══════════════════════════════════════════════════════════════════
def get_next_quote():
    """Fetch the next un-generated quote from the database."""
    with Session(engine) as session:
        statement = select(Quote).where(Quote.is_used == False).order_by(Quote.id).limit(1)
        quote = session.exec(statement).first()
        
        if quote:
            logger.info(f"Selected Quote ID: {quote.id}")
            return quote
        else:
            logger.warning("No more new quotes in the database! Please add more.")
            return None

def save_quote_offset(quote_id):
    """Save the ID of the last processed quote."""
    with open(OFFSET_FILE, "w") as f:
        f.write(str(quote_id))

# ══════════════════════════════════════════════════════════════════
# CORE: Full Automation Pipeline
# ══════════════════════════════════════════════════════════════════
def run_automation_pipeline(scheduled_time_str=None):
    """Runs the end-to-end video generation and social media publishing pipeline."""
    logger.info("=" * 60)
    logger.info("Starting Automation Pipeline...")
    logger.info("=" * 60)
    
    # 1. Get Quote
    quote = get_next_quote()
    if not quote:
        # Even if no quote, record the run so we don't keep retrying
        if scheduled_time_str:
            record_completed_run(scheduled_time_str)
        return

    try:
        with httpx.Client(timeout=180.0) as client:
            # 2. Generate Script
            logger.info("Step 2: Generating Script...")
            script_res = client.post(f"{API_BASE}/api/generate-script", json={
                "quote": quote.text,
                "philosopher": getattr(quote, "philosopher_name", "Chanakya"),
                "rage_level": getattr(quote, "rage_level", 7)
            })
            script_res.raise_for_status()
            script_data = script_res.json()
            logger.info("[OK] Script Generated.")
            
            # 3. Generate Caption
            logger.info("Step 3: Generating Caption & Tags...")
            caption_res = client.post(f"{API_BASE}/api/generate-caption", json={
                "philosopher_name": getattr(quote, "philosopher_name", "Chanakya"),
                "quote_text": quote.text,
                "script_text": script_data.get("fullText", ""),
                "theme": "Harsh Truths",
                "rage_level": getattr(quote, "rage_level", 7),
                "audience_type": "General"
            })
            caption_res.raise_for_status()
            caption_data = caption_res.json()
            description_text = f"{caption_data['caption_text']}\n\n{caption_data['combined_hashtags']}"
            logger.info("[OK] Caption Generated.")
            
            # 4 & 5. Concurrently Generate Voice and Fetch Auto B-Rolls
            logger.info("Steps 4 & 5: Concurrently Generating Voiceover and Fetching B-Roll...")
            import concurrent.futures

            def generate_voice_task():
                selected_voice = "pFZP5JQG7iQjIQuC4Bku"  # Dark Cinematic (Lily)
                res = client.post(f"{API_BASE}/api/generate-voice", json={
                    "text": script_data.get("fullText", ""),
                    "voice_id": selected_voice
                })
                res.raise_for_status()
                return res.json().get("audio_path")
                
            def fetch_b_roll_task():
                try:
                    from services.scene_engine import analyze_scenes
                    from services.pexels_engine import search_and_download_video
                    
                    full_text = script_data.get("fullText", "")
                    scenes = analyze_scenes(full_text)
                    duration = script_data.get("estimatedDuration", 30)
                    
                    if scenes:
                        seg_dur = duration / len(scenes)
                        for sc in scenes:
                            theme = sc.get("theme", "cinematic")
                            keywords = sc.get("keywords", [])
                            query = f"{theme} {keywords[0] if keywords else 'aesthetic'}"
                            # Cache will be populated concurrently
                            search_and_download_video(query, min_duration=int(seg_dur) + 1)
                except Exception as e:
                    logger.error(f"Auto B-Roll pre-fetch failed: {e}")
                return True

            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                future_voice = executor.submit(generate_voice_task)
                future_broll = executor.submit(fetch_b_roll_task)
                
                audio_path = future_voice.result()
                future_broll.result() # Wait for b-roll to finish caching
                
            logger.info(f"[OK] Voiceover Generated: {audio_path}")
            logger.info(f"[OK] Auto B-Rolls cached in background.")
            
            bg_video_paths = None
            
            # Select Random Background Music
            local_audio = glob.glob(os.path.join(UPLOADS_DIR, "audio_*"))
            bg_music_path = None
            if local_audio:
                bg_music_path = os.path.abspath(random.choice(local_audio))
            
            # 6. Render Video
            logger.info("Step 6: Rendering Final Video (This will take a few minutes)...")
            video_req = {
                "script_data": script_data,
                "audio_path": audio_path,
                "bg_video_paths": bg_video_paths,
                "bg_music_path": bg_music_path,
                "bg_music_volume": 0.15,
                "caption_size": "Medium",
                "use_smart_sfx": True,
                "use_auto_b_roll": True
            }
            video_res = client.post(f"{API_BASE}/api/generate-video", json=video_req, timeout=1800.0)
            video_res.raise_for_status()
            
            video_data = video_res.json()
            final_video_path = video_data.get("video_path") or video_data.get("output_path")
            
            if not final_video_path or not os.path.exists(final_video_path):
                if final_video_path and not os.path.isabs(final_video_path):
                    potential_path = os.path.join(ROOT_DIR, final_video_path)
                    if os.path.exists(potential_path):
                        final_video_path = potential_path
            
            if not final_video_path or not os.path.exists(final_video_path):
                raise Exception(f"Video file not found at {final_video_path}")
            
            logger.info(f"✅ Video Rendered: {final_video_path}")
            
            # 7. Export to Desktop and Auto-Upload
            logger.info("Step 7: Exporting and Uploading...")
            
            desktop_dir = os.path.join(os.path.expanduser("~"), "Desktop", "Chanakya_Reel_AI_Uploads")
            os.makedirs(desktop_dir, exist_ok=True)
            
            import shutil
            timestamp = int(time.time())
            desktop_video_path = os.path.join(desktop_dir, f"Reel_Quote_{quote.id}_{timestamp}.mp4")
            desktop_caption_path = os.path.join(desktop_dir, f"Reel_Quote_{quote.id}_{timestamp}_Caption.txt")
            
            logger.info(f"Copying video to: {desktop_video_path}")
            shutil.copy2(final_video_path, desktop_video_path)
            
            logger.info(f"Saving Caption to: {desktop_caption_path}")
            with open(desktop_caption_path, "w", encoding="utf-8") as f:
                f.write("=== CAPTION/DESCRIPTION ===\n\n")
                f.write(description_text)
                
            logger.info("[OK] Export successful!")

            # --- DIRECT YOUTUBE STUDIO UPLOAD ---
            logger.info("Launching YouTube Uploader...")
            yt_script = os.path.join(BACKEND_DIR, "youtube_uploader.py")
            if os.path.exists(yt_script):
                meta_file = os.path.join(BACKEND_DIR, "temp_upload_data.json")
                with open(meta_file, "w", encoding="utf-8") as f:
                    json.dump({
                        "video_path": desktop_video_path,
                        "title": caption_data.get("caption_text", "").split('\n')[0],
                        "description": description_text
                    }, f)
                
                os.system(f"python \"{yt_script}\" \"{meta_file}\"")
                logger.info("[OK] YouTube upload script completed.")
            else:
                logger.warning(f"Could not find {yt_script}")

            # --- DIRECT INSTAGRAM WEB UPLOAD ---
            logger.info("Launching Instagram Uploader...")
            ig_script = os.path.join(BACKEND_DIR, "instagram_uploader.py")
            if os.path.exists(ig_script):
                os.system(f"python \"{ig_script}\" \"{meta_file}\"")
                logger.info("[OK] Instagram upload script completed.")
            else:
                logger.warning(f"Could not find {ig_script}")

            # 8. Mark Processed in Database
            with Session(engine) as session:
                statement = select(Quote).where(Quote.id == quote.id)
                db_quote = session.exec(statement).one()
                db_quote.is_used = True
                session.add(db_quote)
                session.commit()
                logger.info(f"[OK] Marked Quote ID {quote.id} as USED.")

            save_quote_offset(quote.id)
            
            # Record this run as completed
            if scheduled_time_str:
                record_completed_run(scheduled_time_str)
            
            logger.info(f"[SUCCESS] Pipeline Complete for Quote ID: {quote.id}")
            logger.info("=" * 60)

    except Exception as e:
        logger.error(f"[FAIL] Pipeline failed for Quote ID {quote.id}: {e}")
        logger.error(traceback.format_exc())
        # Do NOT record the run as completed so it will be retried

# ══════════════════════════════════════════════════════════════════
# CORE: Scheduled Job Wrapper
# ══════════════════════════════════════════════════════════════════
def scheduled_job(time_str):
    """Wrapper that runs the pipeline and records the run."""
    logger.info(f"[SCHEDULE] Triggered scheduled run for {time_str}")
    if was_run_completed(time_str):
        logger.info(f"Run for {time_str} was already completed today. Skipping.")
        return
    run_automation_pipeline(scheduled_time_str=time_str)

# ══════════════════════════════════════════════════════════════════
# MAIN: Entry Point
# ══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Chronos Scheduler v2.0 Started.")
    logger.info("=" * 60)
    
    # ── Step 1: Wait for Backend ──────────────────────────────
    if not wait_for_backend(max_retries=30, interval=10):
        logger.error("Exiting: Backend never became available.")
        sys.exit(1)
    
    # ── Step 2: Check for Missed Runs ─────────────────────────
    missed = get_missed_runs()
    if missed:
        logger.info(f"[CATCH-UP] Detected {len(missed)} missed run(s) for today: {missed}")
        for missed_time in missed:
            logger.info(f">> Processing missed run: {missed_time}")
            run_automation_pipeline(scheduled_time_str=missed_time)
            # Wait between catch-up runs to avoid overloading
            if len(missed) > 1:
                logger.info("Cooling down 2 minutes before next catch-up...")
                time.sleep(120)
    else:
        logger.info("[OK] No missed runs detected. All caught up!")
    
    # ── Step 3: Register Future Scheduled Runs ────────────────
    for t in SCHEDULED_TIMES:
        schedule.every().day.at(t).do(scheduled_job, time_str=t)
        logger.info(f"[SCHEDULE] Registered daily job at {t}")
    
    logger.info("Entering main loop. Checking every 60 seconds...")
    while True:
        schedule.run_pending()
        time.sleep(60)
