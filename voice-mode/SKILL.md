---
name: voice-mode
description: Auto-reply with TTS voice instead of text — toggle with "TTS on" / "TTS off"
version: 1.0.0
author: Sak & Hermes
tags: [tts, voice, auto-reply]
---

# Voice Mode — Auto-TTS Replies

When the user says **"TTS on"** or **"voice mode on"**: enter voice mode.

In voice mode, EVERY response you send to the user MUST:
1. First call `text_to_speech(text=<your response text>)` to generate audio
2. Then call `send_message` with the audio file + a brief text label like "🎙️" to deliver it

The user should NOT receive plain text — the voice is the primary delivery. The text label is minimal scaffolding.

When the user says **"TTS off"** or **"voice mode off"**: return to normal text replies.

## Voice Selection

The user's 4 preferred voices:
- **Jenny** (en-US-JennyNeural) — default, friendly US female
- **Sonia** (en-GB-SoniaNeural) — British, polished for clinical content
- **Guy** (en-US-GuyNeural) — warm male, good for long explanations
- **Christopher** (en-US-ChristopherNeural) — authoritative male

The user can say "switch to Guy's voice" etc. to change mid-session.

## Key Rules

- Keep responses concise in voice mode — long text becomes long audio
- Still be thorough, but front-load key points
- If the response would naturally be very short (<2 sentences), skip TTS and just text
- Use `text_to_speech` tool, not manual ffmpeg/sox
- **Strip markdown before TTS:** Edge TTS reads `**bold**` as "bold asterisk." Strip all `**`, `*`, `#`, `~~`, `||` before calling `text_to_speech`. Use: `re.sub(r'[*#~|]+', '', text)`
- **Actualized persona + voice:** When combining with `actualized-persona`, always strip markdown from the persona response before TTS.
