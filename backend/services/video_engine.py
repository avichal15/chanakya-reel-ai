"""
Cinematic Video Engine — Philosophy Reel Generator
Produces Instagram-ready 1080x1920 MP4 reels with:
  - Whisper-synced bilingual captions (English=white, Hindi=yellow)
  - ASS Subtitles with Hormozi-style animations (Pop, Highlight)
  - Cinematic effects: slow zoom, dark grading, film grain, fades
  - Background video support or gradient fallback
"""
import PIL.Image

# Monkeypatch for MoviePy compatibility with Pillow 10+
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import (
    VideoFileClip, AudioFileClip, ColorClip, ImageClip,
    CompositeVideoClip, CompositeAudioClip, concatenate_videoclips, vfx
)
import numpy as np
import os
import logging
from . import caption_sync
from . import scene_engine
from . import ass_engine
from . import viral_caption_engine

logger = logging.getLogger(__name__)

# ── Constants ───────────────────────────────────────────────────
WIDTH, HEIGHT = 1080, 1920
FPS = 24
MAX_DURATION = 60  # seconds

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "output")
FONT_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fonts")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Cinematic Effects ───────────────────────────────────────────



def create_gradient_background(duration: float, color1=(15, 5, 25), color2=(5, 15, 35)) -> VideoFileClip:
    """Create a vertical gradient background."""
    img = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        img[y, :] = [r, g, b]
    return ImageClip(img).set_duration(duration)

def apply_ken_burns(clip, zoom_ratio=1.08):
    """Apply slow zoom (ken burns) effect."""
    duration = clip.duration
    def zoom_effect(get_frame, t):
        frame = get_frame(t)
        h, w = frame.shape[:2]
        progress = t / duration if duration > 0 else 0
        scale = 1.0 + (zoom_ratio - 1.0) * progress
        # Crop center
        new_h, new_w = int(h / scale), int(w / scale)
        y1, x1 = (h - new_h) // 2, (w - new_w) // 2
        from PIL import Image as PILImg
        pil_img = PILImg.fromarray(frame[y1:y1+new_h, x1:x1+new_w])
        pil_img = pil_img.resize((w, h), PILImg.LANCZOS)
        return np.array(pil_img)
    return clip.fl(zoom_effect)

# ── Main Generator ──────────────────────────────────────────────

# ── Main Generator ──────────────────────────────────────────────

def generate_video(
    script_data: dict,
    audio_path: str,
    bg_video_paths: list = None,
    bg_music_path: str = None,
    bg_music_volume: float = 0.15,
    caption_size: str = "Medium",
    use_smart_sfx: bool = True,
    use_auto_b_roll: bool = False,
    output_filename: str = "output.mp4",
    use_ass: bool = True
) -> str:
    """
    Generate video with ASS subtitles (primary) or PIL fallback.
    """
    temp_video_path = os.path.join(OUTPUT_DIR, f"temp_{output_filename}")
    final_output_path = os.path.join(OUTPUT_DIR, output_filename)
    log_file = os.path.join(os.path.dirname(OUTPUT_DIR), "logs", "video_cmd.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    try:
        logger.info(f"Starting video generation: {audio_path}")
        if not os.path.exists(audio_path):
            return f"Error: Audio file not found: {audio_path}"

        audio = AudioFileClip(audio_path)
        duration = min(audio.duration, MAX_DURATION)

        # 1. Generate or Load Captions
        logger.info("Generating timestamps...")
        import json
        json_path = audio_path.replace(".wav", ".json").replace(".mp3", ".json")
        captions = []
        try:
            if os.path.exists(json_path):
                logger.info(f"Native timestamps found at {json_path}. Bypassing Whisper.")
                with open(json_path, "r", encoding="utf-8") as f:
                    words = json.load(f)
                if words:
                    captions = [{
                        "start": words[0]["start"],
                        "end": words[-1]["end"],
                        "text": " ".join([w["word"] for w in words]),
                        "lang": "en", 
                        "words": words
                    }]
            else:
                logger.info("No native timestamps found. Falling back to strict Whisper VAD.")
                captions = caption_sync.transcribe_audio(audio_path)
                
            if not captions:
                raise Exception("Empty captions array returned.")
        except Exception as e:
            logger.warning(f"Timestamp generation failed: {e}")
            full_text = script_data.get("fullText", "")
            captions = caption_sync.create_fallback_captions(full_text, duration)

        # 2. Visuals (Bg + Effects)
        bg_clip = None

        # Mode B-1: Multiple Uploaded Videos
        if bg_video_paths and len(bg_video_paths) > 0:
            logger.info(f"Mode B-1: Using {len(bg_video_paths)} uploaded videos")
            clips = []
            for path in bg_video_paths:
                if os.path.exists(path):
                    # Load and vertically resize to fit height immediately to save memory/processing
                    clip = VideoFileClip(path).resize(height=HEIGHT)
                    if clip.w > WIDTH:
                        x_center = clip.w / 2
                        clip = clip.crop(x1=x_center - WIDTH/2, y1=0, x2=x_center + WIDTH/2, y2=HEIGHT)
                    clips.append(clip)
            
            if clips:
                # Concatenate all clips
                bg_clip = concatenate_videoclips(clips, method="compose")
                # Loop the sequence to fill audio duration
                if bg_clip.duration < duration:
                    bg_clip = bg_clip.fx(vfx.loop, duration=duration)
                else:
                    bg_clip = bg_clip.subclip(0, duration)
        
        # Mode A: AI Scene Generation (Fallback if no uploaded video)
        if not bg_clip:
            logger.info("Mode A: AI Scene Generation")
            full_text = script_data.get("fullText", "") \
                        or " ".join([s.get("content", "") for s in script_data.get("sections", [])])
            scenes = scene_engine.analyze_scenes(full_text)
            
            scene_dir = os.path.join(ASSETS_DIR, "scenes")
            stock_files = [f for f in os.listdir(scene_dir) if f.endswith(('.mp4', '.mov'))] if os.path.isdir(scene_dir) else []
            
            # Prioritize Auto-B-Roll if enabled
            if use_auto_b_roll and len(scenes) > 0:
                clips = []
                seg_dur = duration / len(scenes)
                for sc in scenes:
                    clip_added = False
                    try:
                        from .pexels_engine import search_and_download_video
                        theme = sc.get("theme", "cinematic")
                        keywords = sc.get("keywords", [])
                        query = f"{theme} {keywords[0] if keywords else 'aesthetic'}"
                        
                        logger.info(f"Auto B-Roll: Fetching clip for '{query}' (duration: {seg_dur:.1f}s)")
                        vid_path = search_and_download_video(query, min_duration=int(seg_dur) + 1)
                        
                        if vid_path and os.path.exists(vid_path):
                            px_clip = VideoFileClip(vid_path)
                            px_clip = px_clip.resize(height=HEIGHT)
                            if px_clip.w > WIDTH:
                                x_c = px_clip.w / 2
                                px_clip = px_clip.crop(x1=x_c - WIDTH/2, y1=0, x2=x_c + WIDTH/2, y2=HEIGHT)
                            if px_clip.duration < seg_dur:
                                px_clip = px_clip.fx(vfx.loop, duration=seg_dur)
                            else:
                                px_clip = px_clip.subclip(0, seg_dur)
                                
                            clips.append(px_clip)
                            clip_added = True
                    except Exception as e:
                        logger.error(f"Auto B-Roll failed for scene: {e}")
                        
                    # Mixed Fallback: if Pexels fails for one scene, use gradient
                    if not clip_added:
                        colors = scene_engine.get_theme_colors(sc.get("theme", "default"))
                        clips.append(create_gradient_background(seg_dur, colors[0], colors[1]))
                bg_clip = concatenate_videoclips(clips, method="compose")
            
            # Local Stock Video Fallback
            elif stock_files:
                bg_clip = VideoFileClip(os.path.join(scene_dir, stock_files[0]))
                bg_clip = bg_clip.loop(duration=duration).resize(height=HEIGHT)
                if bg_clip.w > WIDTH:
                    x_c = bg_clip.w / 2
                    bg_clip = bg_clip.crop(x1=x_c - WIDTH/2, y1=0, x2=x_c + WIDTH/2, y2=HEIGHT)
                bg_clip = bg_clip.subclip(0, duration)
                
            # Full Gradient Sequence Fallback
            elif len(scenes) > 1:
                clips = []
                seg_dur = duration / len(scenes)
                for sc in scenes:
                    colors = scene_engine.get_theme_colors(sc.get("theme", "default"))
                    clips.append(create_gradient_background(seg_dur, colors[0], colors[1]))
                bg_clip = concatenate_videoclips(clips, method="compose")
                
            # Solid Gradient Fallback
            else:
                bg_clip = create_gradient_background(duration)

        bg_clip = bg_clip.set_duration(duration)
        bg_clip = bg_clip.set_fps(FPS)  # Ensure fps is set on clip (MoviePy 1.0.3 + decorator 5.x compat)
        bg_clip = apply_ken_burns(bg_clip)
        
        # Pixel grading (brightness, saturation, grain) has been offloaded to FFmpeg
        bg_clip = bg_clip.fadeout(0.5)

        # Mix narrator voice with optional background music and SFX
        narrator_audio = audio.subclip(0, duration)
        
        if use_smart_sfx:
            logger.info("Applying Smart SFX Engine...")
            sfx_clips = [narrator_audio.set_start(0)]
            sfx_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "sfx")
            whoosh_path = os.path.join(sfx_dir, "whoosh.wav")
            impact_path = os.path.join(sfx_dir, "impact.wav")
            coin_path = os.path.join(sfx_dir, "coin.wav")
            
            # 1. Whoosh at 0.0s
            if os.path.exists(whoosh_path):
                sfx_clips.append(AudioFileClip(whoosh_path).set_start(0.0).volumex(0.3))
                
            # Flatten whisper captions for word lookup
            word_times = []
            for cap in captions:
                for w in cap.get("words", []):
                    word_times.append({"word": w["word"].strip().lower(), "start": w["start"]})
                    
            if word_times:
                def find_timestamp(query_string):
                    # Basic lookup: first word matches
                    first_word = query_string.split()[0].strip().lower()
                    for w in word_times:
                        # strip punctuation
                        clean_w = ''.join(c for c in w["word"] if c.isalnum())
                        clean_first = ''.join(c for c in first_word if c.isalnum())
                        if clean_first and clean_first in clean_w:
                            return w["start"]
                    return -1

                sections = script_data.get("sections", [])
                for sec in sections:
                    if sec["type"] == "hindi_translation" and os.path.exists(impact_path):
                        ts = find_timestamp(sec["content"])
                        if ts >= 0:
                            sfx_clips.append(AudioFileClip(impact_path).set_start(ts).volumex(0.4))
                    elif sec["type"] == "cta" and os.path.exists(coin_path):
                        ts = find_timestamp(sec["content"])
                        if ts >= 0:
                            sfx_clips.append(AudioFileClip(coin_path).set_start(ts).volumex(0.4))
            
            narrator_audio = CompositeAudioClip(sfx_clips).set_duration(duration)

        if bg_music_path and os.path.exists(bg_music_path):
            logger.info(f"Mixing background music: {bg_music_path}")
            try:
                bg_music = AudioFileClip(bg_music_path)
                # Loop or trim bg music to match voiceover duration
                if bg_music.duration < duration:
                    bg_music = bg_music.fx(vfx.loop, duration=duration)
                else:
                    bg_music = bg_music.subclip(0, duration)
                # Reduce bg music volume so narrator stays clear
                bg_music = bg_music.volumex(bg_music_volume)
                final_audio = CompositeAudioClip([narrator_audio, bg_music])
            except Exception as e:
                logger.warning(f"Failed to mix bg music: {e}. Using narrator only.")
                final_audio = narrator_audio
        else:
            final_audio = narrator_audio

        # Generate and prepend Thumbnail Frame
        sections = script_data.get("sections", [])
        hook_text = ""
        if sections and len(sections) > 0:
            hook_text = sections[0].get("content", "").strip()
            
        rage_title = hook_text if hook_text else script_data.get("rage_bait_title", "").strip()
        
        if rage_title:
            logger.info("Generating Rage Bait Thumbnail...")
            from .thumbnail_engine import create_rage_thumbnail
            from moviepy.editor import ImageClip
            
            # Extract first frame (must use PNG to support RGBA composite alpha channels)
            bg_frame_path = os.path.join(OUTPUT_DIR, f"bg_frame_{output_filename.replace('.mp4', '.png')}")
            bg_clip.save_frame(bg_frame_path, t=0.0)
            
            thumb_path = os.path.join(OUTPUT_DIR, f"thumb_{output_filename.replace('.mp4', '.jpg')}")
            create_rage_thumbnail(rage_title, thumb_path, WIDTH, HEIGHT, bg_image_path=bg_frame_path)
            
            # Create a 0.2s clip and concatenate to shift video & audio
            # Using 0.2s to ensure the frame persists long enough for thumbnail picker algorithms
            thumb_clip = ImageClip(thumb_path).set_duration(0.2).set_fps(FPS)
            bg_clip = concatenate_videoclips([thumb_clip, bg_clip])
            
            # Shift the audio to match the 0.2s thumbnail offset
            final_audio = CompositeAudioClip([final_audio.set_start(0.2)]).set_duration(final_audio.duration + 0.2)

        # Attach audio AFTER concatenation so audio track matches total video duration
        bg_clip = bg_clip.set_audio(final_audio)

        # 3. Compositing logic
        
        # Calculate offset caused by the thumbnail
        time_offset = 0.2 if rage_title else 0.0

        if use_ass:
            # Render Clean Base -> Burn with FFmpeg
            logger.info("Pipeline: ASS Implementation (Primary)")
            
            # Generate ASS
            ass_path = os.path.join(OUTPUT_DIR, output_filename.replace(".mp4", ".ass"))
            ass_engine.generate_ass(captions, ass_path, caption_size, time_offset=time_offset)
            
            # Write temp
            bg_clip.write_videofile(
                temp_video_path, fps=FPS, codec="h264_nvenc", audio_codec="aac",
                ffmpeg_params=["-preset", "fast"],
                audio_fps=44100, bitrate="8000k", threads=4, logger=None
            )
            bg_clip.close()
            audio.close()
            
            # Burn
            def escape_path(path):
                return path.replace("\\", "/").replace(":", "\\:")
            
            escaped_ass = escape_path(ass_path)
            escaped_fonts = escape_path(FONT_DIR)
            
            cmd = [
                "ffmpeg", "-y",
                "-i", temp_video_path,
                "-vf", f"eq=brightness=-0.1:saturation=1.2,noise=alls=10:allf=t,ass='{escaped_ass}':fontsdir='{escaped_fonts}'",
                "-c:v", "h264_nvenc",
                "-preset", "p6", 
                "-r", str(FPS),
                "-c:a", "copy",
                final_output_path
            ]
            
            # Log command
            cmd_str = " ".join(cmd)
            logger.info(f"FFmpeg command: {cmd_str}")
            with open(log_file, "a", encoding="utf-8") as lf:
                lf.write(f"\n[ASS_BURN] {cmd_str}\n")
                
            import subprocess
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            if result.returncode != 0:
                logger.error(f"FFmpeg burn failed: {result.stderr.decode()}")
                with open(log_file, "a", encoding="utf-8") as lf:
                    lf.write(f"[ERROR] {result.stderr.decode()}\n")
                return f"Error: FFmpeg: {result.stderr.decode()[:200]}"
                
            # Cleanup
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
                
        else:
            # Fallback PIL Pipeline
            logger.info("Pipeline: PIL Implementation (Fallback)")
            from .viral_caption_engine import ViralCaptionAnimator
            
            caption_animator = ViralCaptionAnimator(WIDTH, HEIGHT, caption_size)
            
            caption_clips = []
            for cap in captions:
                cap_start = cap["start"] + time_offset
                cap_duration = min(cap["end"] + time_offset, duration) - cap_start
                if cap_duration <= 0: continue
                
                from moviepy.editor import VideoClip
                
                # Use ViralCaptionAnimator (returning rgb, mask)
                def make_frame_rgb(t):
                    rgb, _ = caption_animator.render_frame(cap, t)
                    return rgb
                def make_frame_mask(t):
                    _, mask = caption_animator.render_frame(cap, t)
                    return mask
                    
                txt_clip = VideoClip(make_frame_rgb, duration=cap_duration)
                mask_clip = VideoClip(make_frame_mask, duration=cap_duration, ismask=True)
                txt_clip = txt_clip.set_mask(mask_clip).set_start(cap_start).set_position('center')
                caption_clips.append(txt_clip)
                
            final = CompositeVideoClip([bg_clip] + caption_clips, size=(WIDTH, HEIGHT))
            final = final.set_audio(audio.subclip(0, duration))
            final.write_videofile(
                final_output_path, fps=FPS, codec="h264_nvenc", audio_codec="aac",
                audio_fps=44100, bitrate="8000k", preset="fast", threads=4, logger=None
            )
            final.close()
            audio.close()
            bg_clip.close()

        return final_output_path

    except Exception as e:
        logger.error(f"Video pipeline failed: {e}", exc_info=True)
        return f"Error: {str(e)}"
