import os
import sys
import uuid
import glob
from pathlib import Path
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import Session, select
from dotenv import load_dotenv

# --- FORCE UTF-8 FOR MULTILINGUAL LOGGING ---
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Load .env from backend directory explicitly
env_path = Path(__file__).resolve().parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")

from .database import create_db_and_tables, get_session, Philosopher, Quote, GeneratedScript, VideoExport

# Import Services
from .services import script_engine, voice_engine, video_engine, ingestion_engine, caption_engine, scene_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# CORS Setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure directories exist
os.makedirs("backend/assets", exist_ok=True)
os.makedirs("backend/output", exist_ok=True)

app.mount("/assets", StaticFiles(directory="backend/assets"), name="assets")
app.mount("/output", StaticFiles(directory="backend/output"), name="output")

@app.get("/")
def read_root():
    return {"message": "Viral Philosophy Reels Generator API is running"}

# --- Data Models ---
class ScriptRequest(BaseModel):
    quote: str
    philosopher: str = "Chanakya"
    rage_level: int = 5

class VoiceRequest(BaseModel):
    text: str
    voice_id: str = "JBFqnCBsd6RMkjVDRZzb"

class VideoRequest(BaseModel):
    script_data: dict
    audio_path: str
    bg_video_paths: Optional[List[str]] = None
    bg_music_path: Optional[str] = None
    bg_music_volume: float = 0.15
    caption_size: str = "Medium"
    use_smart_sfx: bool = True
    use_auto_b_roll: bool = False

class CaptionRequest(BaseModel):
    philosopher_name: str
    quote_text: str
    script_text: str
    theme: str = "Harsh Truths"
    rage_level: int = 5
    audience_type: str = "General"

# --- API Endpoints ---

@app.post("/api/generate-caption")
def generate_caption_endpoint(request: CaptionRequest):
    try:
        result = caption_engine.generate_caption(
            request.philosopher_name,
            request.quote_text,
            request.script_text,
            request.theme,
            request.rage_level,
            request.audience_type
        )
        if "error" in result:
            logger.error(f"Gemini Caption Error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except Exception as e:
        import traceback
        logger.error(f"FATAL CAPTION ERROR: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-script")
def generate_script_endpoint(request: ScriptRequest):
    try:
        result = script_engine.generate_script(request.quote, request.philosopher, request.rage_level)
        
        # Check for error from Gemini
        if "error" in result:
            logger.error(f"Gemini Script Error: {result['error']}")
            raise HTTPException(status_code=500, detail=result["error"])
    except Exception as e:
        import traceback
        logger.error(f"FATAL SCRIPT ERROR: {str(e)}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))
    
    # Transform raw Gemini JSON into GeneratedScript format for frontend
    sections = []
    if "hook" in result:
        sections.append({"type": "hook", "content": result["hook"], "durationEstimate": 3})
    if "hindi_translation" in result:
        sections.append({"type": "authority", "content": result["hindi_translation"], "durationEstimate": 9})
    if "modern_breakdown" in result:
        sections.append({"type": "explanation", "content": result["modern_breakdown"], "durationEstimate": 10})
    if "cta" in result:
        sections.append({"type": "cta", "content": result["cta"], "durationEstimate": 8})
    
    full_text = " ".join([s["content"] for s in sections])
    total_duration = sum([s["durationEstimate"] for s in sections])
    
    return {
        "id": str(uuid.uuid4()),
        "sections": sections,
        "fullText": full_text,
        "visualPrompts": result.get("visual_prompts", []),
        "estimatedDuration": max(total_duration, 15),
        "rage_bait_title": result.get("rage_bait_title", "")
    }

@app.get("/api/voices")
def get_voices():
    """Returns the voice registry for the UI dropdown."""
    return voice_engine.get_voice_list()

@app.post("/api/generate-voice")
def generate_voice_endpoint(request: VoiceRequest):
    audio_path = voice_engine.generate_voice(
        text=request.text,
        voice_id=request.voice_id,
    )
    if not audio_path or audio_path.startswith("Error"):
        # Extract clean message if possible
        detail = audio_path if audio_path else "Voice generation failed - generic error"
        raise HTTPException(status_code=500, detail=detail)
        
    # Return relative path for frontend/video engine
    return {"audio_path": audio_path, "url": f"/assets/{os.path.basename(audio_path)}"}

class SceneAnalysisRequest(BaseModel):
    script_text: str

@app.post("/api/upload-background")
async def upload_background_endpoint(file: UploadFile = File(...)):
    """Upload a background video for Mode B."""
    upload_dir = "backend/assets/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    # Secure filename
    filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    return {
        "filename": filename,
        "url": f"/assets/uploads/{filename}",
        "background_path": os.path.abspath(file_path)
    }

@app.post("/api/upload-audio")
async def upload_audio_endpoint(file: UploadFile = File(...)):
    """Upload a custom voiceover/audio."""
    upload_dir = "backend/assets/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    
    filename = f"audio_{uuid.uuid4()}_{file.filename}"
    file_path = os.path.join(upload_dir, filename)
    
    with open(file_path, "wb") as buffer:
        content = await file.read()
        buffer.write(content)
        
    return {
        "filename": filename,
        "url": f"/assets/uploads/{filename}",
        "audio_path": os.path.abspath(file_path)
    }

@app.get("/api/uploads/videos")
def list_uploaded_videos():
    """List all previously uploaded background videos."""
    upload_dir = "backend/assets/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    videos = []
    for f in sorted(glob.glob(os.path.join(upload_dir, "*.mp4")) + glob.glob(os.path.join(upload_dir, "*.mov")) + glob.glob(os.path.join(upload_dir, "*.webm")), key=os.path.getmtime, reverse=True):
        fname = os.path.basename(f)
        # Skip files that start with "audio_" (those are audio uploads)
        if fname.startswith("audio_"):
            continue
        videos.append({
            "filename": fname,
            "url": f"/assets/uploads/{fname}",
            "background_path": os.path.abspath(f)
        })
    return videos

@app.get("/api/uploads/audio")
def list_uploaded_audio():
    """List all previously uploaded background audio/music files."""
    upload_dir = "backend/assets/uploads"
    os.makedirs(upload_dir, exist_ok=True)
    audio_files = []
    for f in sorted(glob.glob(os.path.join(upload_dir, "audio_*")), key=os.path.getmtime, reverse=True):
        fname = os.path.basename(f)
        audio_files.append({
            "filename": fname,
            "url": f"/assets/uploads/{fname}",
            "audio_path": os.path.abspath(f)
        })
    return audio_files

@app.delete("/api/uploads/videos/{filename}")
def delete_uploaded_video(filename: str):
    """Delete an uploaded background video."""
    upload_dir = "backend/assets/uploads"
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "success", "message": "Video deleted"}
    raise HTTPException(status_code=404, detail="File not found")

@app.delete("/api/uploads/audio/{filename}")
def delete_uploaded_audio(filename: str):
    """Delete an uploaded audio file."""
    upload_dir = "backend/assets/uploads"
    file_path = os.path.join(upload_dir, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return {"status": "success", "message": "Audio deleted"}
    raise HTTPException(status_code=404, detail="File not found")

@app.post("/api/analyze-scenes")
def analyze_scenes_endpoint(request: SceneAnalysisRequest):
    """Use Gemini to break script into cinematic visual scenes."""
    scenes = scene_engine.analyze_scenes(request.script_text)
    return {"scenes": scenes, "count": len(scenes)}

@app.post("/api/generate-video")
def generate_video_endpoint(request: VideoRequest, background_tasks: BackgroundTasks, session: Session = Depends(get_session)):
    print(f"\n[DEBUG] INCOMING REEL REQUEST: {request.dict()}\n")
    # Retrieve absolute path for audio if needed, or rely on service validation
    # For now, simplistic path handling
    
    output_filename = f"reel_{os.urandom(4).hex()}.mp4"
    
    # Run video generation in background to avoid blocking
    # In a real app, use Celery/Redis Queue
    # For now, we will wait or use background task if we return a job ID.
    # Since the user wants to see result, we might block or return "Processing"
    # To keep it simple for v1, we block (MoviePy is slow though).
    # Let's block for now to ensure we return the file URL.
    
    # Define directories globally for the endpoint
    backend_dir = os.path.dirname(__file__)
    root_dir = os.path.dirname(backend_dir)
    assets_dir = os.path.join(backend_dir, "assets")
    uploads_dir = os.path.join(assets_dir, "uploads")
    
    # Resolve relative audio paths (e.g. from generated voice or uploads)
    audio_path = request.audio_path
    if not os.path.isabs(audio_path):
        # Could be in backend/assets/ (generated) or backend/assets/uploads/ (uploaded)
        # We try to infer based on the prefix or just test paths
        
        # Test exact match first if it includes dir
        possible_paths = [
            os.path.abspath(audio_path),
            os.path.join(root_dir, audio_path), # Handles "backend/assets..."
            os.path.join(assets_dir, os.path.basename(audio_path)),
            os.path.join(uploads_dir, os.path.basename(audio_path))
        ]
        
        for p in possible_paths:
            if os.path.exists(p):
                audio_path = os.path.normpath(p)
                break
    
    bg_music_path = None
    if request.bg_music_path:
        if os.path.isabs(request.bg_music_path) and os.path.exists(request.bg_music_path):
            bg_music_path = request.bg_music_path
        else:
            bg_music_path = os.path.join(uploads_dir, os.path.basename(request.bg_music_path))
    
    import traceback
    try:
        # We will not pass background_path anymore
        # Generate video with absolute paths
        output_path = video_engine.generate_video(
            script_data=request.script_data,
            audio_path=audio_path,
            bg_video_paths=request.bg_video_paths,
            bg_music_path=bg_music_path,
            bg_music_volume=request.bg_music_volume,
            caption_size=request.caption_size,
            use_smart_sfx=request.use_smart_sfx,
            use_auto_b_roll=request.use_auto_b_roll,
            output_filename=output_filename
        )
    except Exception as e:
        import traceback
        print(f"\n[CRASH IN RENDER PIPELINE]: {e}")
        traceback.print_exc()
        with open("crash.log", "w") as f:
            f.write(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
    
    if output_path.startswith("Error"):
        logger.error(f"Video engine returned error: {output_path}")
        raise HTTPException(status_code=500, detail=output_path)
        
    url = f"/output/{output_filename}"
    
    # Extract script text for history
    script_text = request.script_data.get("fullText", "")
    
    # Save to history
    export_record = VideoExport(
        video_path=output_path,
        video_url=url,
        caption_text=script_text,
        status="completed"
    )
    session.add(export_record)
    session.commit()
    session.refresh(export_record)
        
    return {"video_path": output_path, "url": url, "history_id": export_record.id}

@app.get("/api/history")
def get_export_history(session: Session = Depends(get_session)):
    # Basic sorting by id descending as a proxy for created_at
    records = session.exec(select(VideoExport).order_by(VideoExport.id.desc())).all()
    return records

@app.post("/api/ingest/pdf")
async def ingest_pdf(file: UploadFile = File(...)):
    from fastapi.responses import StreamingResponse
    import json as json_module
    from .database import engine as db_engine
    
    content = await file.read()
    
    def generate_stream():
        all_quotes_data = []
        for progress, status, quotes_so_far in ingestion_engine.extract_quotes_chunked_with_progress(content):
            all_quotes_data = quotes_so_far
            if progress < 100:
                yield json_module.dumps({"progress": progress, "status": status, "count": len(quotes_so_far)}) + "\n"
        
        # Save final quotes to database
        saved_quotes = []
        with Session(db_engine) as db_session:
            for q_data in all_quotes_data:
                quote = Quote(
                    text=q_data.get("text", ""),
                    translation=q_data.get("translation", ""),
                    meaning=q_data.get("meaning", ""),
                    tags=q_data.get("tags", ""),
                    language="mix"
                )
                if isinstance(quote.tags, list):
                    quote.tags = ",".join(quote.tags)
                db_session.add(quote)
                saved_quotes.append(quote)
            db_session.commit()
            for q in saved_quotes:
                db_session.refresh(q)
            
            quotes_list = [{"id": q.id, "text": q.text, "translation": q.translation, "meaning": q.meaning, "tags": q.tags, "language": q.language} for q in saved_quotes]
        
        yield json_module.dumps({"progress": 100, "status": f"Done! Saved {len(quotes_list)} quotes.", "quotes": quotes_list}) + "\n"
    
    return StreamingResponse(generate_stream(), media_type="application/x-ndjson")

# --- Database Endpoints ---

@app.post("/api/philosophers/", response_model=Philosopher)
def create_philosopher(philosopher: Philosopher, session: Session = Depends(get_session)):
    session.add(philosopher)
    session.commit()
    session.refresh(philosopher)
    return philosopher

@app.get("/api/philosophers/", response_model=List[Philosopher])
def read_philosophers(session: Session = Depends(get_session)):
    philosophers = session.exec(select(Philosopher)).all()
    return philosophers

@app.post("/api/quotes/", response_model=Quote)
def create_quote(quote: Quote, session: Session = Depends(get_session)):
    session.add(quote)
    session.commit()
    session.refresh(quote)
    return quote

@app.get("/api/quotes/", response_model=List[Quote])
def read_quotes(session: Session = Depends(get_session)):
    quotes = session.exec(select(Quote)).all()
    return quotes

@app.post("/api/quotes/bulk", response_model=List[Quote])
def create_quotes_bulk(quotes: List[Quote], session: Session = Depends(get_session)):
    saved_quotes = []
    for q in quotes:
        session.add(q)
        saved_quotes.append(q)
    session.commit()
    for q in saved_quotes:
        session.refresh(q)
    return saved_quotes

@app.get("/api/stats")
def get_dashboard_stats(session: Session = Depends(get_session)):
    # 1. Quote Stats
    total_quotes = session.exec(select(Quote)).all()
    used_quotes = [q for q in total_quotes if q.is_used]
    
    # 2. Generation Stats
    total_videos = session.exec(select(VideoExport)).all()
    
    # 3. Library Content Stats
    uploads_dir = "backend/assets/uploads"
    total_files = 0
    total_size_mb = 0
    if os.path.exists(uploads_dir):
        for f in os.listdir(uploads_dir):
            fp = os.path.join(uploads_dir, f)
            if os.path.isfile(fp):
                total_files += 1
                total_size_mb += os.path.getsize(fp)
    
    # 4. Storage Usage
    total_size_mb = round(total_size_mb / (1024 * 1024), 2)

    # 5. API Health Check
    el_api_key = os.getenv("ELEVENLABS_API_KEY")
    api_status = "active"
    voice_engine_mode = "premium"
    credits_remaining = "Unlimited (Edge-TTS)"
    
    if el_api_key:
        try:
            el_resp = requests.get(
                "https://api.elevenlabs.io/v1/user/subscription",
                headers={"xi-api-key": el_api_key},
                timeout=5
            )
            if el_resp.status_code == 200:
                sub_data = el_resp.json()
                char_limit = sub_data.get("character_limit", 0)
                char_count = sub_data.get("character_count", 0)
                rem = char_limit - char_count
                credits_remaining = f"{rem:,} characters"
                if rem <= 0:
                    api_status = "credits_exhausted"
                    voice_engine_mode = "fallback"
            else:
                api_status = "invalid_key"
                voice_engine_mode = "fallback"
        except:
            api_status = "error"
            voice_engine_mode = "fallback"
    else:
        api_status = "not_configured"
        voice_engine_mode = "fallback"

    return {
        "quotes": {
            "total": len(total_quotes),
            "used": len(used_quotes),
            "remaining": len(total_quotes) - len(used_quotes)
        },
        "generations": {
            "total_videos": len(total_videos)
        },
        "library": {
            "media_files": total_files,
            "storage_mb": total_size_mb
        },
        "api_health": {
            "voice": {
                "status": api_status,
                "mode": voice_engine_mode,
                "credits": credits_remaining
            },
            "gemini": {
                "status": "active" if os.getenv("GEMINI_API_KEY") else "missing"
            }
        },
        "automation": {
            "next_run": "09:00 AM / 05:00 PM",
            "status": "Running"
        }
    }
