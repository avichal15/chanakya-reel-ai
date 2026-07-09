"""
Voice Generation Engine
Priority: ElevenLabs (Premium) → Mimo-v2-TTS (High Quality Free) → Edge-TTS (Last Resort)
"""
import requests
import os
import uuid
import logging
import asyncio
import json
import edge_tts
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logger = logging.getLogger(__name__)

# Load .env from backend directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"

MIMO_API_KEY = os.getenv("MIMO_API_KEY")
MIMO_BASE_URL = "https://api.xiaomimimo.com/v1/audio/speech"

# ── Voice Registry (ElevenLabs) ─────────────────────────────────
VOICE_LIBRARY = {
    "Discovery Narrator": "eVItLK1UvXctxuaRV2Oq",
    "Deep Stoic Voice": "wyWA56cQNU2KqUW4eCsI",
    "Calm Philosophy": "piTKgcLEGmPE4e6mJCoi",
    "Dark Cinematic": "pFZP5JQG7iQjIQuC4Bku",
}

# ── Mimo Voice Mapping ──────────────────────────────────────────
# Maps ElevenLabs Voice IDs to Mimo-v2-TTS voice names
MIMO_VOICE_MAPPING = {
    "eVItLK1UvXctxuaRV2Oq": "alloy",      # Discovery Narrator → warm narrator
    "wyWA56cQNU2KqUW4eCsI": "onyx",       # Deep Stoic Voice → deep male
    "piTKgcLEGmPE4e6mJCoi": "shimmer",    # Calm Philosophy → dark sensual female
    "pFZP5JQG7iQjIQuC4Bku": "nova",       # Dark Cinematic → warm engaging female
}

# ── Edge TTS Fallback Mapping (Last Resort) ─────────────────────
EDGE_FALLBACK_MAPPING = {
    "eVItLK1UvXctxuaRV2Oq": "hi-IN-MadhurNeural",
    "wyWA56cQNU2KqUW4eCsI": "en-US-ChristopherNeural",
    "piTKgcLEGmPE4e6mJCoi": "en-US-JennyNeural",
    "pFZP5JQG7iQjIQuC4Bku": "en-US-AriaNeural",
}
DEFAULT_VOICE_ID = "pFZP5JQG7iQjIQuC4Bku"
MODEL_ID = "eleven_v3"

# ── Output Directory ────────────────────────────────────────────
AUDIO_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
os.makedirs(AUDIO_DIR, exist_ok=True)

# ════════════════════════════════════════════════════════════════
# TIMESTAMPS HELPER
# ════════════════════════════════════════════════════════════════
def save_timestamps(filepath: str, words: list) -> str:
    """Save standard word-level timestamps to a JSON file alongside the audio."""
    json_path = filepath.replace(".mp3", ".json").replace(".wav", ".json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(words, f, indent=2)
    return json_path

# ════════════════════════════════════════════════════════════════
# ENGINE 1: ElevenLabs (Premium)
# ════════════════════════════════════════════════════════════════
def _try_elevenlabs(text: str, voice_id: str, filepath: str) -> bool:
    """Attempt ElevenLabs generation with key fallback. Returns True on success."""
    keys_str = os.getenv("ELEVENLABS_API_KEYS", "")
    if not keys_str.strip():
        logger.warning("[SKIP] ElevenLabs API keys not configured.")
        return False
        
    api_keys = [k.strip() for k in keys_str.split(',') if k.strip()]
    if not api_keys:
        return False

    url = f"{ELEVENLABS_BASE_URL}/{voice_id}/with-timestamps"
    payload = {
        "text": text,
        "model_id": MODEL_ID,
        "voice_settings": {
            "stability": 0.8,
            "similarity_boost": 0.75,
            "use_speaker_boost": True
        }
    }

    for idx, key in enumerate(api_keys):
        headers = {
            "xi-api-key": key,
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"[Engine 1] Attempting ElevenLabs (with-timestamps): {voice_id} (Key {idx+1}/{len(api_keys)})")
            response = requests.post(url, json=payload, headers=headers, timeout=60)

            if response.status_code == 200:
                data = response.json()
                import base64
                audio_bytes = base64.b64decode(data["audio_base64"])
                with open(filepath, "wb") as f:
                    f.write(audio_bytes)
                
                # Process timestamps
                alignment = data.get("alignment")
                if alignment and "characters" in alignment:
                    chars = alignment["characters"]
                    starts = alignment["character_start_times_seconds"]
                    ends = alignment["character_end_times_seconds"]
                    
                    words = []
                    current_word = ""
                    current_start = -1
                    
                    for i, char in enumerate(chars):
                        if not char.strip():
                            if current_word:
                                w_start = current_start if current_start is not None else 0.0
                                w_end = ends[i-1] if ends[i-1] is not None else w_start + 0.1
                                words.append({
                                    "word": current_word,
                                    "start": round(w_start, 3),
                                    "end": round(w_end, 3)
                                })
                                current_word = ""
                                current_start = -1
                        else:
                            if current_word == "":
                                current_start = starts[i]
                            current_word += char
                            
                    if current_word:
                        w_start = current_start if current_start is not None else 0.0
                        w_end = ends[-1] if ends[-1] is not None else w_start + 0.1
                        words.append({
                            "word": current_word,
                            "start": round(w_start, 3),
                            "end": round(w_end, 3)
                        })
                        
                    save_timestamps(filepath, words)

                logger.info(f"[OK] ElevenLabs Generation Success with key {idx+1}.")
                return True

            if response.status_code == 401:
                 logger.warning(f"[SKIP] ElevenLabs key {idx+1} unauthorized/exhausted. Trying next key.")
                 continue # Try next key
            elif response.status_code == 429:
                logger.warning(f"[SKIP] ElevenLabs key {idx+1} rate limited. Trying next key.")
                continue # Try next key
            else:
                 logger.error(f"ElevenLabs Error {response.status_code}: {response.text}")
                 # For other errors, we might not want to retry with another key immediately, but for robustness we will 
                 # continue to the next key just in case it's a fluke with that specific account/key's setting.
                 continue 
                 
        except Exception as e:
            logger.warning(f"[SKIP] ElevenLabs connection error with key {idx+1}: {e}. Trying next key.")
            continue # Try next key

    logger.warning("[SKIP] All ElevenLabs API keys exhausted or failed. Trying next engine.")
    return False

# ════════════════════════════════════════════════════════════════
# ENGINE 2: Mimo-v2-TTS (High Quality)
# ════════════════════════════════════════════════════════════════
def _try_mimo_tts(text: str, voice_id: str, filepath: str) -> bool:
    """Attempt Mimo-v2-TTS generation. Returns True on success."""
    if not MIMO_API_KEY or not MIMO_API_KEY.strip():
        logger.info("[SKIP] Mimo API key not configured.")
        return False

    mimo_voice = MIMO_VOICE_MAPPING.get(voice_id, "alloy")
    headers = {
        "Authorization": f"Bearer {MIMO_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mimo-v2-tts",
        "input": text,
        "voice": mimo_voice,
        "response_format": "mp3",
        "speed": 1.0
    }

    try:
        logger.info(f"[Engine 2] Attempting Mimo-v2-TTS: voice={mimo_voice}")
        response = requests.post(MIMO_BASE_URL, json=payload, headers=headers, timeout=90)

        if response.status_code == 200:
            content_type = response.headers.get("content-type", "")
            # Verify we got audio back, not a JSON error
            if "audio" in content_type or "octet-stream" in content_type or len(response.content) > 1000:
                with open(filepath, "wb") as f:
                    f.write(response.content)
                logger.info(f"[OK] Mimo-v2-TTS Success ({len(response.content)} bytes)")
                return True
            else:
                logger.warning(f"[SKIP] Mimo returned non-audio response: {response.text[:200]}")
                return False

        logger.warning(f"[SKIP] Mimo-v2-TTS failed ({response.status_code}): {response.text[:200]}")
        return False
    except Exception as e:
        logger.warning(f"[SKIP] Mimo-v2-TTS connection error: {e}. Trying next engine.")
        return False

# ════════════════════════════════════════════════════════════════
# ENGINE 3: Edge-TTS (Last Resort, Free)
# ════════════════════════════════════════════════════════════════
async def _generate_edge_voice(text: str, voice_name: str, filepath: str):
    """Helper to run edge-tts asynchronously and capture native word boundaries."""
    communicate = edge_tts.Communicate(text, voice_name)
    audio_data = b""
    words = []
    
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
        elif chunk["type"] == "WordBoundary":
            # offset and duration are in 100-nanosecond units
            start_sec = chunk["offset"] / 10_000_000.0
            end_sec = (chunk["offset"] + chunk["duration"]) / 10_000_000.0
            words.append({
                "word": chunk["text"],
                "start": round(start_sec, 3),
                "end": round(end_sec, 3)
            })
            
    with open(filepath, "wb") as f:
        f.write(audio_data)
        
    if words:
        save_timestamps(filepath, words)

def _try_edge_tts(text: str, voice_id: str, filepath: str) -> bool:
    """Attempt Edge-TTS generation. Returns True on success."""
    edge_voice = EDGE_FALLBACK_MAPPING.get(voice_id, "hi-IN-MadhurNeural")
    try:
        logger.info(f"[Engine 3] Attempting Edge-TTS: {edge_voice}")
        asyncio.run(_generate_edge_voice(text, edge_voice, filepath))
        logger.info("[OK] Edge-TTS Success.")
        return True
    except Exception as e:
        logger.error(f"[FAIL] Edge-TTS failed: {e}")
        return False

# ════════════════════════════════════════════════════════════════
# PUBLIC API
# ════════════════════════════════════════════════════════════════
def get_voice_list() -> list[dict]:
    """Returns the voice registry for the frontend."""
    return [{"id": vid, "name": name} for name, vid in VOICE_LIBRARY.items()]

def generate_voice(text: str, voice_id: str = DEFAULT_VOICE_ID, quote_id: str | None = None) -> str:
    """
    Generates audio with cascading fallback:
    1. ElevenLabs (Premium custom voices)
    2. Mimo-v2-TTS (High quality, natural sounding)
    3. Edge-TTS (Free, always available)
    """
    if not text or not text.strip():
        return "Error: Empty text."

    # Prepare output path
    voice_name_in_lib = next((k for k, v in VOICE_LIBRARY.items() if v == voice_id), "custom")
    safe_name = voice_name_in_lib.lower().replace(" ", "_")
    filename = f"voice_{uuid.uuid4().hex[:8]}_{safe_name}.mp3"
    filepath = os.path.join(AUDIO_DIR, filename)

    # Cascade: ElevenLabs → Mimo → Edge-TTS
    success_path = None
    if _try_elevenlabs(text, voice_id, filepath):
        success_path = filepath
    elif _try_mimo_tts(text, voice_id, filepath):
        success_path = filepath
    elif _try_edge_tts(text, voice_id, filepath):
        success_path = filepath

    if success_path:
        # Convert MP3 to 44.1kHz WAV to prevent Encoder Padding and Sample Rate Drift
        import subprocess
        wav_path = success_path.replace(".mp3", ".wav")
        try:
            logger.info(f"Converting TTS audio to standard 44.1kHz WAV: {wav_path}")
            subprocess.run([
                "ffmpeg", "-y", "-i", success_path, 
                "-ar", "44100", "-ac", "2", "-c:a", "pcm_s16le", wav_path
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if os.path.exists(wav_path):
                os.remove(success_path)
                return wav_path
        except Exception as e:
            logger.error(f"Failed to convert TTS to WAV: {e}")
            return success_path

    return "Error: All voice engines failed."
