# Setup Guide

## Prerequisites

- Python 3.11+ (the scripts use the Hermes rag-environment venv)
- A Qdrant Cloud account with the `actualized` collection loaded
- Nomic API key (for embeddings)
- OpenRouter API key (for LLM)

## Environment Variables

Add these to `~/.hermes/.env`:

```
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
NOMIC_API_KEY=your-nomic-api-key
OPENROUTER_API_KEY=sk-or-v1-your-openrouter-key
```

## Python Dependencies

The scripts are designed to run in the Hermes rag-environment venv (`~/.hermes/rag-env/`). If setting up from scratch:

```bash
python3 -m venv ~/.hermes/rag-env
source ~/.hermes/rag-env/bin/activate
pip install qdrant-client nomic requests
```

## Verify Setup

```bash
# Test search
python3 scripts/actualized_search.py "what is life"

# Test full pipeline
python3 scripts/actualized_persona.py "what is life"
```

## Hermes Integration

Copy `SKILL.md` to `~/.hermes/skills/data-science/actualized-persona/SKILL.md` to install as a Hermes skill.

Copy `voice-mode/SKILL.md` to `~/.hermes/skills/productivity/voice-mode/SKILL.md` for voice mode support.

## TTS Setup

Voice mode requires Edge TTS (free, no API key). Configure in `~/.hermes/config.yaml`:

```yaml
tts:
  provider: edge
  edge:
    voice: en-US-JennyNeural
  auto_tts: true
```

Change voice via CLI:
```bash
hermes config set tts.edge.voice en-US-GuyNeural
```
