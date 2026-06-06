# actualized-persona

RAG-powered immersive persona system. Query 12,000+ Actualized.org YouTube transcripts, absorb the retrieved knowledge, and reply as Leo Gura himself — first-person, no citations, just the voice.

## How It Works

Standard RAG: *query → retrieve → cite*. This project inverts it: *query → retrieve → absorb → embody*.

The retrieved chunks are never shown to the user. They become invisible context for the LLM, which then speaks as if the knowledge is its own lived experience. The output sounds like a human who has spent 20 years thinking about these questions — not an AI reading search results.

**Pipeline:**

```
User question
  → nomic-embed-text-v1.5 (Qdrant vector search)
  → Top 8 chunks from `actualized` collection
  → Filter to ~4 coherent excerpts (score ≥ 0.65)
  → DeepSeek V4 Flash via OpenRouter (persona system prompt)
  → First-person response as Leo Gura
  → (optional) Edge TTS audio delivery
```

## Quick Start

```bash
# Search only (returns raw chunks)
python3 scripts/actualized_search.py "what is life"

# Full persona pipeline (search + LLM response)
python3 scripts/actualized_persona.py "what is life"

# With markdown stripped (for TTS)
python3 scripts/actualized_persona.py "what is life" --strip-markdown

# JSON output (includes chunks used)
python3 scripts/actualized_persona.py "what is life" --json
```

## Repository Structure

```
actualized-persona/
├── README.md                         # This file
├── AGENTS.md                         # Agent reference — source of truth
├── SKILL.md                          # Hermes skill definition
├── scripts/
│   ├── actualized_search.py          # Qdrant vector search (no LLM)
│   └── actualized_persona.py         # Full pipeline: search → persona LLM
├── persona-samples/                  # Full Q&A transcripts from the session
│   ├── what_is_life.md
│   ├── why_is_life_hard.md
│   ├── letting_go.md
│   └── just_observing.md
├── audio-samples/                    # TTS audio outputs (Edge, Jenny voice)
│   ├── what_is_life.ogg
│   ├── why_is_life_hard.ogg
│   ├── letting_go.ogg
│   └── just_observing.ogg
├── voice-mode/
│   └── SKILL.md                      # Companion voice-mode skill
└── docs/
    └── setup.md                      # Setup & environment guide
```

## The Collection

| Property | Value |
|----------|-------|
| Name | `actualized` |
| Content | Actualized.org YouTube transcripts (Leo Gura) |
| Topics | Consciousness, self-help, philosophy, spirituality, psychology |
| Points | 12,037 |
| Dimensions | 768 (Cosine distance) |
| Embedding model | nomic-embed-text-v1.5 |

**Note:** The `actualized` collection is not registered in the Hermes rag CLI's `COLLECTIONS` dict. Running `rag --collection actualized` will fail with "invalid choice." You must query it directly via the scripts in this repo or via inline Python using `qdrant-client` + `nomic`.

## Requirements

| Dependency | Purpose |
|------------|---------|
| Python 3.11+ | Runtime |
| `qdrant-client` | Vector DB queries |
| `nomic` | Text embeddings (must use library, not raw HTTP) |
| `requests` | OpenRouter API calls |
| Qdrant Cloud | Vector database hosting |
| Nomic API key | Embedding generation |
| OpenRouter API key | LLM inference |

All credentials live in `~/.hermes/.env`. See `docs/setup.md` for full installation steps.

## Audio Samples

Persona responses generated during the original session (Edge TTS, Jenny voice):

| Question | Audio | Transcript |
|----------|-------|------------|
| "What is life?" | [OGG](audio-samples/what_is_life.ogg) | [MD](persona-samples/what_is_life.md) |
| "Why is life so damn hard?" | [OGG](audio-samples/why_is_life_hard.ogg) | [MD](persona-samples/why_is_life_hard.md) |
| "How do I let go of suffering?" | [OGG](audio-samples/letting_go.ogg) | [MD](persona-samples/letting_go.md) |
| "How do I just observe?" | [OGG](audio-samples/just_observing.ogg) | [MD](persona-samples/just_observing.md) |

## Hermes Integration

Install as a Hermes skill:

```bash
# Copy skill definition
cp SKILL.md ~/.hermes/skills/data-science/actualized-persona/SKILL.md

# Copy voice-mode companion
cp voice-mode/SKILL.md ~/.hermes/skills/productivity/voice-mode/SKILL.md
```

Activate with: *"actualized mode on"*
Deactivate with: *"actualized mode off"*

## Known Pitfalls

- **Nomic direct HTTP fails.** `httpx.post("https://api.nomic.ai/v1/embedding")` throws SSL handshake errors. Always use the `nomic` Python library (`embed.text()`).
- **rag CLI doesn't know about `actualized`.** Must query Qdrant directly.
- **Raw chunks are noisy.** Filter to ~4 coherent excerpts before piping to LLM.
- **TTS reads markdown aloud.** Strip `**`, `*`, `#`, `~~` before calling `text_to_speech`.
- **Voice-to-text is imprecise.** User voice queries may contain transcription errors. Interpret loosely before searching.

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  User Query  │────▶│  nomic embed │────▶│ Qdrant search│────▶│  Chunks  │
│  (voice/text)│     │  (768-dim)   │     │ (actualized) │     │ (top 8)  │
└─────────────┘     └──────────────┘     └──────────────┘     └────┬─────┘
                                                                    │
                                                            ┌───────▼──────┐
                                                            │   Filter     │
                                                            │ (score≥0.65) │
                                                            └───────┬──────┘
                                                                    │
                                                            ┌───────▼──────┐
                                                            │  DeepSeek V4  │
                                                            │  Flash +      │
                                                            │  Persona      │
                                                            │  Prompt       │
                                                            └───────┬──────┘
                                                                    │
                                                            ┌───────▼──────┐
                                                            │  Response    │
                                                            │  (in voice)  │
                                                            │  + Edge TTS  │
                                                            └──────────────┘
```

## License

MIT
