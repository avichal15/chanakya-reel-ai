"""
ASS Subtitle Engine — FFmpeg-compatible animated subtitles
Generates .ass files with Hormozi-style animations (Pop, Highlight).
"""
import logging

logger = logging.getLogger(__name__)

# ── Configuration ───────────────────────────────────────────────
# Colors in BGR format (&HBBGGRR)
# We swap Primary and Secondary colors to achieve Karaoke effect:
# SecondaryColour is the base color (White)
# PrimaryColour is the highlighted color (Yellow)
COLOR_WHITE = "&HFFFFFF"      # White
COLOR_YELLOW = "&H33D6FF"     # Cinematic Gold (BGR format)
COLOR_BLACK = "&H000000"

# Frame Quantization & Timings
FPS = 24.0
VISUAL_OFFSET = -0.05  # Highlight triggers 50ms before audio

# Fonts (Internal Family Names - Must match TTF internal names)
# If Poppins-Bold.ttf is "Poppins" with Bold=1, we use "Poppins".
FONT_EN = "Poppins" 
FONT_HI = "Noto Sans Devanagari"

HEADER_TEMPLATE = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 1

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: English,{FONT_EN},{SIZE_EN},{COLOR_YELLOW},{COLOR_WHITE},{COLOR_BLACK},&H80000000,-1,0,0,0,100,100,0,0,1,8,6,2,20,20,580,1
Style: Hindi,{FONT_HI},{SIZE_HI},{COLOR_YELLOW},{COLOR_WHITE},{COLOR_BLACK},&H80000000,-1,0,0,0,100,100,0,0,1,8,6,2,20,20,580,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

def snap_to_frame(time_sec):
    """Quantize floating point seconds to the nearest exact frame boundary for 24 FPS."""
    return max(0.0, round(time_sec * FPS) / FPS)

def format_time(seconds):
    """Format total seconds to ASS timestamp format: H:MM:SS.cs"""
    seconds = max(0, seconds)
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def generate_ass(captions, output_path, caption_size="Medium", time_offset=0.0):
    """
    Generate .ass file from Whisper captions with word-level animation and dynamic sizing.
    """
    
    if caption_size == "Small":
        size_en, size_hi = 60, 65
    elif caption_size == "Large":
        size_en, size_hi = 100, 105
    else: # Medium
        size_en, size_hi = 80, 85
        
    content = HEADER_TEMPLATE.format(
        FONT_EN=FONT_EN,
        FONT_HI=FONT_HI,
        SIZE_EN=size_en,
        SIZE_HI=size_hi,
        COLOR_WHITE=COLOR_WHITE,
        COLOR_YELLOW=COLOR_YELLOW,
        COLOR_BLACK=COLOR_BLACK
    )

    global_offset = time_offset + VISUAL_OFFSET

    for cap_idx, cap in enumerate(captions):
        lang = cap.get("lang", "en")
        style = "Hindi" if lang == "hi" else "English"
        words = cap.get("words", [])

        if not words:
            start = format_time(snap_to_frame(cap["start"] + global_offset))
            end = format_time(snap_to_frame(cap["end"] + global_offset))
            text = cap["text"]
            anim = r"{\fscx110\fscy110\t(0,150,\fscx105\fscy105)}"
            content += f"Dialogue: 0,{start},{end},{style},,0,0,0,,{anim}{text}\n"
            continue

        chunk_size = 3
        chunks = [words[i:i+chunk_size] for i in range(0, len(words), chunk_size)]

        for c_idx, chunk in enumerate(chunks):
            if not chunk: continue

            line_start_sec = snap_to_frame(chunk[0]["start"] + global_offset)
            
            # Determine line end time
            if c_idx < len(chunks) - 1:
                line_end_sec = snap_to_frame(chunks[c_idx + 1][0]["start"] + global_offset)
            else:
                if cap_idx < len(captions) - 1 and captions[cap_idx+1].get("words"):
                    line_end_sec = snap_to_frame(captions[cap_idx+1]["words"][0]["start"] + global_offset)
                else:
                    line_end_sec = snap_to_frame(chunk[-1]["end"] + global_offset) + 0.5

            if line_end_sec <= line_start_sec:
                line_end_sec = line_start_sec + 0.1

            line_start_cs = int(round(line_start_sec * 100))
            current_cs = line_start_cs

            karaoke_text = ""
            for w_idx, w in enumerate(chunk):
                w_start_sec = snap_to_frame(w["start"] + global_offset)
                w_end_sec = snap_to_frame(w["end"] + global_offset)

                w_start_cs = int(round(w_start_sec * 100))
                w_end_cs = int(round(w_end_sec * 100))

                if w_start_cs < current_cs:
                    w_start_cs = current_cs
                if w_end_cs <= w_start_cs:
                    w_end_cs = w_start_cs + 1
                    
                gap_cs = w_start_cs - current_cs
                
                if w_idx > 0:
                    if gap_cs > 0:
                        karaoke_text += f"{{\\k{gap_cs}}} "
                    else:
                        karaoke_text += " "
                else:
                    if gap_cs > 0:
                        karaoke_text += f"{{\\k{gap_cs}}}"

                w_dur_cs = w_end_cs - w_start_cs
                word_text = w["word"].strip()
                karaoke_text += f"{{\\k{w_dur_cs}}}{word_text}"

                current_cs = w_end_cs

            anim = r"{\fscx110\fscy110\t(0,100,\fscx105\fscy105)}"
            start_str = format_time(line_start_sec)
            end_str = format_time(line_end_sec)

            content += f"Dialogue: 0,{start_str},{end_str},{style},,0,0,0,,{anim}{karaoke_text}\n"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    return output_path
