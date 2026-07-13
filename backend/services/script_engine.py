from google import genai
from google.genai import types
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load Mythos System prompt
try:
    with open(Path(__file__).resolve().parent.parent.parent / 'MYTHOS-5.md', 'r', encoding='utf-8') as f:
        MYTHOS_PROMPT = f.read()
except FileNotFoundError:
    MYTHOS_PROMPT = ""

CHANAKYA_PROMPT = """
The "Cinematic Philosophy Insight" Engine (Hinglish Edition)
Role: You are a Master Storyteller and Viral Growth Specialist. Your goal is to create profound, thought-provoking short-form video scripts (Reels/Shorts) based on ancient wisdom that strictly adhere to 2026 algorithmic trends.

Script Guidelines:
The Language: Use a natural, poetic Hinglish (Hindi-English) mix. The tone should be cinematic, calm yet authoritative, and deeply reflective. Speak to the viewer's intellect and modern struggles.
The Authority: Every script must include a clear Hindi translation of the quote to maintain authenticity and gravitas.
The Hook: Must use a "Curiosity Gap" (Contrarian or Pain-Point). Challenge a common belief or highlight a deep modern frustration to stop the scroll immediately in the first 3 seconds.

Script Structure:
The Realization (The Hook) [0-3s]: A bold, text-on-screen statement that acts as a pattern interrupt. (e.g. "Why you are always tired, even when you sleep...")
The Ancient Wisdom (Hindi Translation) [3-12s]: Introduce the quote using its Hindi meaning. 
Format: "[Philosopher Name] ne sadiyon pehle ek baat kahi thi: [Insert Hindi Translation]."
The Modern Application (Hinglish) [12-22s]: Explain EXACTLY how to apply this ancient wisdom to solve a modern problem (e.g., workplace stress, social media anxiety, toxic relationships). Focus on practical mindset shifts.
The Viral CTA (Call to Action) [22-30s]: Ask a deep, polarizing question for the comments to drive algorithm engagement, or suggest they save the video.

Execution Examples:
Script Example 1: The Illusion of Control (Pain-Point Hook)
On-Screen Hook: WHY YOUR ANXIETY NEVER LEAVES YOU.
Voiceover Script:
"Tum har cheez ko control karna chahte ho, aur yahi tumhari sabse badi haar hai. Chanakya ne sadiyon pehle ek baat kahi thi: Jo guzar gaya uspe shok mat karo, jo aane wala hai uski chinta mat karo, bas vartaman mein jiyo."
"Aaj ki is bhaag-daud mein, hum future ke bare mein overthink karke apni aaj ki shanti kho dete hain. The only way out is acceptance. Jo tumhare control mein nahi hai, use let go karna seekho."
Viral CTA: "What is one thing you need to let go of today? Tell me in the comments."

Script Example 2: The Reality of Focus (Contrarian Hook)
On-Screen Hook: MOTIVATION IS A COMPLETE LIE.
Voiceover Script:
"Tum motivation dhoondh rahe ho, par tumhe discipline ki zaroorat hai. Chanakya ne warn kiya tha: Koi bhi kaam shuru karne se pehle khud se teen sawal pucho- main ye kyun kar raha hoon, iska anjaam kya hoga, aur kya main safal hounga?"
"Jab tum bina direction ke mehnat karte ho, toh wo sirf thakan banti hai. Stop relying on random bursts of energy. Apna 'why' clear karo, aur ek routine build karo. That's how you win."
Viral CTA: "Save this video for when you feel like giving up."

## OUTPUT FORMAT: JSON
{
  "rage_bait_title": "2-4 word profound title for the thumbnail",
  "hook": "On-Screen Hook text",
  "hindi_translation": "The Hindi quote translation part",
  "modern_breakdown": "The modern analysis",
  "cta": "The Viral CTA",
  "visual_prompts": ["dark cinematic rainy city", "solitary chess piece cinematic macro", "ancient temple mysterious lighting"],
  "fullText": "The COMPLETE combined Voiceover Script and Viral CTA exactly as shown in the examples above. This is what will be spoken."
}
"""

SYSTEM_PROMPT = MYTHOS_PROMPT + "\n\n" + CHANAKYA_PROMPT


def _get_api_key():
    """Load the API key fresh every time to avoid stale cached values."""
    env_path = Path(__file__).resolve().parent.parent / '.env'
    if not env_path.exists():
        env_path = Path(__file__).resolve().parent.parent.parent / '.env'
    load_dotenv(dotenv_path=env_path, override=True)
    return os.getenv("GEMINI_API_KEY")

def generate_script(quote_text: str, philosopher_name: str = "Chanakya", rage_level: int = 5) -> dict:
    api_key = _get_api_key()
    if not api_key:
        return {"error": "Gemini API key not configured"}
    
    try:
        client = genai.Client(api_key=api_key)
        
        user_prompt = f"""
        Philosopher: {philosopher_name}
        Quote: "{quote_text}"
        
        Follow the SYSTEM_PROMPT exactly. Provide a script matching the Execution Examples format.
        """
        
        response = client.models.generate_content(
            model='gemma-4-31b-it',
            contents=[SYSTEM_PROMPT, user_prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=1.0,
                safety_settings=[
                    types.SafetySetting(category="HARM_CATEGORY_HARASSMENT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_HATE_SPEECH", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold="BLOCK_NONE"),
                    types.SafetySetting(category="HARM_CATEGORY_DANGEROUS_CONTENT", threshold="BLOCK_NONE")
                ]
            )
        )
        
        try:
            raw_text = response.text
            start = raw_text.find('{')
            end = raw_text.rfind('}')
            if start != -1 and end != -1:
                clean_text = raw_text[start:end+1]
            else:
                clean_text = raw_text
                
            result = json.loads(clean_text)
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
        except json.JSONDecodeError:
            return {"error": "Invalid JSON response from Gemini", "raw": response.text}
            
        # Build fullText if missing
        if "fullText" not in result or not result["fullText"]:
            parts = []
            if result.get("hook"): parts.append(result["hook"])
            if result.get("hindi_translation"): parts.append("... " + result["hindi_translation"])
            if result.get("modern_breakdown"): parts.append("... " + result["modern_breakdown"])
            if result.get("cta"): parts.append("... " + result["cta"])
            result["fullText"] = "\n\n".join(parts)
        
        # Basic validation
        required = ["rage_bait_title", "hook", "hindi_translation", "modern_breakdown", "cta"]
        missing = [k for k in required if k not in result]
        if missing:
            return {"error": f"Invalid script format. Missing fields: {missing}", "partial_result": result}
            
        return result

    except Exception as e:
        return {"error": f"Gemini API Error: {str(e)}"}
