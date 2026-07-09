"""Test the /api/generate-video endpoint with the fix applied."""
import sys
sys.stdout.reconfigure(encoding='utf-8')

import httpx
import json

API_BASE = "http://127.0.0.1:8000"

script_data = {
    "fullText": "Those who keep secrets close to their chest, rule the world. Chanakya knew this. He said that a wise man keeps his intentions hidden like a turtle hides in its shell. Think about it. Follow for more ancient wisdom.",
    "sections": [
        {"type": "hook", "content": "Those who keep secrets close to their chest, rule the world.", "durationEstimate": 3},
        {"type": "authority", "content": "Chanakya knew this.", "durationEstimate": 2},
        {"type": "explanation", "content": "He said that a wise man keeps his intentions hidden like a turtle hides in its shell. Think about it.", "durationEstimate": 8},
        {"type": "cta", "content": "Follow for more ancient wisdom.", "durationEstimate": 3}
    ],
    "rage_bait_title": "SECRETS the Powerful DON'T Want You to Know"
}

audio_path = r"c:\Users\avich\Downloads\chanakya-reel-ai\backend\assets\voice_60efba89_dark_cinematic.wav"

video_req = {
    "script_data": script_data,
    "audio_path": audio_path,
    "bg_video_paths": None,
    "bg_music_path": None,
    "bg_music_volume": 0.15,
    "caption_size": "Medium",
    "use_smart_sfx": True,
    "use_auto_b_roll": True
}

print("Sending /api/generate-video request...")
print(f"Audio: {audio_path}")

try:
    with httpx.Client(timeout=600.0) as client:
        resp = client.post(f"{API_BASE}/api/generate-video", json=video_req)
        print(f"\nStatus: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        
        if resp.status_code == 200:
            print("\n[PASS] VIDEO GENERATION SUCCEEDED!")
        else:
            print("\n[FAIL] VIDEO GENERATION FAILED!")
except Exception as e:
    print(f"\n[FAIL] Request failed: {e}")
