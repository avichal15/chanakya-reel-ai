"""Download Montserrat ExtraBold font"""
import urllib.request
import os

FONT_DIR = "backend/fonts"
os.makedirs(FONT_DIR, exist_ok=True)

# Correct URL for Montserrat ExtraBold from Google Fonts repo
url = "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat-ExtraBold.ttf"
path = os.path.join(FONT_DIR, "Montserrat-ExtraBold.ttf")

if os.path.exists(path):
    print(f"Already exists: {path} ({os.path.getsize(path)} bytes)")
else:
    print(f"Downloading {path}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"  OK: {os.path.getsize(path)} bytes")
    except Exception as e:
        print(f"  FAILED: {e}")
