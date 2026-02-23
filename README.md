# 🎙️ EchoCast 2 — AI Podcast Generator

> **Synthesize your thoughts.** Enter a topic, get a fully-produced podcast with two AI speakers — powered by a 5-agent pipeline.

![Python](https://img.shields.io/badge/Python-3.12+-blue?logo=python&logoColor=white)
![Gemini](https://img.shields.io/badge/Google_Gemini-3_Pro-4285F4?logo=google&logoColor=white)
![ElevenLabs](https://img.shields.io/badge/ElevenLabs-TTS-FF6B00?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgZmlsbD0id2hpdGUiPjxyZWN0IHg9IjQiIHk9IjIiIHdpZHRoPSI0IiBoZWlnaHQ9IjIwIi8+PHJlY3QgeD0iMTAiIHk9IjYiIHdpZHRoPSI0IiBoZWlnaHQ9IjEyIi8+PHJlY3QgeD0iMTYiIHk9IjQiIHdpZHRoPSI0IiBoZWlnaHQ9IjE2Ii8+PC9zdmc+)
![Flask](https://img.shields.io/badge/Flask-Web_UI-000000?logo=flask&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

---

## 🧬 Architecture

EchoCast uses a **5-agent pipeline** where each stage is managed by a dedicated AI agent:

```
    ┌─────────────┐     ┌────────────┐     ┌────────────┐     ┌──────────────┐     ┌───────────┐
    │ ORCHESTRATOR │────▶│ RESEARCHER │────▶│ SUMMARIZER │────▶│ SCRIPT WRITER│────▶│ PRODUCER  │
    │ Gemini Flash │     │   Apify    │     │ Gemini Pro │     │  Gemini Pro  │     │ ElevenLabs│
    └─────────────┘     └────────────┘     └────────────┘     └──────────────┘     └───────────┘
         │                    │                  │                    │                   │
    Generates           Google Search +      Synthesizes       Two-speaker          TTS voices +
    research            deep web crawl       into report       dialogue JSON        pydub → MP3
    queries
```

| Agent | Model/API | Purpose |
|-------|-----------|---------|
| **Orchestrator** | Gemini 3 Flash | Generates targeted research queries from the user's topic |
| **Researcher** | Apify (Google Search + Website Crawler) | Finds URLs and deep-scrapes page content |
| **Summarizer** | Gemini 3 Pro | Distills raw scraped data into structured markdown report |
| **Script Writer** | Gemini 3 Pro | Converts report into natural Host + Guest dialogue (JSON) |
| **Producer** | ElevenLabs + pydub | Text-to-speech per line, stitched into final MP3 |

---

## ✨ Features

- 🤖 **Fully Agentic** — No human intervention after topic input
- 🔍 **Real-time Web Research** — Scrapes live data from 20+ URLs
- 🎭 **Two AI Voices** — Distinct Host and Guest speakers via ElevenLabs
- 📺 **Cyberpunk Web UI** — Retro-futuristic landing page with glitch animations
- 📡 **Live Progress** — Server-Sent Events stream pipeline logs to the browser
- 🎧 **Built-in Player** — Play, seek, and download the podcast directly in the browser
- ⚡ **CLI Mode** — Also works as a command-line tool

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.12+**
- **FFmpeg** (for MP3 export)
  ```bash
  # Windows
  winget install Gyan.FFmpeg
  # macOS
  brew install ffmpeg
  # Linux
  sudo apt install ffmpeg
  ```

### Installation

```bash
# Clone the repo
git clone https://github.com/NeelajDebnath/EchoCast.git
cd EchoCast

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Copy the example env file and fill in your API keys:

```bash
cp .env.example .env
```

You'll need API keys from:

| Service | Get your key at |
|---------|----------------|
| **Google Gemini** | [aistudio.google.com/apikey](https://aistudio.google.com/apikey) |
| **Apify** | [console.apify.com/settings/integrations](https://console.apify.com/settings/integrations) |
| **ElevenLabs** | [elevenlabs.io/app/settings/api-keys](https://elevenlabs.io/app/settings/api-keys) |

### Run

**Web UI (recommended):**
```bash
python server.py
# Open http://localhost:5000
```

**CLI mode:**
```bash
python main.py "The future of quantum computing"
# Output: output/podcast.mp3
```

---

## 📁 Project Structure

```
EchoCast/
├── .env.example         # API key template
├── .gitignore           # Excludes .env, output/, __pycache__/
├── requirements.txt     # Python dependencies
├── main.py              # CLI entrypoint
├── server.py            # Flask web server + REST API + SSE
├── echocast/            # Core pipeline
│   ├── config.py        # Settings, constants, FFmpeg auto-detect
│   ├── gemini_client.py # Gemini API wrapper (Flash + Pro)
│   ├── researcher.py    # Apify web research agent
│   ├── summarizer.py    # Gemini Pro summarization agent
│   ├── scriptwriter.py  # Gemini Pro script generation agent
│   ├── producer.py      # ElevenLabs TTS + pydub audio stitching
│   └── orchestrator.py  # Pipeline coordinator
└── frontend/
    ├── index.html       # Cyberpunk landing page
    └── audio_viz.png    # Audio visualizer background image
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the landing page |
| `POST` | `/api/generate` | Starts podcast generation (body: `{ "topic": "..." }`) |
| `GET` | `/api/status/:jobId` | SSE stream of real-time pipeline logs |
| `GET` | `/api/audio/:filename` | Serves the generated MP3 file |

---

## 🔒 Security

- API keys are stored in `.env` which is **gitignored** — never committed to version control
- `.env.example` contains placeholder values only
- All API clients use **lazy initialization** — imports succeed even without keys configured

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built with 🧠 Gemini 3 • 🔍 Apify • 🎙️ ElevenLabs • 🐍 Python</strong>
</p>
