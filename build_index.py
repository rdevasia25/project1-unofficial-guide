"""
build_index.py — Entry point for the document ingestion and chunking pipeline.

Runs: load_documents() → chunk_records() → validation report + sample output.

Usage:
    python build_index.py
    python build_index.py --docs-dir path/to/documents
"""

import argparse
import sys
from collections import Counter

from chunker import chunk_records, text_hash
from ingest import load_documents

# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

_ARTIFACT_PATTERNS = [
    "Review:",        # uncleaned "Review: " prefix left in text body
    "Tags:",          # uncleaned "Tags: " line left in text body
    "&amp;",          # HTML entity
    "&nbsp;",
    "&lt;",
    "&gt;",
    "<div",           # HTML tag fragment
    "<span",
    "Load More",      # RMP boilerplate
    "Do Not Sell",    # footer boilerplate
    "Rate My Professors, LLC",
]


def _has_artifact(text: str) -> bool:
    lower = text.lower()
    for pat in _ARTIFACT_PATTERNS:
        if pat.lower() in lower:
            return True
    return False


def _validate(chunks: list[dict]) -> dict:
    issues = {
        "empty": [],
        "missing_metadata": [],
        "cleaning_artifacts": [],
        "duplicates": [],
    }

    seen_hashes: dict[str, str] = {}  # hash → chunk_id

    for c in chunks:
        cid = c["chunk_id"]
        text = c["text"]
        meta = c["metadata"]

        if not text.strip():
            issues["empty"].append(cid)

        if not meta.get("professor") and not meta.get("course"):
            issues["missing_metadata"].append(cid)

        # Check the body (the part after the first newline) for artifacts
        body = text.split("\n", 1)[1] if "\n" in text else text
        if _has_artifact(body):
            issues["cleaning_artifacts"].append(cid)

        h = text_hash(text)
        if h in seen_hashes:
            issues["duplicates"].append((cid, seen_hashes[h]))
        else:
            seen_hashes[h] = cid

    return issues


# ---------------------------------------------------------------------------
# Display helpers
# ---------------------------------------------------------------------------

def _print_sample_chunks(chunks: list[dict], n: int = 5) -> None:
    if not chunks:
        print("  (no chunks to display)")
        return

    step = max(1, len(chunks) // n)
    indices = [i * step for i in range(n) if i * step < len(chunks)]
    # Ensure last chunk is also shown if corpus is small
    if (len(chunks) - 1) not in indices:
        indices[-1] = len(chunks) - 1

    for i, idx in enumerate(indices, 1):
        c = chunks[idx]
        text = c["text"]
        display = text if len(text) <= 500 else text[:497] + "..."
        print(f"\n  [{i}/{n}] chunk_id={c['chunk_id']!r}  len={len(text)}")
        print("  " + "\n  ".join(display.splitlines()))


def _print_per_file_counts(chunks: list[dict]) -> None:
    counter: Counter = Counter()
    for c in chunks:
        counter[c["metadata"]["source_file"]] += 1
    for fname, count in sorted(counter.items()):
        print(f"  {fname}: {count} chunks")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(docs_dir: str = "documents") -> None:
    print("=" * 60)
    print("MILESTONE 3 — DOCUMENT PIPELINE INSPECTION")
    print("=" * 60)

    # ---- Ingestion ---------------------------------------------------------
    print("\n[1] Loading documents ...")
    records = load_documents(docs_dir)
    print(f"\n    Total records parsed: {len(records)}")

    if not records:
        print("ERROR: No records loaded. Check that documents/*.txt files exist.")
        sys.exit(1)

    # ---- Chunking ----------------------------------------------------------
    print("\n[2] Chunking records ...")
    chunks = chunk_records(records)
    print(f"\n    Total chunks produced: {len(chunks)}")

    if len(chunks) < 30:
        print("  WARNING: Fewer than 30 chunks — chunks may be too large or parsing failed.")
    if len(chunks) > 200:
        print("  WARNING: More than 200 chunks — chunks may be too small.")

    # ---- Per-file breakdown ------------------------------------------------
    print("\n[3] Chunks per source file:")
    _print_per_file_counts(chunks)

    # ---- Sample inspection -------------------------------------------------
    print(f"\n[4] Sample chunks (5 of {len(chunks)}):")
    _print_sample_chunks(chunks, n=5)

    # ---- Validation --------------------------------------------------------
    print("\n[5] Validation:")
    issues = _validate(chunks)

    empty_count = len(issues["empty"])
    missing_count = len(issues["missing_metadata"])
    artifact_count = len(issues["cleaning_artifacts"])
    dup_count = len(issues["duplicates"])

    print(f"    Empty chunks:          {empty_count}")
    print(f"    Missing metadata:      {missing_count}")
    print(f"    Cleaning artifacts:    {artifact_count}")
    print(f"    Duplicate chunks:      {dup_count}")

    if empty_count:
        print(f"  FAIL — empty chunk IDs: {issues['empty']}")
    if missing_count:
        print(f"  FAIL — missing metadata IDs: {issues['missing_metadata']}")
    if artifact_count:
        print(f"  WARN — artifact chunk IDs: {issues['cleaning_artifacts']}")
    if dup_count:
        print(f"  INFO — duplicate pairs (new_id, original_id): {issues['duplicates']}")

    total_issues = empty_count + missing_count + artifact_count
    print()
    if total_issues == 0:
        print("  All checks passed. Pipeline output looks clean.")
    else:
        print(f"  {total_issues} issue(s) found — review output above before proceeding to Milestone 4.")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run ingestion + chunking pipeline inspection.")
    parser.add_argument("--docs-dir", default="documents", help="Path to documents folder")
    args = parser.parse_args()
    main(docs_dir=args.docs_dir)
