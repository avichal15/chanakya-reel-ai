"""
Scene Intelligence Engine — Gemini-powered visual scene analysis
Maps narration text to cinematic visual scenes for video generation.
"""
import google.generativeai as genai
import os
import json
import logging
from dotenv import load_dotenv
from pathlib import Path

logger = logging.getLogger(__name__)

# Load .env
env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

# ── Theme → Color mapping for gradient backgrounds ─────────────
THEME_COLORS = {
    "war":        ((40, 5, 5),   (15, 0, 0)),      # Deep crimson → black
    "stoicism":   ((15, 15, 25), (5, 5, 15)),       # Cool steel blue
    "luxury":     ((30, 20, 5),  (10, 5, 0)),       # Gold-tinted dark
    "chess":      ((20, 20, 20), (5, 5, 5)),        # Monochrome gray
    "corporate":  ((10, 15, 25), (3, 5, 12)),       # Corporate blue
    "kings":      ((25, 10, 30), (8, 3, 12)),       # Royal purple
    "isolation":  ((5, 10, 15),  (0, 3, 8)),        # Lone cold blue
    "strategy":   ((15, 20, 10), (5, 8, 3)),        # Strategic green
    "philosophy": ((15, 5, 25),  (5, 2, 12)),       # Deep philosophical purple
    "betrayal":   ((25, 5, 10),  (10, 0, 3)),       # Dark blood red
    "power":      ((20, 15, 5),  (8, 5, 0)),        # Amber power
    "default":    ((15, 5, 25),  (5, 15, 35)),      # Default dark gradient
}

SCENE_PROMPT = """You are a cinematic director for viral philosophy reels.

Analyze this narration script and break it into visual scenes suitable for a 9:16 vertical reel.

For EACH scene, return:
- "text": the exact narration text for this scene
- "scene_description": a vivid 1-line description of the visual
- "theme": one of: war, stoicism, luxury, chess, corporate, kings, isolation, strategy, philosophy, betrayal, power
- "emotion": one of: intense, calm, dark, triumphant, reflective, urgent
- "keywords": list of 3-5 visual keywords

IMPORTANT: Every line of the narration must appear in exactly one scene. Do not skip any text.

Return ONLY valid JSON array. Example:
[
  {"text": "Your friends only like you when...", "scene_description": "A lone figure stands on a cliff overlooking a stormy sea", "theme": "isolation", "emotion": "dark", "keywords": ["cliff", "storm", "alone", "ocean"]},
  {"text": "Chanakya said truth is bitter", "scene_description": "Ancient Indian throne room with flickering torches", "theme": "kings", "emotion": "intense", "keywords": ["throne", "torches", "ancient", "wisdom"]}
]"""


def analyze_scenes(script_text: str) -> list[dict]:
    """
    Use Gemini to break narration into cinematic visual scenes.

    Returns list of scene dicts with theme, keywords, emotion, etc.
    Falls back to simple sentence splitting if Gemini fails.
    """
    if not api_key:
        logger.warning("No Gemini API key — using fallback scene analysis")
        return _fallback_scenes(script_text)

    try:
        model = genai.GenerativeModel('gemma-4-31b-it')
        response = model.generate_content(
            f"{SCENE_PROMPT}\n\nNarration:\n{script_text}",
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.7,
            )
        )

        raw = response.text.strip()
        # Parse JSON
        start = raw.find('[')
        end = raw.rfind(']')
        if start != -1 and end != -1:
            clean_text = raw[start:end+1]
        else:
            clean_text = raw
            
        scenes = json.loads(clean_text)

        if not isinstance(scenes, list) or len(scenes) == 0:
            logger.warning("Gemini returned empty scenes, using fallback")
            return _fallback_scenes(script_text)

        # Validate and fill defaults
        for scene in scenes:
            scene.setdefault("theme", "default")
            scene.setdefault("emotion", "dark")
            scene.setdefault("keywords", [])
            scene.setdefault("scene_description", "")
            # Normalize theme
            if scene["theme"] not in THEME_COLORS:
                scene["theme"] = "default"

        logger.info(f"Gemini scene analysis: {len(scenes)} scenes generated")
        return scenes

    except Exception as e:
        logger.error(f"Gemini scene analysis failed: {e}")
        return _fallback_scenes(script_text)


def _fallback_scenes(script_text: str) -> list[dict]:
    """Simple fallback: split text into sentences and assign rotating themes."""
    import re
    sentences = re.split(r'[.!?…]+', script_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    themes = list(THEME_COLORS.keys())
    scenes = []
    for i, sentence in enumerate(sentences):
        theme = themes[i % len(themes)]
        scenes.append({
            "text": sentence,
            "scene_description": f"Scene {i+1}",
            "theme": theme,
            "emotion": "dark",
            "keywords": [],
        })

    return scenes


def get_theme_colors(theme: str) -> tuple:
    """Get gradient colors for a visual theme."""
    return THEME_COLORS.get(theme, THEME_COLORS["default"])
