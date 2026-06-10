"""
retrieve.py — Semantic search over the ChromaDB vector store.

Public API:
    results = retrieve(query, k=5)   # list[dict]
"""

import argparse

import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "vt_cs_reviews"
MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5

_model: SentenceTransformer | None = None
_collection = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _get_collection():
    global _collection
    if _collection is None:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        _collection = client.get_collection(name=COLLECTION_NAME)
    return _collection


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Return the top-k most relevant chunks for a query string.

    Each result dict:
        {
            "rank": int,
            "chunk_id": str,
            "text": str,
            "metadata": dict,
            "distance": float,
        }
    """
    model = _get_model()
    collection = _get_collection()

    query_vec = model.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_vec,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )

    output = []
    ids = results["ids"][0]
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    for rank, (chunk_id, text, metadata, distance) in enumerate(
        zip(ids, documents, metadatas, distances), start=1
    ):
        output.append({
            "rank": rank,
            "chunk_id": chunk_id,
            "text": text,
            "metadata": metadata,
            "distance": distance,
        })

    return output


def _print_results(query: str, results: list[dict]) -> None:
    print(f"\nQuery: {query!r}")
    if not results:
        print("  (no results)")
        return

    for r in results:
        meta = r["metadata"]
        professor = meta.get("professor", "")
        course = meta.get("course", "")
        source_file = meta.get("source_file", "")
        text = r["text"]
        display = text if len(text) <= 400 else text[:397] + "..."
        print(f"\n  [{r['rank']}] dist={r['distance']:.4f}  chunk_id={r['chunk_id']!r}")
        print(f"      professor={professor!r}  course={course!r}  file={source_file!r}")
        print("      " + "\n      ".join(display.splitlines()))


def _check_relevance(query_id: int, results: list[dict]) -> tuple[bool, str]:
    """Return (pass, reason) for a retrieval test query."""
    if not results:
        return False, "no results returned"

    def _top_on_target() -> tuple[bool, float, dict]:
        top = results[0]
        meta = top["metadata"]
        professor = meta.get("professor", "").lower()
        course = meta.get("course", "").upper()
        text = top["text"].lower()
        dist = top["distance"]

        checks = {
            1: lambda: (
                ("lewis" in professor or "lewis" in text)
                and ("cs1064" in course or "cs1064" in text)
            ),
            2: lambda: (
                ("farghally" in professor or "farghally" in text)
                and ("retake" in text or "retakes" in text)
            ),
            3: lambda: False,  # handled separately below
        }

        relevant = checks.get(query_id, lambda: True)()
        return relevant, dist, meta

    if query_id == 3:
        # Planning.md: Thomas reviews mentioning difficulty should appear in top-k
        for r in results:
            meta = r["metadata"]
            professor = meta.get("professor", "").lower()
            course = meta.get("course", "").upper()
            text = r["text"].lower()
            if "thomas" in professor and ("5814" in course or "5864" in course):
                keywords = ("hard", "intense", "easy a", "math heavy", "difficult")
                if any(kw in text for kw in keywords):
                    dist_ok = r["distance"] < 0.65
                    if dist_ok:
                        return True, (
                            f"Thomas {course} chunk at rank {r['rank']} "
                            f"(dist={r['distance']:.4f})"
                        )
                    return False, f"Thomas found at rank {r['rank']} but dist={r['distance']:.4f} > 0.65"
        return False, "no Chris Thomas CS5814/CS5864 chunk in top-k"

    relevant, dist, meta = _top_on_target()
    dist_ok = dist < 0.5

    if relevant and dist_ok:
        return True, f"top result on-target (dist={dist:.4f})"
    if not relevant:
        professor = meta.get("professor", "")
        course = meta.get("course", "")
        return False, f"top result off-target: professor={professor!r}, course={course!r}"
    return False, f"distance too high: {dist:.4f} (threshold 0.5)"


# Evaluation queries from planning.md (first 3)
TEST_QUERIES = [
    (
        1,
        "Which professor do students recommend for CS1064, and how many hours per week "
        "do they say they spend on coursework outside of class?",
        "John Lewis / CS1064",
    ),
    (
        2,
        "Does Mohammed Farghally offer test retakes in CS2114 or CS3114?",
        "Farghally / test retakes",
    ),
    (
        3,
        "Is Chris Thomas's CS5814 or CS5864 class an easy A?",
        "Chris Thomas / not easy A",
    ),
]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test semantic retrieval against the vector store.")
    parser.add_argument("query", nargs="?", help="Optional single query string")
    parser.add_argument("-k", type=int, default=TOP_K, help="Number of results to return")
    args = parser.parse_args()

    if args.query:
        results = retrieve(args.query, k=args.k)
        _print_results(args.query, results)
    else:
        print("=" * 60)
        print("MILESTONE 4 — RETRIEVAL TEST")
        print("=" * 60)

        summary = []
        for qid, query, expected in TEST_QUERIES:
            results = retrieve(query, k=args.k)
            _print_results(query, results)
            passed, reason = _check_relevance(qid, results)
            summary.append((qid, expected, passed, reason))

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        all_pass = True
        for qid, expected, passed, reason in summary:
            status = "PASS" if passed else "FAIL"
            if not passed:
                all_pass = False
            print(f"  Query {qid} ({expected}): {status} — {reason}")

        if all_pass:
            print("\nAll retrieval tests passed. Ready for Milestone 5.")
        else:
            print("\nSome retrieval tests failed — review results above before proceeding.")
