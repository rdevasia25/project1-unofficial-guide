"""
embed.py — Embed chunks and store them in a persistent ChromaDB collection.

Public API:
    build_vector_store(docs_dir="documents", force_rebuild=True) -> int
"""

import argparse

import chromadb
from sentence_transformers import SentenceTransformer

from chunker import chunk_records
from ingest import load_documents

CHROMA_PATH = "./chroma_db"
COLLECTION_NAME = "vt_cs_reviews"
MODEL_NAME = "all-MiniLM-L6-v2"


def build_vector_store(docs_dir: str = "documents", force_rebuild: bool = True) -> int:
    """
    Load documents, chunk them, embed with all-MiniLM-L6-v2, and store in ChromaDB.

    Returns the number of chunks stored.
    """
    print("Loading and chunking documents...")
    records = load_documents(docs_dir)
    chunks = chunk_records(records)
    print(f"\nPrepared {len(chunks)} chunks for embedding.")

    if not chunks:
        raise ValueError("No chunks to embed. Run build_index.py first to verify ingestion.")

    print(f"Loading embedding model: {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)

    chunk_ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]

    print("Embedding chunks...")
    vectors = model.encode(texts, show_progress_bar=True)

    client = chromadb.PersistentClient(path=CHROMA_PATH)

    if force_rebuild:
        try:
            client.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'.")
        except (ValueError, chromadb.errors.NotFoundError):
            pass

    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )

    collection.add(
        ids=chunk_ids,
        embeddings=vectors.tolist(),
        documents=texts,
        metadatas=metadatas,
    )

    count = collection.count()
    print(f"\nStored {count} chunks in collection '{COLLECTION_NAME}' at {CHROMA_PATH}")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Embed chunks and build ChromaDB vector store.")
    parser.add_argument("--docs-dir", default="documents", help="Path to documents folder")
    parser.add_argument(
        "--force",
        action="store_true",
        default=True,
        help="Rebuild the collection from scratch (default: True)",
    )
    parser.add_argument(
        "--no-force",
        action="store_false",
        dest="force",
        help="Append to existing collection without deleting it",
    )
    args = parser.parse_args()
    build_vector_store(docs_dir=args.docs_dir, force_rebuild=args.force)
