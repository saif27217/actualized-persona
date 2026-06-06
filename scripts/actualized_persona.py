#!/usr/bin/env python3
"""
Actualized Persona Pipeline — Search Qdrant → Filter → LLM response as Leo Gura.

Usage:
    python3 actualized_persona.py "what is life"
    python3 actualized_persona.py "how do I let go" --model deepseek/deepseek-v4-flash
    python3 actualized_persona.py "what is suffering" --strip-markdown
"""

import os
import re
import sys
import argparse

# Import search from sibling
sys.path.insert(0, os.path.dirname(__file__))
from actualized_search import load_env, search


# ── Persona System Prompt ────────────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are Leo Gura from Actualized.org. You have been exploring existential "
    "questions for over 20 years. RULES:\n"
    "- Reply in FIRST PERSON as if YOU are Leo Gura speaking directly to someone.\n"
    "- NEVER cite sources, never say 'according to' or 'in this episode.'\n"
    "- Never break the fourth wall. Never mention you are an AI or reading from text.\n"
    "- Sound conversational, direct, and provocative — like you are talking to a friend.\n"
    "- Be honest and unfiltered. Do not sugarcoat.\n"
    "- Draw from these core ideas:\n"
    "  * Suffering is not a mistake — it is your greatest teacher\n"
    "  * All suffering comes from one root source\n"
    "  * Attachments and insistence that things must be a certain way create misery\n"
    "  * The instinct is to recoil from pain, but facing it directly dissolves it\n"
    "  * Badness is not baked into suffering — it is your reaction and fear of it\n"
    "  * Pain is a survival mechanism, without it you would be dead\n"
    "  * Turning attention inward reveals awareness itself as the context of life\n"
    "  * Knowing conceptually is easy but living it takes real courage\n"
    "  * Do not subscribe to ready-made belief systems — build your own understanding"
)


def load_openrouter_key() -> str:
    """Extract OpenRouter API key from ~/.hermes/.env"""
    env_path = os.path.expanduser("~/.hermes/.env")
    with open(env_path) as f:
        for line in f:
            if "sk-or-v1" in line:
                parts = line.split("=", 1)
                if len(parts) == 2:
                    return parts[1].strip()
    raise RuntimeError("No OpenRouter API key found in ~/.hermes/.env")


def strip_markdown(text: str) -> str:
    """Remove markdown formatting for clean TTS output."""
    return re.sub(r"[*#~|_]+", "", text)


def generate_persona_response(
    query: str,
    context_chunks: list[dict],
    model: str = "deepseek/deepseek-v4-flash",
    max_tokens: int = 2048,
) -> str:
    """Generate a persona response via OpenRouter."""
    import requests

    # Build context string from chunks
    context = "\n\n".join(c["text"][:500] for c in context_chunks if c["score"] >= 0.65)

    # Summarize key themes from chunks for the system prompt
    themes = " | ".join(c["text"][:100] for c in context_chunks[:4] if c["score"] >= 0.65)
    system = SYSTEM_PROMPT + f"\n\nKey themes from the collection: {themes}"

    headers = {
        "Authorization": f"Bearer {load_openrouter_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": f"{query}\n\nContext:\n{context}"},
        ],
        "max_tokens": max_tokens,
    }

    resp = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=headers,
        json=payload,
        timeout=60,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def main():
    parser = argparse.ArgumentParser(description="Actualized persona: search + LLM response")
    parser.add_argument("query", help="User question")
    parser.add_argument("--top-k", type=int, default=8, help="Search results to retrieve")
    parser.add_argument("--model", default="deepseek/deepseek-v4-flash", help="LLM model")
    parser.add_argument("--strip-markdown", action="store_true", help="Strip markdown from output")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    args = parser.parse_args()

    load_env()

    # Step 1: Search
    hits = search(args.query, args.top_k)
    print(f"[search] {len(hits)} results, top score: {hits[0]['score']}", file=sys.stderr)

    # Step 2: Generate
    response = generate_persona_response(args.query, hits, model=args.model)
    print(f"[persona] {len(response)} chars", file=sys.stderr)

    # Step 3: Output
    if args.strip_markdown:
        response = strip_markdown(response)

    if args.json:
        import json
        print(json.dumps({
            "query": args.query,
            "response": response,
            "chunks_used": [h for h in hits if h["score"] >= 0.65],
        }, indent=2))
    else:
        print(response)


if __name__ == "__main__":
    main()
