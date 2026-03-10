# 🔄 System Flow

Detailed pipeline flow diagrams for all AutoClip Pro processing workflows.

## Main Clip Generation Pipeline

This is the primary workflow triggered when a user submits a YouTube URL.

```mermaid
flowchart TD
    START(["🎬 User submits YouTube URL"]) --> CREATE["Create Job<br/>(status: pending)"]
    CREATE --> DL["📥 Download Video<br/>(yt-dlp multi-strategy)"]

    DL --> DL_S1{"Strategy 1:<br/>Cookies + Best Format"}
    DL_S1 -->|Success| AUDIO
    DL_S1 -->|403 Forbidden| DL_S2{"Strategy 2:<br/>iOS/Android fallback"}
    DL_S2 -->|Success| AUDIO
    DL_S2 -->|Fail| FAIL

    AUDIO["🎵 Extract Audio<br/>(FFmpeg → WAV 16kHz)"]
    AUDIO --> TRANS["🎙️ Transcribe<br/>(Whisper STT)"]
    TRANS --> DETECT{"✨ Detect Highlights"}

    DETECT -->|Local| LOCAL["Rule-based Analysis<br/>(keyword + energy scoring)"]
    DETECT -->|OpenAI| GPT["GPT-4o-mini<br/>(JSON response)"]
    DETECT -->|Gemini| GEM["Gemini 2.5 Flash<br/>(JSON response)"]

    LOCAL --> HIGHLIGHTS
    GPT --> HIGHLIGHTS
    GEM --> HIGHLIGHTS

    HIGHLIGHTS["📊 Ranked Highlights<br/>(score + title + reason)"]
    HIGHLIGHTS --> CUT["✂️ Cut Clips<br/>(FFmpeg stream copy)"]

    CUT --> VERT{"📱 Vertical<br/>Format?"}
    VERT -->|Yes| CROP["Crop to 9:16<br/>(1080×1920)"]
    VERT -->|No| SUBS
    CROP --> SUBS

    SUBS["📝 Generate Subtitles<br/>(SRT per clip)"]
    SUBS --> DONE(["✅ Job Completed<br/>Clips ready for download"])

    FAIL(["❌ Job Failed"])

    style START fill:#7c3aed,color:#fff
    style DONE fill:#10b981,color:#fff
    style FAIL fill:#ef4444,color:#fff
```

## Highlight Detection Flow

How the AI analyzes transcripts and scores moments.

```mermaid
flowchart LR
    TRANSCRIPT["Full Transcript<br/>(timestamped segments)"] --> FORMAT["Format for LLM<br/>[MM:SS] (start-end) text"]
    FORMAT --> LLM["Send to LLM<br/>(system prompt + transcript)"]
    LLM --> PARSE["Parse JSON Response"]
    PARSE --> SCORE["Score & Rank<br/>(0.0 – 1.0)"]
    SCORE --> FILTER["Filter by<br/>duration constraints"]
    FILTER --> OUTPUT["Highlight List<br/>(start, end, score, title, reason)"]
```

## Data Flow Through Architecture Layers

```mermaid
sequenceDiagram
    participant U as 🖥️ Frontend
    participant A as 📡 API Server
    participant P as 🔄 Pipeline
    participant S as ⚙️ Services
    participant I as 🔌 Infrastructure

    U->>A: POST /api/jobs {url, detector, vertical}
    A->>A: Create Job (in-memory)
    A->>P: run_clip_pipeline(job)
    A-->>U: 201 {job_id, status: pending}

    Note over P,I: Background Thread

    P->>S: VideoIngestService.ingest(url)
    S->>I: YtdlpDownloader.download(url)
    I-->>S: VideoMetadata {path, title, duration}
    S-->>P: VideoMetadata

    P->>S: TranscriptService.transcribe(video)
    S->>I: FfmpegEditor.extract_audio()
    S->>I: WhisperEngine.transcribe()
    I-->>S: Transcript {segments[]}
    S-->>P: Transcript

    P->>S: HighlightService.detect(transcript)
    S->>I: GeminiDetector.detect() / OpenAI / Local
    I-->>S: Highlight[] {start, end, score, title, reason}
    S-->>P: Highlight[]

    P->>S: ClipService.generate_clips(highlights)
    S->>I: FfmpegEditor.cut() × N clips
    I-->>S: Clip[] {id, path, score, reason}
    S-->>P: Clip[]

    P->>S: SubtitleService.generate(clips)
    S->>I: SrtGenerator.generate() × N clips
    I-->>S: Clip[] with subtitle_path
    S-->>P: Clip[]

    P-->>A: Job {status: completed, clips[]}

    U->>A: GET /api/jobs/{id}
    A-->>U: JobDetail {clips with score, reason, urls}
```

## API Request Flow

```mermaid
flowchart LR
    subgraph "Client"
        BROWSER["🌐 Browser<br/>(localhost:3000)"]
    end

    subgraph "Backend (localhost:8000)"
        FASTAPI["FastAPI Router"]
        STATIC_C["/clips/ static files"]
        STATIC_S["/subtitles/ static files"]
    end

    BROWSER -->|"POST /api/jobs"| FASTAPI
    BROWSER -->|"GET /api/jobs"| FASTAPI
    BROWSER -->|"GET /api/jobs/:id"| FASTAPI
    BROWSER -->|"GET /api/detectors"| FASTAPI
    BROWSER -->|"GET /clips/:id.mp4"| STATIC_C
    BROWSER -->|"GET /subtitles/:id.srt"| STATIC_S
```

## Job State Machine

```mermaid
stateDiagram-v2
    [*] --> pending: Job Created
    pending --> downloading: Pipeline Start
    downloading --> transcribing: Video Downloaded
    transcribing --> detecting_highlights: Audio Transcribed
    detecting_highlights --> clipping: Highlights Found
    clipping --> generating_subtitles: Clips Cut
    generating_subtitles --> completed: Subtitles Ready

    downloading --> failed: Download Error
    transcribing --> failed: Whisper Error
    detecting_highlights --> failed: LLM Error
    clipping --> failed: FFmpeg Error
    generating_subtitles --> failed: SRT Error

    completed --> [*]
    failed --> [*]
```
