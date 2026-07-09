"""
Caption Sync Engine — Whisper-based word-level timestamp generation
Uses faster-whisper for efficient transcription with word timestamps.
"""
import os
# Fix OpenMP duplicate library crash on Windows (numpy + torch conflict)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import re
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Hindi/Devanagari Unicode range detection
DEVANAGARI_PATTERN = re.compile(r'[\u0900-\u097F]')


def is_hindi(text: str) -> bool:
    """Check if text contains Devanagari characters."""
    return bool(DEVANAGARI_PATTERN.search(text))


def detect_language(text: str) -> str:
    """Detect if text is Hindi or English."""
    return "hi" if is_hindi(text) else "en"


def transcribe_audio(audio_path: str) -> list[dict]:
    """
    Transcribe audio using faster-whisper and return word-level timestamps.

    Returns list of caption segments:
    [
        {"start": 0.0, "end": 1.5, "text": "Sach kadwa hota hai", "lang": "hi",
         "words": [{"word": "Sach", "start": 0.0, "end": 0.4}, ...]},
        ...
    ]
    """
    from faster_whisper import WhisperModel

    if not os.path.exists(audio_path):
        logger.error(f"Audio file not found: {audio_path}")
        return []

    logger.info(f"Transcribing: {audio_path}")

    # Use base model for speed + accuracy balance
    model = WhisperModel("base", device="cpu", compute_type="int8")

    segments, info = model.transcribe(
        audio_path,
        word_timestamps=True,
        language="en",  # Force English to prevent Urdu/Arabic script output
        vad_filter=True, # Prevent hallucinating pauses into word durations
    )

    captions = []
    for segment in segments:
        text = segment.text.strip()
        # Segment-level detection
        seg_lang = detect_language(text)
        
        words = []
        if segment.words:
            for w in segment.words:
                word_text = w.word.strip()
                # Use segment lang, but if mixed, maybe re-detect? 
                # For safety/speed, inherit segment lang unless word is clearly Devanagari
                word_lang = "hi" if is_hindi(word_text) else seg_lang
                
                word_obj = {
                    "word": word_text,
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "lang": word_lang
                }
                words.append(word_obj)
                logger.debug(f"Word: {word_text} | {word_lang} | {word_obj['start']}-{word_obj['end']}")

        captions.append({
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": text,
            "lang": seg_lang,
            "words": words,
        })
    
    logger.info(f"Transcription complete: {len(captions)} segments, detected language: {info.language}")
    return captions


def generate_srt(captions: list[dict], output_path: str) -> str:
    """
    Generate an SRT subtitle file from caption segments.
    Returns the output file path.
    """
    def format_time(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

    lines = []
    for i, cap in enumerate(captions, 1):
        lines.append(str(i))
        lines.append(f"{format_time(cap['start'])} --> {format_time(cap['end'])}")
        lines.append(cap['text'])
        lines.append("")

    srt_content = "\n".join(lines)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(srt_content)

    logger.info(f"SRT saved: {output_path}")
    return output_path


def create_fallback_captions(script_text: str, audio_duration: float) -> list[dict]:
    """
    Create evenly-spaced captions from script text when Whisper is unavailable.
    Splits text into chunks and distributes across the audio duration.
    """
    import textwrap

    # Split into sentences
    sentences = re.split(r'[.!?…]+', script_text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if not sentences:
        return [{"start": 0.0, "end": audio_duration, "text": script_text, "lang": detect_language(script_text), "words": []}]

    # Distribute evenly across duration
    segment_duration = audio_duration / len(sentences)
    captions = []

    for i, sentence in enumerate(sentences):
        start = round(i * segment_duration, 3)
        end = round((i + 1) * segment_duration, 3)
        lang = detect_language(sentence)

        # Create simple word list (no real timestamps, evenly spaced)
        words_list = sentence.split()
        word_dur = (end - start) / max(len(words_list), 1)
        words = []
        for j, word in enumerate(words_list):
            words.append({
                "word": word,
                "start": round(start + j * word_dur, 3),
                "end": round(start + (j + 1) * word_dur, 3),
            })

        captions.append({
            "start": start,
            "end": end,
            "text": sentence,
            "lang": lang,
            "words": words,
        })

    return captions
