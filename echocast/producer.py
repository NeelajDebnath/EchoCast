"""
EchoCast 2 — Producer Agent
Converts a podcast dialogue (JSON) into a stitched MP3 file using
ElevenLabs TTS and pydub. Uses lazy client initialisation.
"""

from __future__ import annotations

import io
from pathlib import Path

from elevenlabs import ElevenLabs
from pydub import AudioSegment

from echocast.config import (
    ELEVENLABS_API_KEY,
    OUTPUT_DIR,
    TTS_MODEL,
    TTS_OUTPUT_FORMAT,
    VOICE_GUEST,
    VOICE_HOST,
)

# ── Lazy ElevenLabs client ───────────────────────────────────────────────────
_el_client: ElevenLabs | None = None

# Map speaker names to voice IDs
_VOICE_MAP: dict[str, str] = {
    "Host": VOICE_HOST,
    "Guest": VOICE_GUEST,
}

# Silence between dialogue lines (milliseconds)
_PAUSE_MS = 600


def _get_el_client() -> ElevenLabs:
    global _el_client
    if _el_client is None:
        if not ELEVENLABS_API_KEY:
            raise RuntimeError(
                "ELEVENLABS_API_KEY is not set. "
                "Copy .env.example → .env and fill in your key."
            )
        _el_client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    return _el_client


def _generate_speech(text: str, voice_id: str) -> AudioSegment:
    """
    Call ElevenLabs TTS and return the audio as a pydub AudioSegment.
    """
    client = _get_el_client()
    audio_iterator = client.text_to_speech.convert(
        voice_id=voice_id,
        output_format=TTS_OUTPUT_FORMAT,
        text=text,
        model_id=TTS_MODEL,
    )

    # Collect all chunks from the iterator into a bytes buffer
    audio_bytes = b"".join(audio_iterator)
    audio_buffer = io.BytesIO(audio_bytes)
    segment = AudioSegment.from_mp3(audio_buffer)
    return segment


def produce(dialogue: list[dict[str, str]], filename: str = "podcast.mp3") -> Path:
    """
    Main entry-point for the Producer Agent.
    Takes a dialogue list and produces a stitched MP3 file.
    Returns the path to the output file.
    """
    print("\n🎧  PRODUCER AGENT — Generating audio …")

    if not dialogue:
        raise ValueError("No dialogue lines to produce.")

    silence = AudioSegment.silent(duration=_PAUSE_MS)
    combined = AudioSegment.empty()
    total_chars_used = 0

    for i, line in enumerate(dialogue):
        speaker = line.get("speaker", "Host")
        text = line.get("text", "")
        voice_id = _VOICE_MAP.get(speaker, VOICE_HOST)
        total_chars_used += len(text)

        print(f"  🔊  [{i + 1}/{len(dialogue)}] {speaker}: "
              f"{text[:60]}{'…' if len(text) > 60 else ''} "
              f"({len(text)} chars)")

        segment = _generate_speech(text, voice_id)
        combined += segment + silence

    # ── Export final file ─────────────────────────────────────────────────
    output_path = OUTPUT_DIR / filename
    combined.export(str(output_path), format="mp3", bitrate="128k")

    duration_secs = len(combined) / 1000
    print(f"\n  ✅  Audio exported: {output_path}")
    print(f"  📊  Duration: {duration_secs:.1f}s | "
          f"Characters used: {total_chars_used:,}")
    print("🎧  PRODUCER AGENT — Complete.\n")
    return output_path
