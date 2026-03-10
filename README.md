# 🎬 AutoClip Pro

AI-powered video clip generator that transforms long YouTube videos into engaging short clips — perfect for TikTok, YouTube Shorts, and Instagram Reels.

![Python 3.11](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![Next.js](https://img.shields.io/badge/Next.js-15-black?logo=next.js)
![License](https://img.shields.io/badge/License-MIT-green)

## ✨ Features

- 📥 **Smart Download** — Downloads YouTube videos via yt-dlp with automatic fallback strategies
- 🎙️ **AI Transcription** — Whisper-powered speech-to-text with precise timestamps
- ✨ **Multi-AI Highlight Detection** — Choose between Local Analysis, OpenAI GPT, or Google Gemini
- ✂️ **Auto Clipping** — FFmpeg cuts and encodes clips automatically
- 📱 **Vertical Format** — Optional 9:16 crop for TikTok / YouTube Shorts
- 📝 **Subtitle Generation** — Automatic SRT subtitles for each clip
- ⭐ **Viral Scoring** — Each clip receives an AI-generated engagement score with reasoning
- 🖥️ **Modern Web UI** — Dark-themed glassmorphism dashboard built with Next.js

## 🏗️ Architecture

AutoClip Pro follows a **layered clean architecture**:

```
apps/          → API server (FastAPI + Uvicorn)
pipelines/     → Workflow orchestration
services/      → Business logic
infra/         → External integrations (yt-dlp, Whisper, OpenAI, Gemini, FFmpeg)
interfaces/    → Abstract contracts
core/          → Models, config, logging, errors
```

> See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system diagram.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- FFmpeg (`brew install ffmpeg`)

### 1. Clone & Install

```bash
git clone https://github.com/ocsenbenho/AutoClip-Pro.git
cd AutoClip-Pro

# Backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend
npm install
cd ..
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Required for Gemini highlight detection
AUTOCLIP_GEMINI_API_KEY=your-gemini-api-key

# Optional: OpenAI (alternative to Gemini)
AUTOCLIP_OPENAI_API_KEY=your-openai-api-key

# Whisper model size: tiny | base | small | medium | large
AUTOCLIP_WHISPER_MODEL=base
```

### 3. Run

```bash
# Terminal 1: Backend API
source .venv/bin/activate
python3 -m uvicorn apps.api.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

Open **http://localhost:3000** in your browser.

> See [docs/USAGE_GUIDE.md](docs/USAGE_GUIDE.md) for detailed usage instructions.

## 📊 How It Works

```
YouTube URL → Download → Transcribe → AI Highlights → Cut Clips → Subtitles → Done!
```

1. Paste a YouTube URL and select your AI model
2. The system downloads the video and extracts audio
3. Whisper transcribes the audio with precise timestamps
4. AI analyzes the transcript to find viral-worthy moments
5. FFmpeg cuts clips at the detected timestamps
6. Each clip receives a viral score and engagement reasoning
7. Subtitles are auto-generated for each clip

> See [docs/SYSTEM_FLOW.md](docs/SYSTEM_FLOW.md) for detailed pipeline flow diagrams.

## 🤖 Supported AI Models

| Model | Type | Cost | Quality |
|-------|------|------|---------|
| **Local Analysis** | Rule-based | Free | Good |
| **Google Gemini** | `gemini-2.5-flash` | Free tier | Very Good |
| **OpenAI GPT** | `gpt-4o-mini` | Paid | Excellent |

## 📁 Project Structure

```
AutoClip-Pro/
├── apps/api/              # FastAPI server & routes
├── pipelines/             # Clip generation pipeline
├── services/              # Business logic services
├── infra/
│   ├── download/          # yt-dlp downloader
│   ├── llm/               # OpenAI, Gemini, Local detectors
│   ├── speech/            # Whisper engine
│   ├── subtitle/          # SRT generator
│   └── video/             # FFmpeg editor
├── interfaces/            # Abstract contracts
├── core/
│   ├── config/            # Centralized settings
│   ├── models/            # Pydantic data models
│   ├── errors/            # Custom exceptions
│   └── logging/           # Shared logger
├── frontend/              # Next.js 15 React app
├── configs/               # Pipeline YAML config
├── data/                  # Output videos, clips, subtitles
└── docs/                  # Documentation
```

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
