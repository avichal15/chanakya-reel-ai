"""
Debug script to test Hindi caption rendering with PIL.
"""
from PIL import Image, ImageDraw, ImageFont
import os

FONT_DIR = "backend/fonts"
HI_FONT = os.path.join(FONT_DIR, "NotoSansDevanagari-Bold.ttf")
EN_FONT = os.path.join(FONT_DIR, "Montserrat-Bold.ttf")

WIDTH, HEIGHT = 1080, 1920

def test_render(text, font_path, out_name):
    print(f"Testing render for: '{text}' using {font_path}")
    
    if not os.path.exists(font_path):
        print(f"ERROR: Font not found: {font_path}")
        return

    img = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 255)) # Black bg
    draw = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype(font_path, 80)
        print("Font loaded successfully.")
    except Exception as e:
        print(f"ERROR loading font: {e}")
        return

    # Draw centered
    bbox = draw.textbbox((0, 0), text, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (WIDTH - w) // 2
    y = (HEIGHT - h) // 2
    
    # Draw with yellow color
    draw.text((x, y), text, font=font, fill=(255, 215, 0, 255))
    
    out_path = f"debug_{out_name}.png"
    img.save(out_path)
    print(f"Saved: {out_path} ({os.path.getsize(out_path)} bytes)")

# Test English
test_render("Viral Philosophy", EN_FONT, "en")

# Test Hindi/Devanagari
hindi_text = "सच कड़वा होता है"
test_render(hindi_text, HI_FONT, "hi")

# Test Mixed
mixed_text = "Truth is bitter | सच कड़वा है"
test_render(mixed_text, HI_FONT, "mixed_hi_font")
