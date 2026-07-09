import google.generativeai as genai
import os
import json
from typing import List, Dict
from dotenv import load_dotenv

from pathlib import Path

# Load .env from backend directory
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

SYSTEM_PROMPT = """
You are a Viral Growth Engineer and Social Media Algorithm Specialist.
Your task is to build an AI module that automatically generates viral Instagram captions and high-performing hashtag sets for short-form philosophy reels.

Tone: Bold, Direct, Provocative, Reliability-check style, Hinglish mix.

CAPTION STRUCTURE FRAMEWORK (5 Blocks):
1. SCROLL-STOP HOOK (Block 1): Max 10 words. Triggers ego or discomfort. (e.g. "Sach kadwa hota hai...")
2. QUOTE AUTHORITY (Block 2): Credit philosopher. (e.g. "Chanakya ne isliye warn kiya tha...")
3. MODERN RELATABILITY (Block 3): Explain relevance in today's world (Corporate, Fake Friends, etc). Hinglish.
4. IDENTITY TRIGGER (Block 4): Make viewer self-reflect. (e.g. "Agar tum alag sochte ho... you're rare.")
5. SHARE/TAG CTA (Block 5): Viral loop commands. NO "Like" requests. (e.g. "Tag that fake friend.")

HASHTAG RULES:
- Tier 1: Broad Reach (5 tags)
- Tier 2: Niche Targeting (10 tags)
- Tier 3: Viral Bait (10 tags)
- Include philosopher-specific tags.

OUTPUT FORMAT (JSON):
{
  "caption_text": "Full caption with line breaks...",
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
    
    model = genai.GenerativeModel('gemma-4-31b-it')
    
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
        response = model.generate_content(
            contents=[SYSTEM_PROMPT, user_prompt],
            generation_config={"response_mime_type": "application/json"}
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
