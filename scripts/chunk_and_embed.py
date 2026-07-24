"""
scripts/chunk_and_embed.py
──────────────────────────────────────────────────────────────────────
Takes the scraped .txt files, splits them into overlapping chunks,
and saves a JSON file of all chunks with metadata.

Run after scrape_site.py:
    python scripts/chunk_and_embed.py

Output:
    data/crushaders_tech/processed/chunks.json
──────────────────────────────────────────────────────────────────────
"""

import os
import json
import re
from datetime import datetime, timezone

WEBSITE_ID  = "crushaders_tech"
BASE_URL    = "https://crushaderstech.com"
RAW_DIR     = os.path.join("data", WEBSITE_ID, "raw")
OUTPUT_DIR  = os.path.join("data", WEBSITE_ID, "processed")
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "chunks.json")

# ── Chunking parameters ───────────────────────────────────────────────
# CHUNK_SIZE: target character count per chunk
# Too large → vague vector that doesn't match specific questions
# Too small → not enough context for the LLM to give a useful answer
# 450 chars ≈ 80-100 words — the sweet spot for service/about text
CHUNK_SIZE    = 450
CHUNK_OVERLAP = 80   # last 80 chars of chunk N become start of chunk N+1
                     # prevents cutting sentences mid-meaning

# Maps filename prefix to page_type metadata value
PAGE_TYPE_MAP = {
    "home":               "home",
    "about":              "about",
    "service_":           "service",
    "industry_":          "industry",
    "contact":            "contact",
    "blog":               "blog",
    "faq":                "faq",
}

# Maps filename to the URL that will appear in the "sources" field
URL_MAP = {
    "home":                  "https://crushaderstech.com/",
    "about":                 "https://crushaderstech.com/about",
    "service_content":       "https://crushaderstech.com/content-creation",
    "service_branding":      "https://crushaderstech.com/digital-branding",
    "service_ecommerce":     "https://crushaderstech.com/e-commerce-solutions",
    "service_lead_gen":      "https://crushaderstech.com/lead-generation",
    "service_celebrity":     "https://crushaderstech.com/celebrity-profile-management",
    "service_orm":           "https://crushaderstech.com/online-reputation-management",
    "service_political":     "https://crushaderstech.com/political-campaign-management",
    "industry_education":    "https://crushaderstech.com/education",
    "industry_realestate":   "https://crushaderstech.com/real-estate",
    "industry_healthcare":   "https://crushaderstech.com/healthcare",
    "industry_hospitality":  "https://crushaderstech.com/hospitality-tourism",
    "industry_jewellery":    "https://crushaderstech.com/jewellery-watches",
    "industry_manufact":     "https://crushaderstech.com/manufacturing",
    "contact":               "https://crushaderstech.com/contacts",
    "blogs":                 "https://crushaderstech.com/blogs",
}


def get_page_type(filename: str) -> str:
    """Infer page_type from filename using the prefix map."""
    for prefix, ptype in PAGE_TYPE_MAP.items():
        if filename.startswith(prefix):
            return ptype
    return "general"


def get_url(filename: str) -> str:
    """Get the source URL for this filename."""
    return URL_MAP.get(filename, f"{BASE_URL}/{filename}")


def split_into_chunks(text: str) -> list[str]:
    """
    Split text into overlapping chunks of approximately CHUNK_SIZE characters.

    Strategy: RecursiveCharacterSplitting (manual implementation)
    We try to split on sentence boundaries (". ") first, then on spaces.
    This avoids cutting words or sentences mid-way.

    Example with CHUNK_SIZE=20, OVERLAP=5:
    Text:   "Hello world. This is a test. More text here."
    Chunk1: "Hello world. This is"
    Chunk2: "s is a test. More te"  ← starts 5 chars before chunk1 ended
    Chunk3: "More text here."
    """
    chunks = []
    start = 0
    text_len = len(text)

    while start < text_len:
        end = start + CHUNK_SIZE

        if end >= text_len:
            # We've reached the end — take whatever remains
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break

        # Try to find a natural break point near the end of this chunk
        # Prefer breaking at ". " (sentence end), then " " (word end)
        slice_text = text[start:end]

        # Look for the last period+space within the chunk
        last_period = slice_text.rfind(". ")
        if last_period > CHUNK_SIZE // 2:
            # Found a sentence boundary in the second half of the chunk
            actual_end = start + last_period + 2  # include the ". "
        else:
            # No good sentence break — break at last space
            last_space = slice_text.rfind(" ")
            if last_space > 0:
                actual_end = start + last_space
            else:
                actual_end = end  # no space found, hard cut

        chunk = text[start:actual_end].strip()
        if chunk:
            chunks.append(chunk)

        # Next chunk starts CHUNK_OVERLAP characters before this chunk ended
        # This creates the overlap — the "bridge" between consecutive chunks
        start = actual_end - CHUNK_OVERLAP

    return chunks


def process_file(filename: str, text: str) -> list[dict]:
    """
    Split one page's text into chunks and attach metadata to each chunk.
    Returns a list of chunk dicts ready to be saved and later embedded.
    """
    chunks_text = split_into_chunks(text)
    page_type   = get_page_type(filename)
    source_url  = get_url(filename)
    scraped_at  = datetime.now(timezone.utc).isoformat()

    chunk_records = []
    for i, chunk_text in enumerate(chunks_text):
        # Skip chunks that are too short to be useful
        # (often navigation remnants or section headers alone)
        if len(chunk_text) < 60:
            continue

        chunk_records.append({
            # ── Multi-tenancy key (THE most important field) ──────────
            "website_id":   WEBSITE_ID,

            # ── Source tracing ────────────────────────────────────────
            "url":          source_url,
            "page_title":   filename.replace("_", " ").title(),
            "page_type":    page_type,
            "doc_type":     "website_public",

            # ── The actual content (what the LLM reads) ───────────────
            "chunk_text":   chunk_text,

            # ── Ordering and debugging ────────────────────────────────
            "chunk_index":  i,
            "char_count":   len(chunk_text),

            # ── Freshness tracking ────────────────────────────────────
            "scraped_at":   scraped_at,
        })

    return chunk_records


def main():
    print(f"\n{'='*60}")
    print(f"  Chunking: {WEBSITE_ID}")
    print(f"  Source:   {RAW_DIR}")
    print(f"  Chunk size: {CHUNK_SIZE} chars, overlap: {CHUNK_OVERLAP}")
    print(f"{'='*60}\n")

    all_chunks = []
    txt_files  = [f for f in os.listdir(RAW_DIR) if f.endswith(".txt")]

    for txt_file in sorted(txt_files):
        filename = txt_file.replace(".txt", "")
        filepath = os.path.join(RAW_DIR, txt_file)

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        chunks = process_file(filename, text)
        all_chunks.extend(chunks)

        print(f"  ✓  {txt_file:35s}  →  {len(chunks):3d} chunks")

    # Save all chunks to JSON
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  Total chunks: {len(all_chunks)}")
    print(f"  Saved to:     {OUTPUT_FILE}")
    print(f"{'='*60}\n")

    # Print a sample chunk so you can verify it looks correct
    if all_chunks:
        print("  Sample chunk:")
        sample = all_chunks[0]
        for key, val in sample.items():
            if key == "chunk_text":
                print(f"    {key}: {val[:100]}...")
            else:
                print(f"    {key}: {val}")


if __name__ == "__main__":
    main()