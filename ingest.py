"""
ingest.py — Load and parse all document files into structured review records.

Two file formats are supported:
  - *_rmp.txt      Rate My Professors professor pages
  - *_coursicle.txt  Coursicle course pages

Public API:
    records = load_documents("documents")   # list[dict]
"""

import re
from pathlib import Path


# ---------------------------------------------------------------------------
# Header parsing (shared by both formats)
# ---------------------------------------------------------------------------

def _parse_file_header(text: str) -> dict:
    """Extract key: value pairs from the top of a file (before the first --- line)."""
    result = {}
    for line in text.splitlines():
        if line.startswith("---"):
            break
        if ":" in line:
            key, _, value = line.partition(":")
            result[key.strip().lower().replace(" ", "_")] = value.strip()
    return result


# ---------------------------------------------------------------------------
# RMP parser
# ---------------------------------------------------------------------------

def _parse_rmp(path: Path) -> list[dict]:
    """Parse a Rate My Professors .txt file into one record per review block."""
    text = path.read_text(encoding="utf-8")

    # Split header from review body on the --- Reviews --- separator
    if "--- Reviews ---" not in text:
        return []
    header_text, reviews_text = text.split("--- Reviews ---", 1)

    header = _parse_file_header(header_text)
    professor = header.get("professor", "")
    source_url = header.get("url", "")
    source = header.get("source", "Rate My Professors")

    records = []
    # Individual review blocks are separated by one or more blank lines
    blocks = re.split(r"\n{2,}", reviews_text.strip())

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()
        first_line = lines[0] if lines else ""

        # Skip blocks that are not actual reviews (e.g. stray separator text)
        if not re.search(r"^Course:", first_line):
            continue

        # Extract fields from the first "Course: ... | Date: ... | Quality: ... | Difficulty: ..." line
        course_m = re.search(r"Course:\s*(\S+)", first_line)
        date_m = re.search(r"Date:\s*([^|]+)", first_line)
        quality_m = re.search(r"Quality:\s*([\d.]+)", first_line)
        difficulty_m = re.search(r"Difficulty:\s*([\d.]+)", first_line)

        course = course_m.group(1) if course_m else ""
        date = date_m.group(1).strip() if date_m else ""
        quality = quality_m.group(1) if quality_m else ""
        difficulty = difficulty_m.group(1) if difficulty_m else ""

        # Find the Review: line (may not be the last line — Tags: can follow)
        review_text = ""
        for line in lines:
            if line.startswith("Review:"):
                review_text = line[len("Review:"):].strip()
                break

        if not review_text:
            continue

        # Strip inline Tags that were written on the same line ("... Tags: Amazing lectures")
        review_text = re.sub(r"\s+Tags:.*$", "", review_text, flags=re.IGNORECASE).strip()

        records.append({
            "professor": professor,
            "course": course,
            "source": source,
            "source_url": source_url,
            "source_file": path.name,
            "date": date,
            "quality": quality,
            "difficulty": difficulty,
            "text": review_text,
            "record_type": "review",
        })

    return records


# ---------------------------------------------------------------------------
# Coursicle parser
# ---------------------------------------------------------------------------

def _extract_section(text: str, start_marker: str) -> str:
    """Return the text between start_marker and the next '--- ' section marker (or end of file)."""
    pattern = re.escape(start_marker) + r"\s*\n(.*?)(?=\n--- |\Z)"
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1).strip() if m else ""


def _parse_coursicle(path: Path) -> list[dict]:
    """Parse a Coursicle .txt file into one course-description record plus one per review."""
    text = path.read_text(encoding="utf-8")

    header = _parse_file_header(text)
    source_url = header.get("url", "")
    source = header.get("source", "Coursicle")
    # "Course: CS1064 - Intro to Programming in Python"
    course_full = header.get("course", "")

    # Shortest course code prefix (e.g. "CS1064")
    code_m = re.match(r"(CS\d+)", course_full)
    course_code = code_m.group(1) if code_m else course_full

    records = []

    # ---- Course description ------------------------------------------------
    desc_text = _extract_section(text, "--- Course Description ---")
    if desc_text:
        records.append({
            "professor": "",
            "course": course_full,
            "source": source,
            "source_url": source_url,
            "source_file": path.name,
            "date": "",
            "quality": "",
            "difficulty": "",
            "text": desc_text,
            "record_type": "course_description",
        })

    # ---- Review sections ---------------------------------------------------
    # Merge "Sample Reviews" and "Notes from additional Coursicle reviews" into one stream
    review_pool = ""
    review_pool += "\n\n" + _extract_section(text, "--- Sample Reviews ---")
    notes = _extract_section(text, "--- Notes from additional Coursicle reviews ---")
    if notes:
        review_pool += "\n\n" + notes

    blocks = re.split(r"\n{2,}", review_pool.strip())

    for block in blocks:
        block = block.strip()
        if not block:
            continue

        lines = block.splitlines()

        # Must have both a Professor: line and a Review: line
        prof_line = next((l for l in lines if l.startswith("Professor:")), None)
        rev_line = next((l for l in lines if l.startswith("Review:")), None)

        if not prof_line or not rev_line:
            # Skip metadata lines like "Recent professors..." and "Cons noted..."
            continue

        # Professor name is the part before " | Student:" (or the whole thing)
        prof_m = re.match(r"Professor:\s*([^|]+)", prof_line)
        professor = prof_m.group(1).strip() if prof_m else ""

        review_text = rev_line[len("Review:"):].strip()

        if not review_text:
            continue

        records.append({
            "professor": professor,
            "course": course_code,
            "source": source,
            "source_url": source_url,
            "source_file": path.name,
            "date": "",
            "quality": "",
            "difficulty": "",
            "text": review_text,
            "record_type": "review",
        })

    return records


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

def load_documents(docs_dir: str = "documents") -> list[dict]:
    """
    Walk docs_dir/*.txt, parse each file, and return a flat list of records.
    Prints a per-file summary line to stdout.
    """
    docs_path = Path(docs_dir)
    all_records: list[dict] = []

    for txt_file in sorted(docs_path.glob("*.txt")):
        if txt_file.name.endswith("_rmp.txt"):
            records = _parse_rmp(txt_file)
        elif txt_file.name.endswith("_coursicle.txt"):
            records = _parse_coursicle(txt_file)
        else:
            continue  # skip sources.md and any unrecognised files

        print(f"  {txt_file.name}: {len(records)} records")
        all_records.extend(records)

    return all_records


if __name__ == "__main__":
    print("Loading documents...")
    recs = load_documents()
    print(f"\nTotal records: {len(recs)}")
    if recs:
        print("\nFirst record sample:")
        for k, v in recs[0].items():
            print(f"  {k}: {v!r}")
