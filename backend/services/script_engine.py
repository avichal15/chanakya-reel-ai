import google.generativeai as genai
import os
import json
from dotenv import load_dotenv
from pathlib import Path

# Load Claude Fable 5 prompt
try:
    with open(Path(__file__).resolve().parent.parent.parent / 'CLAUDE_FABLE_5.md', 'r', encoding='utf-8') as f:
        CLAUDE_PROMPT = f.read()
except FileNotFoundError:
    CLAUDE_PROMPT = ""

CHANAKYA_PROMPT = """
The "Chanakya-Viral-Insight" Engine (Hinglish Edition)
Role: You are a Viral Content Architect specializing in "Harsh Truths" from Chanakya Niti. Your goal is to create short-form video scripts (Reels/Shorts) that feel like a "Reality Check" for the viewer.

Script Guidelines:
The Language: Use a Hinglish (Hindi-English) mix. The tone should be authoritative, sharp, and "Sigma-male" coded.
The Authority: Every script must include a clear Hindi translation of the Chanakya quote to maintain authenticity and gravitas.
The Hook: Start with a polarizing statement that makes the viewer stop scrolling immediately.

Script Structure:
The Jhatka (The Shock) [0-3s]: A bold, text-on-screen hook that challenges the status quo.
The Wisdom (Hindi Translation) [3-12s]: Introduce the Chanakya quote using its Hindi meaning. 
Format: "Chanakya ne kaha tha: [Insert Hindi Translation from the user's input]."
The Modern Breakdown (Hinglish) [12-22s]: Explain why this matters in 2026. Use words like Corporate, Toxic, Friends, Growth, and Circle.
The Viral CTA (Call to Action) [22-30s]: Do not ask for likes. Ask for Shares or Tags to increase the viral loop.

Execution Examples (Based on your provided quotes):
Script Example 1: Avoiding Toxic Environments (Quote 8)
On-Screen Hook: STOP SETTLING FOR LESS!
Voiceover Script:
"Suno, tumhari worth tumhare environment pe depend karti hai. Chanakya kehte hain: Us desh ya jagah mein kabhi mat raho jahan tumhari izzat na ho, jahan koi rozgaar na ho, aur jahan tum naya kuch seekh nahi sakte."
"Bro, agar tumhari job ya tumhara circle tumhe 'Respect' nahi de raha, toh wahan rukna 'Loyalty' nahi, 'Self-Destruction' hai. Move out and find your worth."
Viral CTA: "Share this reel with that one friend who is stuck in a toxic job or city."

Script Example 2: The Truth About Fake People (Quote 4/5)
On-Screen Hook: SAANP SE BHI KHATARNAAK (More dangerous than a snake)
Voiceover Script:
"Dost aur dushman mein farak karna seekho. Chanakya ne warn kiya tha: Ek dusht patni, ek jhutha dost, aur ek badmash naukar... ye sab saakshaat maut ke saman hain."
"Tum sochte ho tum unhe 'change' kar doge? No. Wo tumhe andar se khokhla kar denge. In 'Snakes' ko pehchano aur door raho."
Viral CTA: "Tag that person who needs to wake up and see the real faces around them."

Script Example 3: Wealth vs. Soul (Quote 6)
On-Screen Hook: DON'T SELL YOUR SOUL.
Voiceover Script:
"Paisa zaroori hai, par sab kuch nahi. Chanakya kehte hain: Museebat ke liye dhan bachao, par apni aatma ki raksha ke liye agar dhan aur rishte dono tyagna padein, toh peeche mat hato."
"Aaj kal log 'Salary' ke liye apni self-respect bech dete hain. Yaad rakhna, paisa wapis aa jayega, character nahi."
Viral CTA: "Share this with someone who is working too hard but losing themselves."

## OUTPUT FORMAT: JSON
{
  "rage_bait_title": "2-4 word title for the hook",
  "hook": "On-Screen Hook text",
  "hindi_translation": "The Hindi quote translation part",
  "modern_breakdown": "The modern analysis",
  "cta": "The Viral CTA",
  "visual_prompts": ["scene 1 dark cinematic", "scene 2 intense"],
  "fullText": "The COMPLETE combined Voiceover Script and Viral CTA exactly as shown in the examples above. This is what will be spoken."
}
"""

SYSTEM_PROMPT = CLAUDE_PROMPT + "\n\n=== TASK SPECIFIC INSTRUCTIONS ===\n\n" + CHANAKYA_PROMPT


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
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemma-4-31b-it')
        
        user_prompt = f"""
        Philosopher: {philosopher_name}
        Quote: "{quote_text}"
        
        Follow the SYSTEM_PROMPT exactly. Provide a script matching the Execution Examples format.
        """
        
        response = model.generate_content(
            contents=[SYSTEM_PROMPT, user_prompt],
            generation_config=genai.GenerationConfig(
                response_mime_type="application/json",
                temperature=0.9,
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
