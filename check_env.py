"""Check env setup"""
from dotenv import load_dotenv
from pathlib import Path
import os

# Check all possible .env locations
locations = [
    Path('.env'),
    Path('.env.local'),
    Path('backend/.env'),
    Path('backend/.env.local'),
]

for p in locations:
    print(f"{p}: exists={p.exists()}")
    if p.exists():
        with open(p, 'r') as f:
            content = f.read()
            # Mask API keys for security
            for line in content.strip().split('\n'):
                if '=' in line:
                    key, val = line.split('=', 1)
                    if len(val) > 8:
                        masked = val[:4] + '...' + val[-4:]
                    else:
                        masked = val
                    print(f"  {key}={masked}")

# Check what script_engine.py actually loads
print("\n--- script_engine.py env path resolution ---")
script_path = Path('backend/services/script_engine.py').resolve()
parent = script_path.parent.parent.parent
env1 = parent / '.env'
print(f"Primary .env: {env1} (exists={env1.exists()})")
env2 = script_path.parent.parent / '.env'
print(f"Fallback .env: {env2} (exists={env2.exists()})")

# Check what voice_engine.py loads
print("\n--- voice_engine.py env path resolution ---")
voice_path = Path('backend/services/voice_engine.py').resolve()
env3 = voice_path.parent.parent / '.env'
print(f"voice_engine .env: {env3} (exists={env3.exists()})")

# Check actual env vars
print(f"\nELEVENLABS_API_KEY from env: {os.getenv('ELEVENLABS_API_KEY', 'NOT SET')}")
print(f"GEMINI_API_KEY from env: {os.getenv('GEMINI_API_KEY', 'NOT SET')[:20] if os.getenv('GEMINI_API_KEY') else 'NOT SET'}...")

# Try loading from all locations
for p in locations:
    if p.exists():
        load_dotenv(dotenv_path=p)
        
print(f"\nAfter loading all .envs:")
print(f"ELEVENLABS_API_KEY: {os.getenv('ELEVENLABS_API_KEY', 'NOT SET')}")
gemini = os.getenv('GEMINI_API_KEY', 'NOT SET')
print(f"GEMINI_API_KEY: {gemini[:20] if gemini != 'NOT SET' else 'NOT SET'}...")
