from google import genai
from google.genai import types
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

from pathlib import Path

# Load .env from backend directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

SYSTEM_PROMPT = """
You are a Viral Growth Engineer and Social Media Algorithm Specialist.
Your task is to build an AI module that automatically generates viral Instagram/YouTube captions and high-performing hashtag sets for short-form philosophy reels.

Tone: Profound, Cinematic, Deeply Reflective, and highly Aesthetic.

CAPTION STRUCTURE FRAMEWORK (3 Blocks):
1. THE TRENDING HOOK (Block 1): A deeply relatable, aesthetic "Curiosity Gap" hook that forces the user to watch the video for the answer. (e.g. "If you always feel burnt out, this is why... 🕰️" or "Most people get motivation completely wrong...").
2. THE ANCIENT WISDOM (Block 2): The essence of the quote translated to a modern realization. Use minimal, clean formatting.
3. THE ENGAGEMENT CTA (Block 3): Ask a thought-provoking question to drive comments (algorithm trigger), or tell them to "Save this as a daily reminder 📌".

HASHTAG RULES (MUST USE CURRENT TRENDING ALGORITHM META):
- Tier 1: Mega-Trending Philosophy (5 tags: e.g., #mindset #stoicism #deepquotes #lifequotes #wisdom)
- Tier 2: Aesthetic / Niche (10 tags: e.g., #cinematicreels #darkaesthetic #ancientwisdom #philosophyquotes #mindsetshift)
- Tier 3: Viral Algorithm Triggers (10 tags: e.g., #shorts #viral #fyp #explorepage #trending)
- ALWAYS include philosopher-specific tags. Ensure tags are highly relevant to the "dark academia" or "stoic" trending aesthetics.

OUTPUT FORMAT (JSON):
{
  "caption_text": "Full caption with line breaks and minimal emojis...",
  "hook_line": "...",
  "cta_line": "...",
  "hashtags_tier1": ["#tag1", ...],
  "hashtags_tier2": ["#tag1", ...],
  "hashtags_tier3": ["#tag1", ...],
  "combined_hashtags": "#tag1 #tag2 ..."
}
"""

def generate_caption(
    philosopher_name: str,
    quote_text: str,
    script_text: str,
    theme: str = "Harsh Truths",
    rage_level: int = 5,
    audience_type: str = "General"
) -> dict:
    if not api_key:
        return {"error": "Gemini API key not configured"}
    
    client = genai.Client(api_key=api_key)
    
    user_prompt = f"""
    Philosopher: {philosopher_name}
    Quote: "{quote_text}"
    Script context: "{script_text}"
    Theme: {theme}
    Rage Level: {rage_level}
    Audience: {audience_type}
    
    Generate a viral caption and hashtag set following the system rules.
    """
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[SYSTEM_PROMPT, user_prompt],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        raw_text = response.text
        start = raw_text.find('{')
        end = raw_text.rfind('}')
        if start != -1 and end != -1:
            clean_text = raw_text[start:end+1]
        else:
            clean_text = raw_text
            
        return json.loads(clean_text)
    except Exception as e:
        print(f"Error generating caption: {e}")
        return {"error": str(e)}
