from google import genai
from google.genai import types
import os
import io
import json
import time
import logging
from typing import List, Dict
from pathlib import Path
from dotenv import load_dotenv
from PyPDF2 import PdfReader

env_path = Path(__file__).resolve().parent.parent / '.env'
if not env_path.exists():
    env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

api_key = os.getenv("GEMINI_API_KEY")

logger = logging.getLogger("IngestionEngine")

# ── Step 1: Extract raw text from PDF locally (FREE, no API) ────

def extract_text_from_pdf(pdf_bytes: bytes) -> List[str]:
    """Extract text from each page of a PDF using PyPDF2. Returns a list of page texts."""
    reader = PdfReader(io.BytesIO(pdf_bytes))
    pages = []
    for page in reader.pages:
        text = page.extract_text() or ""
        if text.strip():
            pages.append(text.strip())
    logger.info(f"Extracted text from {len(pages)} non-empty pages (out of {len(reader.pages)} total)")
    return pages

# ── Step 2: Chunk pages into groups ─────────────────────────────

def chunk_pages(pages: List[str], pages_per_chunk: int = 5) -> List[str]:
    """Group page texts into larger chunks for batch API calls."""
    chunks = []
    for i in range(0, len(pages), pages_per_chunk):
        batch = pages[i:i + pages_per_chunk]
        combined = "\n\n--- PAGE BREAK ---\n\n".join(batch)
        chunks.append(combined)
    logger.info(f"Created {len(chunks)} chunks ({pages_per_chunk} pages each)")
    return chunks

# ── Step 3: Extract quotes from a single text chunk via Gemini ──

EXTRACTION_PROMPT = """
You are a meticulous archivist and expert in ancient Indian philosophy, specializing in Chanakya Neeti.
Analyze the following text (extracted from a PDF) and extract ALL Chanakya Neeti verses/quotes you can find.

For each quote found, return:
1. "text": The original Sanskrit/Hindi/English text of the quote.
2. "translation": An English translation of the quote.
3. "meaning": A one-sentence modern interpretation.
4. "tags": Comma-separated relevant keywords.

Rules:
- Extract EVERY quote you can find, do not skip any.
- If a quote spans multiple lines, combine them.
- Ignore chapter headings, page numbers, and commentary that are NOT quotes.
- If you find no quotes in this chunk, return an empty list [].

Return ONLY a valid JSON array:
[
  {"text": "...", "translation": "...", "meaning": "...", "tags": "..."}
]

TEXT TO ANALYZE:
"""

def extract_quotes_from_chunk(text_chunk: str) -> List[Dict]:
    """Send a single text chunk to Gemini for quote extraction."""
    if not api_key:
        return []

    client = genai.Client(api_key=api_key)
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[EXTRACTION_PROMPT + text_chunk],
            config=types.GenerateContentConfig(response_mime_type="application/json")
        )
        
        raw_text = response.text
        start = raw_text.find('[')
        end = raw_text.rfind(']')
        if start != -1 and end != -1:
            clean_text = raw_text[start:end+1]
        else:
            clean_text = raw_text
            
        data = json.loads(clean_text)
        if isinstance(data, list):
            return data
        return data.get("quotes", [])
        
    except Exception as e:
        logger.error(f"Gemini extraction error for chunk: {e}")
        return []

# ── Step 4: Orchestrate the full chunked pipeline ───────────────

def extract_quotes_chunked(pdf_bytes: bytes, pages_per_chunk: int = 5) -> List[Dict]:
    """
    Full pipeline (non-streaming version):
    1. Extract text from PDF locally (free)
    2. Split into chunks
    3. Send each chunk to Gemini
    4. Deduplicate and return all quotes
    """
    all_quotes = []
    for progress, status, quotes in extract_quotes_chunked_with_progress(pdf_bytes, pages_per_chunk):
        all_quotes = quotes
    return all_quotes

def extract_quotes_chunked_with_progress(pdf_bytes: bytes, pages_per_chunk: int = 5):
    """
    Generator that yields (progress_pct, status_msg, quotes_so_far) tuples.
    Used by the streaming endpoint for real-time progress updates.
    """
    logger.info("Starting chunked PDF extraction pipeline...")
    
    # Step 1: Local text extraction
    yield (5, "Extracting text from PDF...", [])
    pages = extract_text_from_pdf(pdf_bytes)
    if not pages:
        logger.warning("No text could be extracted from the PDF")
        yield (100, "No text found in PDF", [])
        return
    
    yield (10, f"Found {len(pages)} pages with text. Splitting into chunks...", [])
    
    # Step 2: Chunk
    chunks = chunk_pages(pages, pages_per_chunk)
    
    # Step 3: Process each chunk through Gemini
    all_quotes = []
    for i, chunk in enumerate(chunks):
        # Progress: 10% to 90% is the Gemini processing range
        chunk_progress = 10 + int((i / len(chunks)) * 80)
        yield (chunk_progress, f"Processing chunk {i+1} of {len(chunks)}...", list(all_quotes))
        
        logger.info(f"Processing chunk {i+1}/{len(chunks)}...")
        quotes = extract_quotes_from_chunk(chunk)
        logger.info(f"  → Extracted {len(quotes)} quotes from chunk {i+1}")
        all_quotes.extend(quotes)
        
        # Small delay between API calls to avoid rate limiting
        if i < len(chunks) - 1:
            time.sleep(1)
    
    # Step 4: Deduplicate by text content
    yield (92, "Deduplicating quotes...", list(all_quotes))
    seen_texts = set()
    unique_quotes = []
    for q in all_quotes:
        text = q.get("text", "").strip()
        if text and text not in seen_texts:
            seen_texts.add(text)
            unique_quotes.append(q)
    
    logger.info(f"Pipeline complete: {len(unique_quotes)} unique quotes extracted (from {len(all_quotes)} raw)")
    yield (100, f"Done! Extracted {len(unique_quotes)} unique quotes.", unique_quotes)

# ── Legacy single-shot function (kept for backward compat) ──────

def extract_quotes_from_pdf(pdf_bytes: bytes) -> List[Dict]:
    """Legacy: delegates to the chunked pipeline."""
    return extract_quotes_chunked(pdf_bytes)
