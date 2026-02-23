"""
EchoCast 2 — Configuration & Settings
Loads API keys from .env and defines constants used across all agents.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# ── Load .env from project root ──────────────────────────────────────────────
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

# ── API Keys ─────────────────────────────────────────────────────────────────
GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
APIFY_API_TOKEN: str = os.getenv("APIFY_API_TOKEN", "")
ELEVENLABS_API_KEY: str = os.getenv("ELEVENLABS_API_KEY", "")

# ── Gemini Model Names ───────────────────────────────────────────────────────
MODEL_FLASH: str = "gemini-3-flash-preview"      # Orchestrator (fast)
MODEL_PRO: str = "gemini-3-pro-preview"           # Summarizer & Script Writer (powerful)

# ── Apify Actor IDs ──────────────────────────────────────────────────────────
APIFY_GOOGLE_SEARCH: str = "apify/google-search-scraper"
APIFY_WEB_CRAWLER: str = "apify/website-content-crawler"

# ── ElevenLabs Settings ──────────────────────────────────────────────────────
# Default voices available on the free tier
VOICE_HOST: str = "JBFqnCBsd6RMkjVDRZzb"         # George — deep, authoritative
VOICE_GUEST: str = "EXAVITQu4vr4xnSDxMaL"        # Sarah — warm, conversational
TTS_MODEL: str = "eleven_multilingual_v2"
TTS_OUTPUT_FORMAT: str = "mp3_44100_128"

# ── Script Budget (stay within ElevenLabs free tier) ─────────────────────────
MAX_SCRIPT_CHARS: int = 8_000        # Total chars across all dialogue lines
MAX_CHARS_PER_LINE: int = 2_400      # ElevenLabs limit is 2,500 per request

# ── Output ───────────────────────────────────────────────────────────────────
OUTPUT_DIR: Path = _PROJECT_ROOT / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ── FFmpeg auto-detection ────────────────────────────────────────────────────
# pydub requires ffmpeg on PATH for MP3 export. Auto-detect common locations.
import glob
import shutil

def _find_ffmpeg() -> str | None:
    """Find ffmpeg executable, checking PATH then common install locations."""
    # Already on PATH?
    found = shutil.which("ffmpeg")
    if found:
        return found
    # Check winget install location
    patterns = [
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gyan*\*\bin\ffmpeg.exe"),
        r"C:\ffmpeg\bin\ffmpeg.exe",
        r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    ]
    for pattern in patterns:
        matches = glob.glob(pattern)
        if matches:
            return matches[0]
    return None

_ffmpeg_path = _find_ffmpeg()
if _ffmpeg_path:
    _ffmpeg_dir = str(Path(_ffmpeg_path).parent)
    # Add to PATH so pydub & subprocess can find it
    if _ffmpeg_dir not in os.environ.get("PATH", ""):
        os.environ["PATH"] = _ffmpeg_dir + os.pathsep + os.environ.get("PATH", "")
