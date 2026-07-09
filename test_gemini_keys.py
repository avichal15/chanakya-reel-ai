"""Test Gemini API keys against the script engine workflow."""
import google.generativeai as genai
import json
import sys

# Force UTF-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

KEYS = [
    ("Key-1 (AQ...PQ)", "AQ.Ab8RN6LDyVn8zrzSpmwpGGIWn_zIfXy95QGeePKWp7XLh5QdPQ"),
    ("Key-2 (AQ...dw)", "AQ.Ab8RN6I66cRdNUCI01Yke_yotGE_v9_Z6DM3EX2EuXeCwCNsdw"),
    ("Key-3 (AIza...cc)", "AIzaSyB4q0W17OB2QbceYSCpEvhlZ58aW5k-4cc"),
]

# Models to try for each key
MODELS = [
    "gemini-3.1-pro-preview",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]

TEST_PROMPT = "Say 'Hello' in one word. Nothing else."

def test_key(name, key):
    print(f"\n{'='*60}")
    print(f"  Testing: {name}")
    print(f"  Key:     {key[:12]}...{key[-4:]}")
    print(f"{'='*60}")
    
    try:
        genai.configure(api_key=key)
    except Exception as e:
        print(f"  [FAIL] Could not configure: {e}")
        return
    
    for model_name in MODELS:
        try:
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(
                TEST_PROMPT,
                generation_config=genai.GenerationConfig(
                    max_output_tokens=10,
                    temperature=0.1,
                )
            )
            text = response.text.strip()
            print(f"  [OK]   {model_name:30s} -> \"{text}\"")
        except Exception as e:
            err_str = str(e)
            # Shorten long error messages
            if len(err_str) > 150:
                err_str = err_str[:150] + "..."
            print(f"  [FAIL] {model_name:30s} -> {err_str}")

def main():
    print("=" * 60)
    print("  Gemini API Key Tester for Chanakya Reel AI")
    print("=" * 60)
    
    for name, key in KEYS:
        test_key(name, key)
    
    print(f"\n{'='*60}")
    print("  Test complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
