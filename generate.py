"""
generate.py — Grounded response generation using Groq + retrieved context.

Public API:
    result = ask(question)
    # result["answer"]  -> str
    # result["sources"] -> list[str]  (deduplicated source filenames)
    # result["chunks"]  -> list[dict] (raw retrieve() output for inspection)
"""

import os

from dotenv import load_dotenv
from groq import Groq

from retrieve import retrieve

load_dotenv()

MODEL = "llama-3.3-70b-versatile"
TOP_K = 5

SYSTEM_PROMPT = (
    "You are an assistant that answers questions about CS professors at Virginia Tech "
    "using ONLY the student review documents provided below.\n\n"
    "Rules you must follow:\n"
    "1. Answer using only information explicitly stated in the provided documents. "
    "Do NOT use any outside knowledge or general assumptions about professors or courses.\n"
    "2. For every factual claim, cite the source file it came from using the format "
    "(Source: <filename>).\n"
    "3. If the provided documents do not contain enough information to answer the question, "
    'respond with exactly: "I don\'t have enough information in the provided reviews to '
    'answer that question."\n'
    "4. Do not speculate, extrapolate, or fill gaps with plausible-sounding guesses."
)


def _build_context(chunks: list[dict]) -> str:
    """Format retrieved chunks into a numbered context block for the LLM."""
    lines = []
    for chunk in chunks:
        meta = chunk["metadata"]
        header = (
            f"[{chunk['rank']}] Source: {meta.get('source_file', '')} "
            f"| Professor: {meta.get('professor', '')} "
            f"| Course: {meta.get('course', '')}"
        )
        # Strip the embedded metadata prefix from the chunk text to avoid duplication,
        # keeping just the review body (the part after the first newline).
        text = chunk["text"]
        body = text.split("\n", 1)[1].strip() if "\n" in text else text
        lines.append(f"{header}\n{body}")
    return "\n\n".join(lines)


def ask(question: str, k: int = TOP_K) -> dict:
    """
    Retrieve relevant chunks and generate a grounded answer.

    Returns:
        {
            "answer":  str           — LLM response grounded in retrieved text
            "sources": list[str]     — deduplicated source_file values (ordered)
            "chunks":  list[dict]    — raw retrieve() output for inspection
        }
    """
    chunks = retrieve(question, k=k)
    context = _build_context(chunks)

    user_message = f"Documents:\n\n{context}\n\nQuestion: {question}"

    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.2,
    )

    answer = response.choices[0].message.content.strip()

    # Build sources list programmatically — order of first appearance in chunks
    seen: set[str] = set()
    sources: list[str] = []
    for chunk in chunks:
        sf = chunk["metadata"].get("source_file", "")
        if sf and sf not in seen:
            seen.add(sf)
            sources.append(sf)

    return {"answer": answer, "sources": sources, "chunks": chunks}


# ---------------------------------------------------------------------------
# Evaluation harness — 5 questions from planning.md
# ---------------------------------------------------------------------------

EVAL_QUESTIONS = [
    (
        1,
        "Which professor do students recommend for CS1064, and how many hours per week "
        "do they say they spend on coursework outside of class?",
    ),
    (
        2,
        "Does Mohammed Farghally offer test retakes in CS2114 or CS3114?",
    ),
    (
        3,
        "What specific grading complaint do students raise about Margaret Ellis's CS2114 section?",
    ),
    (
        4,
        "Is Chris Thomas's CS5814 or CS5864 class an easy A?",
    ),
    (
        5,
        "How many reports are assigned in Amun Kharel's CS3724 (Intro to HCI), "
        "and is attendance mandatory?",
    ),
]


def _sep(char: str = "-", width: int = 60) -> str:
    return char * width


if __name__ == "__main__":
    print(_sep("="))
    print("MILESTONE 5 — GROUNDED GENERATION TEST")
    print(_sep("="))

    for qnum, question in EVAL_QUESTIONS:
        print(f"\nQ{qnum}: {question}")
        print(_sep())

        result = ask(question)

        print(f"Answer:\n{result['answer']}")
        print(f"\nRetrieved from: {', '.join(result['sources'])}")
        print(f"Chunks used: {[c['chunk_id'] for c in result['chunks']]}")
        print(f"\n[Grounding check: does this answer reference only the listed sources?]")
        print(_sep())

    print("\n" + _sep("="))
    print("Done. Review answers above for grounding and source attribution.")
    print(_sep("="))
