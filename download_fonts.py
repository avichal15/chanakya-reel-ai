"""Download bold fonts for video captions"""
import urllib.request
import os

FONT_DIR = "backend/fonts"
os.makedirs(FONT_DIR, exist_ok=True)

fonts = {
    "Montserrat-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/montserrat/Montserrat%5Bwght%5D.ttf",
    "NotoSansDevanagari-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari/NotoSansDevanagari%5Bwdth%2Cwght%5D.ttf",
}

for name, url in fonts.items():
    path = os.path.join(FONT_DIR, name)
    if os.path.exists(path):
        print(f"Already exists: {name} ({os.path.getsize(path)} bytes)")
        continue
    print(f"Downloading {name}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"  OK: {os.path.getsize(path)} bytes")
    except Exception as e:
        print(f"  FAILED: {e}")
        # Fallback: try alternative URL format
        alt_url = url.replace("%5B", "[").replace("%5D", "]").replace("%2C", ",")
        try:
            urllib.request.urlretrieve(alt_url, path)
            print(f"  OK (alt): {os.path.getsize(path)} bytes")
        except Exception as e2:
            print(f"  FAILED (alt): {e2}")

# Verify
print("\nFont directory contents:")
for f in os.listdir(FONT_DIR):
    fp = os.path.join(FONT_DIR, f)
    print(f"  {f}: {os.path.getsize(fp)} bytes")
