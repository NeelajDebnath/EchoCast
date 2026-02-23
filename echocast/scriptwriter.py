"""
EchoCast 2 — Script Writer Agent
Uses Gemini 3 Pro to convert a research report into a two-person
podcast dialogue, returned as a JSON array.
"""

from __future__ import annotations

import json
import re

from echocast.config import MAX_SCRIPT_CHARS, MAX_CHARS_PER_LINE
from echocast.gemini_client import call_pro

_SYSTEM_PROMPT = f"""\
You are a talented podcast scriptwriter. You will receive a comprehensive
research report on a specific topic. Your job is to transform it into an
engaging, natural-sounding podcast dialogue between two people:

• **Host** — The primary presenter. Confident, curious, sets the agenda.
• **Guest** — A knowledgeable expert. Provides depth, examples, and analogies.

Rules:
1. The dialogue must feel natural and conversational — avoid academic tone.
2. Include an intro where the Host welcomes listeners and introduces the topic.
3. Cover all key points from the report — don't skip important information.
4. End with a summary and a sign-off from the Host.
5. STRICT CHARACTER BUDGET:
   - Total script must be under {MAX_SCRIPT_CHARS:,} characters.
   - NO single dialogue line may exceed {MAX_CHARS_PER_LINE:,} characters.
6. Output ONLY a JSON array with objects like:
   {{"speaker": "Host", "text": "..."}}
   {{"speaker": "Guest", "text": "..."}}
7. Do NOT include any text outside the JSON array — no markdown code fences,
   no commentary, just the raw JSON array.
"""


def _extract_json(raw: str) -> list[dict[str, str]]:
    """
    Robustly extract the JSON array from the LLM response,
    handling markdown code fences or extra text.
    """
    # Try direct parse first
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return data
    except json.JSONDecodeError:
        pass

    # Try to find JSON inside code fences
    fence_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find the first [ ... ] block
    bracket_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if bracket_match:
        try:
            return json.loads(bracket_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not extract valid JSON dialogue from LLM response.")


def write_script(topic: str, report: str) -> list[dict[str, str]]:
    """
    Main entry-point for the Script Writer Agent.
    Takes a topic and summary report, returns a dialogue as a list of
    {"speaker": "Host"/"Guest", "text": "..."} dicts.
    """
    print("\n🎙️  SCRIPT WRITER AGENT — Generating podcast dialogue …")

    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Research Report:\n{report}\n\n"
        f"Now write the podcast script as a JSON array."
    )

    raw_response = call_pro(_SYSTEM_PROMPT, user_prompt)
    dialogue = _extract_json(raw_response)

    # ── Validate the dialogue ────────────────────────────────────────────
    total_chars = 0
    for i, line in enumerate(dialogue):
        speaker = line.get("speaker", "Unknown")
        text = line.get("text", "")
        line_len = len(text)
        total_chars += line_len
        if line_len > MAX_CHARS_PER_LINE:
            print(f"  ⚠️  Line {i} ({speaker}) is {line_len} chars — "
                  f"truncating to {MAX_CHARS_PER_LINE}")
            line["text"] = text[:MAX_CHARS_PER_LINE]
            total_chars = total_chars - line_len + MAX_CHARS_PER_LINE

    print(f"  📊  Script: {len(dialogue)} lines, {total_chars:,} total characters")
    if total_chars > MAX_SCRIPT_CHARS:
        print(f"  ⚠️  Script exceeds budget ({MAX_SCRIPT_CHARS:,} chars). Trimming …")
        trimmed: list[dict[str, str]] = []
        running = 0
        for line in dialogue:
            line_len = len(line["text"])
            if running + line_len > MAX_SCRIPT_CHARS:
                break
            trimmed.append(line)
            running += line_len
        dialogue = trimmed
        print(f"  ✂️  Trimmed to {len(dialogue)} lines, {running:,} characters")

    print("🎙️  SCRIPT WRITER AGENT — Complete.\n")
    return dialogue
