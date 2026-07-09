"""Download additional viral fonts"""
import urllib.request
import os

FONT_DIR = "backend/fonts"
os.makedirs(FONT_DIR, exist_ok=True)

fonts = {
    "Anton-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/anton/Anton-Regular.ttf",
    "BebasNeue-Regular.ttf": "https://github.com/google/fonts/raw/main/ofl/bebasneue/BebasNeue-Regular.ttf",
    "Poppins-Bold.ttf": "https://github.com/google/fonts/raw/main/ofl/poppins/Poppins-Bold.ttf",
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

# Verify
print("\nFont directory contents:")
for f in os.listdir(FONT_DIR):
    fp = os.path.join(FONT_DIR, f)
    print(f"  {f}: {os.path.getsize(fp)} bytes")
