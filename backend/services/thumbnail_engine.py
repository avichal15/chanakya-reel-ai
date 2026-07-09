import os
from PIL import Image, ImageDraw, ImageFont

FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")

def get_font_path():
    local = os.path.join(FONT_DIR, "Anton-Regular.ttf")
    if os.path.exists(local):
        return local
    return "C:/Windows/Fonts/impact.ttf"

def create_rage_thumbnail(text: str, output_path: str, width=1080, height=1920, bg_image_path=None):
    """
    Generates a highly provocative text-based thumbnail image (Rage Bait)
    """
    if bg_image_path and os.path.exists(bg_image_path):
        from textwrap import wrap
        from PIL import ImageEnhance
        img = Image.open(bg_image_path).convert('RGB')
        img = img.resize((width, height), Image.Resampling.LANCZOS)
        enhancer = ImageEnhance.Brightness(img)
        img = enhancer.enhance(0.6)  # Darken to make text pop
    else:
        img = Image.new('RGB', (width, height), color=(15, 15, 18))
    draw = ImageDraw.Draw(img)
    
    font_path = get_font_path()
    try:
        # Verify font loads
        ImageFont.truetype(font_path, 50)
    except:
        font_path = "arial.ttf"
        
    text = text.upper()
    
    # intelligent line breaks (max 3-4 words per line)
    words = text.split()
    lines = []
    current_line = []
    for w in words:
        current_line.append(w)
        if len(current_line) >= 3:
            lines.append(" ".join(current_line))
            current_line = []
    if current_line:
        if lines:
            lines[-1] += " " + " ".join(current_line)
        else:
            lines.append(" ".join(current_line))
            
    # Base font size to match reference
    font_size = 180
    font = ImageFont.truetype(font_path, font_size)
    
    # Calculate total height to center vertically
    y_offset = height // 2 - (len(lines) * (font_size + 20)) // 2
    
    for idx, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        # Scale down if it exceeds the width
        current_font = font
        current_size = font_size
        while text_w > width - 100 and current_size > 50:
            current_size -= 10
            current_font = ImageFont.truetype(font_path, current_size)
            bbox = draw.textbbox((0, 0), line, font=current_font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]
            
        x = (width - text_w) // 2
        
        # Consistent bold Red color matching the reference
        color = (239, 68, 68)  # Tailwind red-500 equivalent
        
        # Strong diffused Shadow/Glow
        shadow_layers = 15
        for s in range(shadow_layers, 0, -1):
            alpha = int(255 * (s / shadow_layers))
            draw.text((x + s, y_offset + s), line, font=current_font, fill=(0,0,0, alpha))
            draw.text((x - s, y_offset + s), line, font=current_font, fill=(0,0,0, alpha))
            draw.text((x + s, y_offset - s), line, font=current_font, fill=(0,0,0, alpha))
            draw.text((x - s, y_offset - s), line, font=current_font, fill=(0,0,0, alpha))
                
        # Fill
        draw.text((x, y_offset), line, font=current_font, fill=color)
        
        y_offset += text_h + 30
        
    img.save(output_path)
    return output_path
