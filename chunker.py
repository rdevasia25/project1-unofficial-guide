"""
chunk.py — Convert parsed records into self-contained, embedding-ready chunk dicts.

Chunking strategy (from planning.md):
  - One record = one chunk under normal conditions.
  - Every chunk body is prefixed with a metadata header so it is self-attributing
    even when retrieved in isolation.
  - Fallback: review text bodies longer than LONG_REVIEW_CHARS are split into
    overlapping windows before the prefix is applied.

Public API:
    chunks = chunk_records(records)   # list[dict]
"""

import hashlib
import re

# Threshold above which a review body is split into overlapping sub-chunks
LONG_REVIEW_CHARS = 800
WINDOW_SIZE = 512
WINDOW_OVERLAP = 64


# ---------------------------------------------------------------------------
# Metadata prefix builders
# ---------------------------------------------------------------------------

def _rmp_prefix(rec: dict) -> str:
    """Build the metadata header line for a Rate My Professors review chunk."""
    parts = [
        f"Source: {rec['source']}",
        f"Professor: {rec['professor']}",
        f"Course: {rec['course']}",
        f"File: {rec['source_file']}",
    ]
    if rec.get("quality"):
        parts.append(f"Quality: {rec['quality']}/5")
    if rec.get("difficulty"):
        parts.append(f"Difficulty: {rec['difficulty']}/5")
    return "[" + " | ".join(parts) + "]"


def _coursicle_review_prefix(rec: dict) -> str:
    """Build the metadata header line for a Coursicle review chunk."""
    parts = [
        f"Source: {rec['source']}",
        f"Professor: {rec['professor']}",
        f"Course: {rec['course']}",
        f"File: {rec['source_file']}",
    ]
    return "[" + " | ".join(parts) + "]"


def _coursicle_desc_prefix(rec: dict) -> str:
    """Build the metadata header line for a Coursicle course-description chunk."""
    parts = [
        f"Source: {rec['source']}",
        f"Course: {rec['course']}",
        f"File: {rec['source_file']}",
    ]
    return "[" + " | ".join(parts) + "]"


def _build_prefix(rec: dict) -> str:
    if rec["record_type"] == "course_description":
        return _coursicle_desc_prefix(rec)
    if rec["source"].lower().startswith("coursicle"):
        return _coursicle_review_prefix(rec)
    return _rmp_prefix(rec)


# ---------------------------------------------------------------------------
# Splitting helpers
# ---------------------------------------------------------------------------

def _split_long_text(text: str, window: int = WINDOW_SIZE, overlap: int = WINDOW_OVERLAP) -> list[str]:
    """
    Split a text string into overlapping windows of `window` characters with
    `overlap` characters of shared context between adjacent windows.
    Each window is stripped and non-empty.
    """
    if len(text) <= window:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + window
        segment = text[start:end].strip()
        if segment:
            chunks.append(segment)
        if end >= len(text):
            break
        start = end - overlap  # backtrack by overlap for next window

    return chunks


# ---------------------------------------------------------------------------
# Chunk ID helper
# ---------------------------------------------------------------------------

def _make_chunk_id(source_file: str, index: int) -> str:
    stem = source_file.replace(".txt", "").replace("-", "_")
    return f"{stem}_{index}"


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def chunk_records(records: list[dict]) -> list[dict]:
    """
    Convert a list of ingest records into a list of chunk dicts.

    Each chunk dict:
        {
            "chunk_id":  str,   e.g. "john_lewis_rmp_0"
            "text":      str,   metadata prefix + newline + review body
            "metadata":  dict,  professor, course, source, source_url,
                                source_file, record_type
        }
    """
    chunks: list[dict] = []
    chunk_index = 0

    for rec in records:
        body = rec["text"].strip()
        if not body:
            continue

        prefix = _build_prefix(rec)
        metadata = {
            "professor": rec["professor"],
            "course": rec["course"],
            "source": rec["source"],
            "source_url": rec["source_url"],
            "source_file": rec["source_file"],
            "record_type": rec["record_type"],
        }

        if len(body) > LONG_REVIEW_CHARS:
            # Fallback: split into overlapping windows, each with the same prefix
            sub_bodies = _split_long_text(body)
        else:
            sub_bodies = [body]

        for sub_body in sub_bodies:
            full_text = f"{prefix}\n{sub_body}"
            chunks.append({
                "chunk_id": _make_chunk_id(rec["source_file"], chunk_index),
                "text": full_text,
                "metadata": metadata,
            })
            chunk_index += 1

    return chunks


def text_hash(text: str) -> str:
    """Return a short hash of a string (used for duplicate detection)."""
    return hashlib.md5(text.encode()).hexdigest()[:12]


if __name__ == "__main__":
    from ingest import load_documents

    print("Loading documents...")
    records = load_documents()
    print(f"Parsed {len(records)} records")

    chunks = chunk_records(records)
    print(f"Produced {len(chunks)} chunks")

    print("\nFirst 3 chunks:")
    for c in chunks[:3]:
        print(f"\n  [{c['chunk_id']}]\n  {c['text'][:300]}{'...' if len(c['text']) > 300 else ''}")
