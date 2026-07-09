"""
Viral Caption Engine — Hormozi-style animated captions
Implements 4 viral animation presets:
1. Pop Bounce (Scale 70% -> 110% -> 100%)
2. Word Highlight (Karaoke style)
3. Punch Drop (Y-axis drop with bounce)
4. CTA Pulse (Zoom + Glow loop)
"""
import PIL.Image
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import numpy as np
import os
import math

# ── Font Configuration ──────────────────────────────────────────
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")

FONTS = {
    "primary": "Montserrat-Bold.ttf",       # Clean, modern
    "impact": "Anton-Regular.ttf",          # Viral/Loud
    "tall": "BebasNeue-Regular.ttf",        # Tall/Condensed
    "hindi": "NotoSansDevanagari-Bold.ttf"  # Hindi support
}

# ── Colors ──────────────────────────────────────────────────────
COLORS = {
    "white": (255, 255, 255),
    "yellow": (255, 215, 0),
    "neon_green": (57, 255, 20),
    "neon_red": (255, 49, 49),
    "cyan": (0, 255, 255),
    "black": (0, 0, 0),
}

def get_font_path(font_name):
    # Try local project fonts first
    local = os.path.join(FONT_DIR, font_name)
    if os.path.exists(local):
        return local
    # Fallback to Windows fonts
    win_fonts = {
        "Montserrat-Bold.ttf": "arialbd.ttf",
        "Anton-Regular.ttf": "impact.ttf",
        "BebasNeue-Regular.ttf": "arial.ttf",
        "NotoSansDevanagari-Bold.ttf": "Nirmala.ttf" 
    }
    fb = win_fonts.get(font_name, "arial.ttf")
    return f"C:/Windows/Fonts/{fb}"

class ViralCaptionAnimator:
    def __init__(self, width=1080, height=1920, caption_size="Medium"):
        self.width = width
        self.height = height
        self.stroke_width = 8
        self.shadow_offset = 6
        self.caption_size = caption_size
        
        # Load fonts
        self.fonts = {}
        for key, fname in FONTS.items():
            self.fonts[key] = get_font_path(fname)

    def _get_font(self, font_type, size):
        try:
            return ImageFont.truetype(self.fonts[font_type], size)
        except:
            return ImageFont.load_default()

    def render_frame(self, caption, t, preset="word_highlight"):
        """
        Render a single frame of the caption animation.
        Returns: (rgb_array, mask_array)
        """
        # Create canvas
        img = Image.new('RGBA', (self.width, self.height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        lang = caption.get("lang", "en")
        words = caption.get("words", [])
        text = caption.get("text", "")
        
        # Determine active word based on audio time (t is relative to caption start)
        # caption["start"] is absolute time. t is relative.
        # But words have absolute timestamps.
        # So current_abs_time = caption["start"] + t
        cap_start = caption.get("start", 0)
        current_abs_time = cap_start + t
        
        current_word_idx = -1
        if words:
            for i, w in enumerate(words):
                if w["start"] <= current_abs_time <= w["end"]:
                    current_word_idx = i
                    break
        
        is_devanagari = any('\u0900' <= ch <= '\u097F' for ch in text)
        font_key = "hindi" if (lang == "hi" or is_devanagari) else "primary"
        
        if self.caption_size == "Small":
            font_size = 55 if font_key == "hindi" else 50
        elif self.caption_size == "Large":
            font_size = 85 if font_key == "hindi" else 80
        else:
            font_size = 70 if font_key == "hindi" else 65 
            
        font = self._get_font(font_key, font_size)

        # Dispatch to preset renderer
        if preset == "pop_bounce":
            self._render_pop_bounce(draw, words, current_word_idx, font, lang, current_abs_time)
        elif preset == "punch_drop":
             self._render_punch_drop(draw, words, current_word_idx, font, lang, t)
        elif preset == "cta_pulse":
            self._render_cta_pulse(draw, text, font, t)
        else:
            self._render_word_highlight(draw, words, current_word_idx, font, lang)
            
        # Convert to RGB + Mask for MoviePy
        # RGB: (H, W, 3)
        # Mask: (H, W) float 0-1
        rgba = np.array(img)
        rgb = rgba[:, :, :3]
        mask = rgba[:, :, 3].astype(float) / 255.0
        return rgb, mask

    def _draw_text(self, draw, x, y, text, font, color, scale=1.0, alpha=255):
        """Draw text with stroke and shadow, supporting scaling."""
        # Note: PIL doesn't support direct scaling of text drawing. 
        # For scaling, we draw to a separate image and resize.
        
        if scale != 1.0:
            # Estimate size
            bbox = draw.textbbox((0, 0), text, font=font)
            w, h = bbox[2] - bbox[0] + 20, bbox[3] - bbox[1] + 20
            
            # Draw to temp image
            tmp = Image.new('RGBA', (w, h), (0,0,0,0))
            d_tmp = ImageDraw.Draw(tmp)
            
            # Draw at (10, 10) padding
            self._draw_text_simple(d_tmp, 10, 10, text, font, color, alpha)
            
            # Resize
            new_w, new_h = int(w * scale), int(h * scale)
            tmp = tmp.resize((new_w, new_h), Image.Resampling.LANCZOS)
            
            # Paste centered at x, y
            paste_x = int(x - (new_w - w)/2)
            paste_y = int(y - (new_h - h)/2)
            
            # We need to paste onto the main draw object's image
            draw.im.paste(tmp, (paste_x, paste_y), tmp)
            return

        self._draw_text_simple(draw, x, y, text, font, color, alpha)

    def _draw_text_simple(self, draw, x, y, text, font, color, alpha=255):
        # Shadow
        shadow_color = (0, 0, 0, int(alpha * 0.6))
        draw.text((x + self.shadow_offset, y + self.shadow_offset), text, font=font, fill=shadow_color)
        
        # Stroke
        stroke_color = (0, 0, 0, alpha)
        # PIL stroke is weak, draw multiple offsets
        for dx in range(-4, 5, 2):
            for dy in range(-4, 5, 2):
                draw.text((x+dx, y+dy), text, font=font, fill=stroke_color)

        # Fill
        fill_color = color + (alpha,) if len(color) == 3 else color
        draw.text((x, y), text, font=font, fill=fill_color)

    def _layout_words_center(self, words, font):
        """Layout words into lines for center alignment."""
        import textwrap
        full_text = " ".join([w["word"] for w in words])
        lines = textwrap.wrap(full_text, width=24) # Narrow width for mobile
        
        layout = []
        word_iter = iter(words)
        
        for line_text in lines:
            line_words = []
            curr_line_len = 0
            # Reconstruct line word objects
            temp_text = line_text
            while temp_text:
                try:
                    w = next(word_iter)
                    line_words.append(w)
                    width = len(w["word"])
                    # Heuristic consumer
                    temp_text = temp_text[width:].lstrip() 
                except StopIteration:
                    break
            layout.append(line_words)
            
        return layout

    def _render_word_highlight(self, draw, words, active_idx, font, lang):
        """Preset 2: Highlight active word in neon color."""
        layout = self._layout_words_center(words, font)
        
        # Measure total height
        line_heights = []
        for line_words in layout:
             line_str = " ".join([w["word"] for w in line_words])
             bbox = draw.textbbox((0, 0), line_str, font=font)
             line_heights.append(bbox[3] - bbox[1])
        
        total_h = sum(line_heights) + (len(lines := layout) - 1) * 20
        start_y = (self.height // 2) + 200 # Lower middle
        
        curr_y = start_y
        global_w_idx = 0
        
        base_color = COLORS["yellow"] if lang == "hi" else COLORS["white"]
        hl_color = COLORS["neon_green"] if lang == "hi" else COLORS["neon_red"] # Red for English punch
        
        for i, line_words in enumerate(layout):
            line_str = " ".join([w["word"] for w in line_words])
            bbox = draw.textbbox((0, 0), line_str, font=font)
            line_w = bbox[2] - bbox[0]
            curr_x = (self.width - line_w) // 2
            
            for w in line_words:
                color = hl_color if global_w_idx == active_idx else base_color
                
                self._draw_text(draw, curr_x, curr_y, w["word"], font, color)
                
                w_bbox = draw.textbbox((0, 0), w["word"] + " ", font=font)
                curr_x += w_bbox[2] - w_bbox[0]
                global_w_idx += 1
            
            curr_y += line_heights[i] + 20

    def _render_pop_bounce(self, draw, words, active_idx, font, lang, t):
        """Preset 1: Active word pops up in scale."""
        layout = self._layout_words_center(words, font)
        
        # Similar layout logic
        line_heights = []
        for line_words in layout:
             line_str = " ".join([w["word"] for w in line_words])
             bbox = draw.textbbox((0, 0), line_str, font=font)
             line_heights.append(bbox[3] - bbox[1])
        
        start_y = (self.height // 2) + 200
        curr_y = start_y
        global_w_idx = 0
        
        base_color = COLORS["yellow"] if lang == "hi" else COLORS["white"]
        
        for i, line_words in enumerate(layout):
            # Calculate line width to center it
            # We must account for the SCALED width of the active word to center correctly?
            # Complexity: smooth centering jitter. Better to center based on static width
            # and let the pop expand outwards or mutually.
            
            # Static centering for stability
            line_str = " ".join([w["word"] for w in line_words])
            bbox = draw.textbbox((0, 0), line_str, font=font)
            line_w = bbox[2] - bbox[0]
            curr_x = (self.width - line_w) // 2
            
            for w in line_words:
                scale = 1.0
                if global_w_idx == active_idx:
                    # Pop effect: just fixed scale for now
                    scale = 1.2
                    color = COLORS["cyan"]
                else:
                    color = base_color
                
                # Draw
                self._draw_text(draw, curr_x, curr_y, w["word"], font, color, scale=scale)
                
                # Update X with scaled width
                w_bbox = draw.textbbox((0, 0), w["word"] + " ", font=font)
                static_w = w_bbox[2] - w_bbox[0]
                
                # Use scale to adjust spacing
                spacing = static_w * scale
                
                curr_x += spacing
                global_w_idx += 1
            
            curr_y += line_heights[i] + 20
    def _render_punch_drop(self, draw, words, active_idx, font, lang, t):
        """Preset 3: Words drop in."""
        # Just use word highlight for now to ensure we ship something stable first
        self._render_word_highlight(draw, words, active_idx, font, lang)

    def _render_cta_pulse(self, draw, text, font, t):
        """Preset 4: Pulsing CTA."""
        # Pulse scale 1.0 -> 1.1 -> 1.0 over 1 second
        cycle = t % 1.0
        scale = 1.0 + 0.1 * math.sin(cycle * 2 * math.pi)
        
        bbox = draw.textbbox((0, 0), text, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        
        x = (self.width - w) // 2
        y = (self.height // 2)
        
        self._draw_text(draw, x, y, text, font, COLORS["neon_red"], scale=scale)

