"""
EchoCast 2 — Orchestrator
The main pipeline coordinator powered by Gemini 3 Flash.
Generates search queries then drives each agent in sequence.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from echocast.gemini_client import call_flash
from echocast.researcher import research
from echocast.summarizer import summarise
from echocast.scriptwriter import write_script
from echocast.producer import produce

_QUERY_SYSTEM_PROMPT = """\
You are an expert research strategist. Given a topic, generate a list of
5-7 highly targeted search queries that will surface the most comprehensive
and diverse information about that topic.

Rules:
1. Queries should cover different angles: technical details, recent news,
   expert opinions, history, future outlook, controversies, applications.
2. Each query should be specific enough to find high-quality results.
3. Output ONLY a JSON array of query strings — no extra text, no code fences.

Example output:
["query one", "query two", "query three"]
"""


def _extract_queries(raw: str) -> list[str]:
    """Parse the JSON array of queries from the LLM response."""
    # Try direct parse
    try:
        data = json.loads(raw)
        if isinstance(data, list):
            return [str(q) for q in data]
    except json.JSONDecodeError:
        pass

    # Try finding array in code fences
    fence_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", raw, re.DOTALL)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass

    # Try finding any array
    bracket_match = re.search(r"\[.*\]", raw, re.DOTALL)
    if bracket_match:
        try:
            return json.loads(bracket_match.group(0))
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not extract search queries from LLM response.")


def run(topic: str) -> Path:
    """
    Execute the full EchoCast pipeline:
      Topic → Queries → Research → Summary → Script → Audio
    Returns the path to the final podcast MP3.
    """
    print("=" * 60)
    print(f"  🎙️  EchoCast 2 — Generating podcast")
    print(f"  📌  Topic: {topic}")
    print("=" * 60)

    # ── Stage 1: Generate search queries (Gemini Flash) ──────────────────
    print("\n🧠  ORCHESTRATOR — Generating research queries …")
    raw_queries = call_flash(
        _QUERY_SYSTEM_PROMPT,
        f"Generate search queries for the following podcast topic:\n\n{topic}",
    )
    queries = _extract_queries(raw_queries)
    print(f"  ✅  Generated {len(queries)} queries:")
    for i, q in enumerate(queries, 1):
        print(f"    {i}. {q}")

    # ── Stage 2: Deep research (Apify) ───────────────────────────────────
    research_data = research(queries)

    if not research_data:
        print("  ⚠️  No research data collected. Aborting.")
        raise RuntimeError("Research stage returned no data.")

    # ── Stage 3: Summarise (Gemini Pro) ──────────────────────────────────
    report = summarise(topic, research_data)

    # ── Stage 4: Write script (Gemini Pro) ───────────────────────────────
    dialogue = write_script(topic, report)

    # ── Stage 5: Produce audio (ElevenLabs + pydub) ──────────────────────
    output_path = produce(dialogue)

    print("=" * 60)
    print(f"  🎉  PODCAST READY: {output_path}")
    print("=" * 60)
    return output_path
