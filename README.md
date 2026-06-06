# actualized-persona

RAG-powered immersive persona — turns an AI assistant into a direct embodiment of Leo Gura (Actualized.org) by querying a collection of 12,000+ YouTube transcripts, absorbing the retrieved knowledge, and replying as the person themselves. No citations, no attribution. Just the voice.

## What It Does

This is a Hermes Agent skill that implements a **persona inhabitation** pattern:

1. User asks a question
2. The system queries a Qdrant vector database of Actualized.org transcripts
3. Top 4-8 relevant chunks are extracted (filtered for coherence)
4. Chunks are fed into DeepSeek V4 Flash via OpenRouter with a first-person persona system prompt
5. Response is delivered as if Leo Gura is speaking directly to you

## Audio Samples

Sample persona responses generated during the original session (Edge TTS, Jenny voice):

| Question | Audio |
|----------|-------|
| "What is life?" | [what_is_life.ogg](audio-samples/what_is_life.ogg) |
| "Why is life so damn hard?" | [why_is_life_hard.ogg](audio-samples/why_is_life_hard.ogg) |
| "How do I let go of suffering and what I love?" | [letting_go.ogg](audio-samples/letting_go.ogg) |
| "How do I just observe without trying?" | [just_observing.ogg](audio-samples/just_observing.ogg) |

Full Q&A transcripts are in `persona-samples/`.

## Repo Structure

```
actualized-persona/
├── README.md                     # This file
├── SKILL.md                      # Hermes skill definition (copy)
├── scripts/
│   ├── actualized_search.py      # Standalone Qdrant search (no LLM)
│   └── actualized_persona.py     # Full pipeline: search + persona LLM
├── persona-samples/              # Full Q&A transcripts from the session
│   ├── what_is_life.md
│   ├── why_is_life_hard.md
│   ├── letting_go.md
│   └── just_observing.md
├── audio-samples/                # TTS audio from the session
│   └── *.ogg
├── voice-mode/
│   └── SKILL.md                  # Companion voice-mode skill
└── docs/
    └── setup.md                  # Setup & requirements
```

## Quick Start

```bash
# 1. Query the collection (search only)
python3 scripts/actualized_search.py "what is life"

# 2. Full persona pipeline (search + LLM response)
python3 scripts/actualized_persona.py "what is life"
```

## Requirements

- Python 3.11+
- `qdrant-client`, `nomic`, `requests` (see `docs/setup.md`)
- Qdrant Cloud credentials in `~/.hermes/.env`
- Nomic API key in `~/.hermes/.env`
- OpenRouter API key in `~/.hermes/.env`

## The Collection

- **Name:** `actualized`
- **Content:** Actualized.org YouTube transcripts (Leo Gura)
- **Topics:** consciousness, self-help, philosophy, spirituality, psychology
- **Size:** 12,037 points, 768-dim Cosine (nomic-embed-text-v1.5)

## Key Insight

The standard RAG pattern is: *query → retrieve → cite*. This project flips it to: *query → retrieve → absorb → embody*. The retrieved chunks aren't shown to the user — they become part of the LLM's internal context, producing a response that sounds like a human who has spent 20 years thinking about these questions, not an AI reading search results.

## License

MIT
