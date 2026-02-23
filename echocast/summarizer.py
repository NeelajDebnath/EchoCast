"""
EchoCast 2 — Summarizer Agent
Uses Gemini 3 Pro to distil raw research data into a structured report.
"""

from __future__ import annotations

from echocast.gemini_client import call_pro

_SYSTEM_PROMPT = """\
You are a world-class research analyst. You will receive a collection of
scraped web articles on a specific topic. Your job is to synthesise ALL
of the information into a single, comprehensive, well-structured report.

Rules:
- Use markdown headers, bullet points, and numbered lists for clarity.
- Include key facts, statistics, expert opinions, and contrasting viewpoints.
- Cite the source URL inline where appropriate, e.g. (source: <url>).
- The report should be thorough — aim for 2,000-4,000 words.
- Do NOT add any information you do not find in the provided sources.
- Organise the report into logical sections with clear headings.
"""


def _format_research(research_data: list[dict[str, str]]) -> str:
    """Format raw research dicts into a single text block for the prompt."""
    parts: list[str] = []
    for i, item in enumerate(research_data, 1):
        parts.append(
            f"--- Source {i} ---\n"
            f"URL: {item['url']}\n"
            f"Title: {item['title']}\n\n"
            f"{item['text']}\n"
        )
    return "\n".join(parts)


def summarise(topic: str, research_data: list[dict[str, str]]) -> str:
    """
    Main entry-point for the Summarizer Agent.
    Takes the topic and raw research data, returns a structured report.
    """
    print("\n📝  SUMMARIZER AGENT — Synthesising research …")

    if not research_data:
        print("  ⚠️  No research data provided. Returning empty summary.")
        return ""

    formatted = _format_research(research_data)

    user_prompt = (
        f"Topic: {topic}\n\n"
        f"Below are {len(research_data)} scraped web articles. "
        f"Synthesise them into a comprehensive research report.\n\n"
        f"{formatted}"
    )

    report = call_pro(_SYSTEM_PROMPT, user_prompt)

    print(f"  ✅  Report generated — {len(report):,} characters")
    print("📝  SUMMARIZER AGENT — Complete.\n")
    return report
