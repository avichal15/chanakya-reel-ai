import sys
import os
from pathlib import Path

# Add backend directory to sys.path so we can import modules
sys.path.append(str(Path(__file__).resolve().parent))

from backend.services.script_engine import generate_script

def test():
    print("Testing generate_script with Fable embedded...")
    
    quote = "A man is born alone and dies alone; and he experiences the good and bad consequences of his karma alone; and he goes alone to hell or the Supreme abode."
    
    result = generate_script(
        quote_text=quote,
        philosopher_name="Chanakya",
        rage_level=5
    )
    
    print("\nRESULT:")
    import json
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    test()
