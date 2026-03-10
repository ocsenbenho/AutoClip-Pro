# 📖 Usage Guide

Step-by-step instructions for using AutoClip Pro.

## Starting the Application

### 1. Start the Backend API

```bash
cd AutoClip-Pro
source .venv/bin/activate
python3 -m uvicorn apps.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.

### 2. Start the Frontend

```bash
cd AutoClip-Pro/frontend
npm run dev
```

The web UI will be available at `http://localhost:3000`.

---

## Creating a Clip Job

### Step 1: Paste a YouTube URL

Open `http://localhost:3000` and paste any YouTube video URL into the input field.

> **Tip:** The system automatically strips playlist parameters, so Mix or playlist URLs work fine.

### Step 2: Choose a Highlight Detector

Select from the dropdown:

| Detector | When to Use |
|----------|-------------|
| **Local Analysis** | Quick results, no API key needed |
| **Google Gemini** | Best free option, requires `AUTOCLIP_GEMINI_API_KEY` |
| **OpenAI GPT** | Highest quality, requires `AUTOCLIP_OPENAI_API_KEY` |

### Step 3: Enable Vertical Format (Optional)

Check ☑️ **Vertical Format (9:16)** if you want clips optimized for:
- TikTok
- YouTube Shorts
- Instagram Reels

This crops the video from landscape to portrait (1080×1920).

### Step 4: Submit

Click **⚡ Generate Clips** and wait for the pipeline to complete.

---

## Monitoring Progress

After submitting, click on the job card to view real-time pipeline progress:

1. 📥 **Download** — Video is being downloaded from YouTube
2. 🎙️ **Transcribe** — Audio is being transcribed by Whisper
3. ✨ **Highlights** — AI is analyzing the transcript
4. ✂️ **Clipping** — FFmpeg is cutting video segments
5. 📝 **Subtitles** — SRT files are being generated
6. ✅ **Done** — All clips are ready!

---

## Viewing Results

Each completed clip card shows:

- 🎬 **Video Player** — Preview the clip directly in the browser
- ⭐ **Viral Score** — Color-coded engagement score (green ≥80%, yellow ≥50%, red <50%)
- 💡 **Reason** — AI explanation of why this moment was selected
- 🕐 **Timestamps** — Original video time range
- 📥 **Download MP4** — Download the clip file
- 📝 **Download SRT** — Download the subtitle file

---

## Configuration

### Environment Variables (`.env`)

| Variable | Default | Description |
|----------|---------|-------------|
| `AUTOCLIP_GEMINI_API_KEY` | (empty) | Google Gemini API key |
| `AUTOCLIP_GEMINI_MODEL` | `gemini-2.5-flash` | Gemini model name |
| `AUTOCLIP_OPENAI_API_KEY` | (empty) | OpenAI API key |
| `AUTOCLIP_OPENAI_MODEL` | `gpt-4o-mini` | OpenAI model name |
| `AUTOCLIP_WHISPER_MODEL` | `base` | Whisper model size |
| `AUTOCLIP_MIN_CLIP_DURATION` | `15.0` | Min clip length (seconds) |
| `AUTOCLIP_MAX_CLIP_DURATION` | `90.0` | Max clip length (seconds) |
| `AUTOCLIP_MAX_CLIPS` | `10` | Max clips per video |
| `AUTOCLIP_API_HOST` | `0.0.0.0` | API bind address |
| `AUTOCLIP_API_PORT` | `8000` | API port |

### Pipeline Config (`configs/pipeline.yaml`)

```yaml
whisper:
  model: "base"

openai:
  model: "gpt-4o-mini"

clips:
  min_duration: 15.0
  max_duration: 90.0
  max_count: 10

output:
  video_dir: "data/videos"
  clip_dir: "data/clips"
  subtitle_dir: "data/subtitles"
```

---

## Output Files

All generated files are saved in the `data/` directory:

```
data/
├── videos/      # Downloaded source videos
├── clips/       # Generated clip MP4 files
└── subtitles/   # Generated SRT subtitle files
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/jobs` | Create a new clip job |
| `GET` | `/api/jobs` | List all jobs |
| `GET` | `/api/jobs/{id}` | Get job details + clips |
| `DELETE` | `/api/jobs/{id}` | Delete a completed/failed job |
| `GET` | `/api/detectors` | List available AI detectors |
| `GET` | `/clips/{id}.mp4` | Stream/download a clip |
| `GET` | `/subtitles/{id}.srt` | Download a subtitle file |

### Example: Create Job via API

```bash
curl -X POST http://localhost:8000/api/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "detector": "gemini",
    "vertical_format": true
  }'
```
