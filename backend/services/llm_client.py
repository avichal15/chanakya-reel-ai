import os
import json
import logging
import requests
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

logger = logging.getLogger("LLMClient")

# Load environment variables
env_path = Path(__file__).resolve().parent.parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

OLLAMA_API_KEY = os.getenv("OLLAMA_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OLLAMA_NATIVE_URL = "https://ollama.com/api/chat"

def generate_json(system_prompt: str, user_prompt: str, ollama_model: str = "gemma4:31b-cloud", gemini_model: str = "gemini-2.5-flash") -> dict:
    """
    Unified LLM generation function that attempts to use Ollama Cloud API first.
    If Ollama fails or is unconfigured, it gracefully falls back to Google Gemini.
    """
    if OLLAMA_API_KEY:
        try:
            logger.info(f"[LLM_CLIENT] Attempting generation with Ollama ({ollama_model})...")
            headers = {
                "Authorization": f"Bearer {OLLAMA_API_KEY}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": ollama_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "format": "json",
                "stream": False
            }
            
            response = requests.post(OLLAMA_NATIVE_URL, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            res_json = response.json()
            raw_text = res_json.get("message", {}).get("content", "")
            
            return _clean_and_parse_json(raw_text)
            
        except Exception as e:
            logger.error(f"[LLM_CLIENT] Ollama failed: {e}. Falling back to Gemini...")
    else:
        logger.info("[LLM_CLIENT] OLLAMA_API_KEY not found. Defaulting to Gemini...")

    # Fallback to Gemini
    if not GEMINI_API_KEY:
        return {"error": "Neither OLLAMA_API_KEY nor GEMINI_API_KEY are configured."}
        
    try:
        logger.info(f"[LLM_CLIENT] Generating with Gemini ({gemini_model})...")
        client = genai.Client(api_key=GEMINI_API_KEY)
        
        response = client.models.generate_content(
            model=gemini_model,
            contents=[system_prompt, user_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.7
            )
        )
        return _clean_and_parse_json(response.text)
        
    except Exception as e:
        logger.error(f"[LLM_CLIENT] Gemini fallback failed: {e}")
        return {"error": f"LLM Generation failed entirely. Last error: {e}"}

def _clean_and_parse_json(raw_text: str) -> dict:
    """Safely extracts and parses JSON from markdown blocks if necessary."""
    try:
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        
        # If no object braces found, check for array
        if start == -1 or end == -1:
            start = raw_text.find('[')
            end = raw_text.rfind(']')
            
        if start != -1 and end != -1:
            clean_text = raw_text[start:end+1]
        else:
            clean_text = raw_text
            
        data = json.loads(clean_text)
        return data
    except json.JSONDecodeError:
        logger.error(f"Failed to parse JSON. Raw output: {raw_text}")
        return {"error": "Invalid JSON response from LLM", "raw": raw_text}
