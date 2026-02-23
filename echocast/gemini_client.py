"""
EchoCast 2 — Gemini API Client Wrapper
Provides call_flash() and call_pro() helpers for the two model tiers.
Uses lazy initialisation so imports succeed without API keys set.
"""

from __future__ import annotations

from google import genai
from google.genai import types

from echocast.config import GEMINI_API_KEY, MODEL_FLASH, MODEL_PRO

# ── Lazy client singleton ─────────────────────────────────────────────────────
_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        if not GEMINI_API_KEY:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Copy .env.example → .env and fill in your key."
            )
        _client = genai.Client(api_key=GEMINI_API_KEY)
    return _client


def call_flash(system_prompt: str, user_prompt: str) -> str:
    """Call Gemini 3 Flash (fast orchestrator model)."""
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_FLASH,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
        contents=user_prompt,
    )
    return response.text or ""


def call_pro(system_prompt: str, user_prompt: str) -> str:
    """Call Gemini 3 Pro (powerful reasoning model)."""
    client = _get_client()
    response = client.models.generate_content(
        model=MODEL_PRO,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
        ),
        contents=user_prompt,
    )
    return response.text or ""
