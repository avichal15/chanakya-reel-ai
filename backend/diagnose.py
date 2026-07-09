
import os
import sys
from dotenv import load_dotenv
from moviepy.config import get_setting

# Load env from different possible locations
load_dotenv('backend/.env')
load_dotenv('.env')

print(f"Current Working Directory: {os.getcwd()}")
print(f"Gemini Key Present: {bool(os.getenv('GEMINI_API_KEY'))}")
print(f"ElevenLabs Key Present: {bool(os.getenv('ELEVENLABS_API_KEY'))}")

print("-" * 20)
print("Checking MoviePy Configuration:")
try:
    ffmpeg_binary = get_setting('FFMPEG_BINARY')
    print(f"MoviePy FFmpeg Binary: {ffmpeg_binary}")
    
    # Try to execute it
    import subprocess
    result = subprocess.run([ffmpeg_binary, '-version'], capture_output=True, text=True)
    if result.returncode == 0:
        print("FFmpeg execution successful.")
    else:
        print(f"FFmpeg execution failed with code {result.returncode}")
        print(result.stderr)
except Exception as e:
    print(f"MoviePy FFmpeg Error: {e}")

print("-" * 20)
print("Testing Gemini API:")
try:
    import google.generativeai as genai
    key = os.getenv('GEMINI_API_KEY')
    if not key:
        print("Skipping Gemini test (No Key)")
    else:
        genai.configure(api_key=key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hello")
        if response and response.text:
            print("Gemini Test: Success")
        else:
            print("Gemini Test: Failed (Empty Response)")
except Exception as e:
    print(f"Gemini Test Error: {e}")

print("-" * 20)
print("Testing ElevenLabs API:")
try:
    from elevenlabs.client import ElevenLabs
    key = os.getenv('ELEVENLABS_API_KEY')
    if not key:
        print("Skipping ElevenLabs test (No Key)")
    else:
        client = ElevenLabs(api_key=key)
        # Just list voices to verify auth
        voices = client.voices.get_all()
        print(f"ElevenLabs Test: Success (Found {len(voices.voices)} voices)")
except Exception as e:
    print(f"ElevenLabs Test Error: {e}")
