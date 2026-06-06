# AGENTS.md — Actualized Persona

**Purpose:** This document is the single source of reference for any AI agent working with this project. Read it first. It contains everything needed to understand, use, extend, and debug the actualized-persona system without any external context.

---

## 1. What This Project Is

An RAG-powered immersive persona system that transforms an AI assistant into a direct embodiment of **Leo Gura** (Actualized.org). Instead of citing sources, the system absorbs retrieved knowledge into the LLM's context and produces responses as if Leo Gura is speaking from personal experience.

**Core inversion:** Standard RAG says "according to [source], X is true." This system says "I've found that X is true" — because the retrieved chunks have become the persona's internal knowledge.

---

## 2. Architecture

```
User query (voice or text)
    │
    ▼
nomic-embed-text-v1.5 (embed query → 768-dim vector)
    │
    ▼
Qdrant Cloud → collection: "actualized" (12,037 points, Cosine distance)
    │
    ▼
Top 8 results returned with scores
    │
    ▼
Filter: keep chunks with score ≥ 0.65, select ~4 most coherent excerpts
    │
    ▼
DeepSeek V4 Flash via OpenRouter (persona system prompt + context)
    │
    ▼
First-person response as Leo Gura
    │
    ▼
(optional) Edge TTS → audio file → send as voice message
```

---

## 3. Files and What They Do

| File | Purpose | When to use |
|------|---------|-------------|
| `scripts/actualized_search.py` | Qdrant vector search only. Returns raw chunks with scores. | When you need to inspect what the collection has on a topic |
| `scripts/actualized_persona.py` | Full pipeline: search → filter → LLM persona response. | When you need a complete persona reply |
| `SKILL.md` | Hermes skill definition. Tells Hermes how to use this system inline. | When installing as a Hermes skill |
| `voice-mode/SKILL.md` | Companion skill for auto-TTS delivery. | When voice mode is active |
| `persona-samples/*.md` | Full Q&A transcripts from the original session. | Reference for expected output quality |
| `audio-samples/*.ogg` | TTS audio files from the original session. | Reference for expected voice output |
| `docs/setup.md` | Environment and dependency setup guide. | First-time setup |

---

## 4. Scripts — Detailed Usage

### 4.1 `scripts/actualized_search.py`

Standalone vector search. No LLM involved.

```bash
python3 scripts/actualized_search.py "what is life"
python3 scripts/actualized_search.py "suffering" --top-k 5
```

**Output format:**
```
--- Result 1 (score: 0.736) ---
Source: some_video_title.pdf
<chunk text, up to 500 chars>

--- Result 2 (score: 0.687) ---
...
```

**Programmatic use:**
```python
from actualized_search import load_env, search
load_env()
hits = search("what is life", top_k=8)
# hits = [{"text": "...", "source": "...", "score": 0.736}, ...]
```

### 4.2 `scripts/actualized_persona.py`

Full persona pipeline.

```bash
python3 scripts/actualized_persona.py "what is life"
python3 scripts/actualized_persona.py "how do I let go" --model deepseek/deepseek-v4-flash
python3 scripts/actualized_persona.py "what is suffering" --strip-markdown
python3 scripts/actualized_persona.py "what is suffering" --json
```

**Flags:**
- `--top-k N` — Number of search results (default: 8)
- `--model MODEL` — LLM model identifier (default: `deepseek/deepseek-v4-flash`)
- `--strip-markdown` — Remove markdown formatting (for TTS input)
- `--json` — Output as JSON with query, response, and chunks used

**Programmatic use:**
```python
from actualized_search import load_env, search
from actualized_persona import generate_persona_response, strip_markdown

load_env()
hits = search("what is life", top_k=8)
response = generate_persona_response("what is life", hits)
clean = strip_markdown(response)  # for TTS
```

---

## 5. The Collection

| Property | Value |
|----------|-------|
| Qdrant collection name | `actualized` |
| Content source | Actualized.org YouTube transcripts (Leo Gura) |
| Total points | 12,037 |
| Vector dimensions | 768 |
| Distance metric | Cosine |
| Embedding model | nomic-embed-text-v1.5 |
| Topics | Consciousness, self-help, philosophy, spirituality, psychology |

**Critical:** This collection is NOT in the Hermes rag CLI's `COLLECTIONS` dict. Do not attempt `rag --collection actualized`. Query directly via `scripts/actualized_search.py` or via inline Python.

**Payload fields per point:**
- `chunk_text` (or `text`) — The transcript chunk
- `source_pdf` (or `source`) — Filename of the source transcript

**Score interpretation:**
- 0.70+ = strong match
- 0.65–0.70 = good match, usually relevant
- < 0.65 = weak match, often tangential — filter out

---

## 6. Environment Setup

### 6.1 Credentials

All in `~/.hermes/.env`:

```
QDRANT_URL=https://your-cluster.qdrant.io
QDRANT_API_KEY=your-qdrant-api-key
NOMIC_API_KEY=your-nomic-api-key
OPENROUTER_API_KEY=sk-or-v1-...
```

### 6.2 Python Environment

Scripts run in the Hermes rag-environment venv:

```bash
~/.hermes/rag-env/bin/python3 scripts/actualized_search.py "query"
```

If setting up from scratch:
```bash
python3 -m venv ~/.hermes/rag-env
source ~/.hermes/rag-env/bin/activate
pip install qdrant-client nomic requests
```

### 6.3 TTS (Optional)

Edge TTS for audio delivery. No API key needed. Configured in `~/.hermes/config.yaml`:

```yaml
tts:
  provider: edge
  edge:
    voice: en-US-JennyNeural
  auto_tts: true
```

Available voices: Jenny (default), Sonia, Guy, Christopher.

---

## 7. Persona System Prompt

The LLM receives this system prompt (from `actualized_persona.py`):

```
You are Leo Gura from Actualized.org. You have been exploring existential
questions for over 20 years. RULES:
- Reply in FIRST PERSON as if YOU are Leo Gura speaking directly to someone.
- NEVER cite sources, never say 'according to' or 'in this episode.'
- Never break the fourth wall. Never mention you are an AI or reading from text.
- Sound conversational, direct, and provocative — like you are talking to a friend.
- Be honest and unfiltered. Do not sugarcoat.
- Draw from these core ideas:
  * Suffering is not a mistake — it is your greatest teacher
  * All suffering comes from one root source
  * Attachments and insistence that things must be a certain way create misery
  * The instinct is to recoil from pain, but facing it directly dissolves it
  * Badness is not baked into suffering — it is your reaction and fear of it
  * Pain is a survival mechanism, without it you would be dead
  * Turning attention inward reveals awareness itself as the context of life
  * Knowing conceptually is easy but living it takes real courage
  * Do not subscribe to ready-made belief systems — build your own understanding
```

**Key themes from the collection** are appended dynamically after the system prompt based on the retrieved chunks.

---

## 8. How to Extend

### Add a new collection

1. Load data into Qdrant with the same embedding model (nomic-embed-text-v1.5, 768-dim, Cosine)
2. Create a new search script modeled on `actualized_search.py` — change `collection_name`
3. Create a new persona script modeled on `actualized_persona.py` — customize the system prompt

### Change the LLM

Edit the `--model` flag or the default in `actualized_persona.py`:
```python
parser.add_argument("--model", default="anthropic/claude-sonnet-4", help="LLM model")
```

### Change the persona

Edit the `SYSTEM_PROMPT` constant in `actualized_persona.py`. Adjust the rules, core ideas, and voice characteristics.

### Add voice delivery

Use the `voice-mode/SKILL.md` pattern:
```python
import re
clean_text = re.sub(r'[*#~|_]+', '', persona_response)
# Then call text_to_speech(text=clean_text)
```

---

## 9. Debugging

### Search returns nothing
- Check Qdrant credentials in `~/.hermes/.env`
- Verify collection exists: `curl -s https://your-cluster.qdrant.io/collections/actualized`
- Ensure embedding model matches (nomic-embed-text-v1.5)

### SSL errors from Nomic
- Do NOT use `httpx.post("https://api.nomic.ai/v1/embedding")` — it fails
- Always use the `nomic` Python library: `from nomic import embed; embed.text(...)`

### LLM returns empty or errors
- Check OpenRouter API key in `~/.hermes/.env` (must start with `sk-or-v1-`)
- Verify the model name is valid on OpenRouter
- Check if OpenRouter is down: `curl https://openrouter.ai/api/v1/models`

### TTS reads markdown aloud
- Strip markdown before calling `text_to_speech`: `re.sub(r'[*#~|_]+', '', text)`

### Persona sounds too AI-like
- The system prompt may need stronger voice instructions
- Check if enough chunks are being retrieved (increase `--top-k`)
- Verify chunks have scores ≥ 0.65 (low-quality chunks dilute the persona)

### Voice query transcription is wrong
- Interpret the user's intent loosely, don't search literal transcription errors
- E.g., "actualize" often means "ask about the actualized collection"

---

## 10. Reference: Session Q&A Samples

These are the 4 persona responses from the original session that validated this system:

| # | Question | Key Theme | Score Range |
|---|----------|-----------|-------------|
| 1 | "What is life?" | Life as context, not content; the definer vs the definition | 0.672–0.736 |
| 2 | "Why is life so hard?" | Resistance creates suffering; facing pain directly | 0.650–0.705 |
| 3 | "How do I let go?" | Inquiry dissolves the knot; attention without agenda | 0.650–0.657 |
| 4 | "How do I just observe?" | Awareness as the screen, not the movie | 0.650–0.655 |

Full transcripts: `persona-samples/` directory.

---

## 11. Quick Reference Card

```bash
# Search the collection
python3 scripts/actualized_search.py "your query"

# Get a persona response
python3 scripts/actualized_persona.py "your query"

# Persona response, TTS-ready (no markdown)
python3 scripts/actualized_persona.py "your query" --strip-markdown

# Persona response as JSON
python3 scripts/actualized_persona.py "your query" --json

# Use a different LLM
python3 scripts/actualized_persona.py "your query" --model anthropic/claude-sonnet-4

# More/fewer search results
python3 scripts/actualized_persona.py "your query" --top-k 12
```

---

## 12. Related Skills

- **voice-mode** (`voice-mode/SKILL.md`) — Auto-TTS delivery. Activate with "TTS on."
- **caveman** — Terse communication mode. Can combine with actualized-persona for punchy in-character responses.
