"""
evaluate.py — Run all 5 evaluation questions and print a detailed report.

Usage:
    python evaluate.py
    python evaluate.py --json   # machine-readable output
"""

import argparse
import json

from generate import ask

EVAL_QUESTIONS = [
    {
        "id": 1,
        "question": (
            "Which professor do students recommend for CS1064, and how many hours per week "
            "do they say they spend on coursework outside of class?"
        ),
        "expected": (
            "John Lewis. Reviews say CS1064 is not very difficult if you spend roughly "
            "1–3 hours outside of class; Lewis is praised for clear assignments and accessibility."
        ),
    },
    {
        "id": 2,
        "question": "Does Mohammed Farghally offer test retakes in CS2114 or CS3114?",
        "expected": (
            "Yes. Multiple reviews state he offers free test retakes. CS3114 reviews also "
            "mention a 10% bonus for turning projects in early."
        ),
    },
    {
        "id": 3,
        "question": "What specific grading complaint do students raise about Margaret Ellis's CS2114 section?",
        "expected": (
            "Students report that TAs grade very slowly — grades can drop from an A to a "
            "B-/C+ over several weeks. Negative reviews also cite heavy classwork and unclear instructions."
        ),
    },
    {
        "id": 4,
        "question": "Is Chris Thomas's CS5814 or CS5864 class an easy A?",
        "expected": (
            "No. Reviews describe math-heavy courses with intense exams and homework. Students "
            "say 'if you want easy A take someone else' and 'No easy A by any means.'"
        ),
    },
    {
        "id": 5,
        "question": (
            "How many reports are assigned in Amun Kharel's CS3724 (Intro to HCI), "
            "and is attendance mandatory?"
        ),
        "expected": (
            "4 group reports and 1 personal report. Reviews state attendance is mandatory "
            "in some sections; Kharel is flexible with extensions."
        ),
    },
]


def run_evaluation() -> list[dict]:
    results = []
    for item in EVAL_QUESTIONS:
        result = ask(item["question"])
        chunks_summary = [
            {
                "rank": c["rank"],
                "chunk_id": c["chunk_id"],
                "distance": round(c["distance"], 4),
                "professor": c["metadata"].get("professor", ""),
                "course": c["metadata"].get("course", ""),
                "source_file": c["metadata"].get("source_file", ""),
                "preview": c["text"].split("\n", 1)[-1][:150],
            }
            for c in result["chunks"]
        ]
        results.append({
            "id": item["id"],
            "question": item["question"],
            "expected": item["expected"],
            "answer": result["answer"],
            "sources": result["sources"],
            "chunks": chunks_summary,
        })
    return results


def print_report(results: list[dict]) -> None:
    print("=" * 70)
    print("EVALUATION REPORT — VT CS Professor Unofficial Guide")
    print("=" * 70)

    for r in results:
        print(f"\nQ{r['id']}: {r['question']}")
        print("-" * 70)
        print(f"Expected: {r['expected']}")
        print(f"\nSystem response:\n{r['answer']}")
        print(f"\nSources: {', '.join(r['sources'])}")
        print("Retrieved chunks:")
        for c in r["chunks"]:
            print(
                f"  [{c['rank']}] dist={c['distance']} "
                f"{c['source_file']} | {c['professor']} | {c['course']}"
            )
            print(f"       {c['preview']}...")
        print("-" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run evaluation questions through the full RAG pipeline.")
    parser.add_argument("--json", action="store_true", help="Print results as JSON")
    args = parser.parse_args()

    results = run_evaluation()
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print_report(results)
