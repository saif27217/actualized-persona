#!/usr/bin/env python3
"""
Actualized Collection Search — Qdrant vector search only (no LLM).

Usage:
    python3 actualized_search.py "what is life"
    python3 actualized_search.py "suffering and letting go" --top-k 5
"""

import os
import sys
import argparse


def load_env():
    """Load env vars from ~/.hermes/.env"""
    env_path = os.path.expanduser("~/.hermes/.env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, val = line.split("=", 1)
                    os.environ.setdefault(key.strip(), val.strip())


def search(query: str, top_k: int = 8) -> list[dict]:
    """Search the actualized collection via Qdrant."""
    load_env()

    from qdrant_client import QdrantClient
    from nomic import embed

    url = os.environ.get("QDRANT_URL")
    api_key = os.environ.get("QDRANT_API_KEY")
    if not url or not api_key:
        print("ERROR: Set QDRANT_URL and QDRANT_API_KEY in ~/.hermes/.env", file=sys.stderr)
        sys.exit(1)

    client = QdrantClient(url=url, api_key=api_key)

    # Embed query using nomic (NOT httpx — SSL fails with direct API calls)
    output = embed.text(
        texts=[query],
        model="nomic-embed-text-v1.5",
        task_type="search_query"
    )
    vec = output["embeddings"][0]

    # Search Qdrant
    results = client.query_points(
        collection_name="actualized",
        query=vec,
        limit=top_k,
    )

    hits = []
    for hit in results.points:
        payload = hit.payload or {}
        text = payload.get("chunk_text", "") or payload.get("text", "") or ""
        source = payload.get("source_pdf", "") or payload.get("source", "")
        if source and "/" in source:
            source = source.split("/")[-1]
        hits.append({
            "text": text,
            "source": source,
            "score": round(hit.score, 4),
        })
    return hits


def main():
    parser = argparse.ArgumentParser(description="Search the Actualized.org transcript collection")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--top-k", type=int, default=8, help="Number of results (default: 8)")
    args = parser.parse_args()

    hits = search(args.query, args.top_k)

    for i, h in enumerate(hits, 1):
        print(f"--- Result {i} (score: {h['score']}) ---")
        if h["source"]:
            print(f"Source: {h['source']}")
        print(h["text"][:500])
        print()


if __name__ == "__main__":
    main()
