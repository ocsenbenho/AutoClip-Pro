# 🏗️ System Architecture

AutoClip Pro follows a **layered clean architecture** where each layer has strict responsibilities and dependencies flow in one direction only.

## Architecture Diagram

```mermaid
graph TD
    subgraph "🖥️ Apps Layer"
        API["FastAPI Server<br/>(apps/api)"]
    end

    subgraph "🔄 Pipelines Layer"
        CP["Clip Pipeline<br/>(pipelines/clip_pipeline.py)"]
    end

    subgraph "⚙️ Services Layer"
        VIS["Video Ingest<br/>Service"]
        TS["Transcript<br/>Service"]
        HS["Highlight<br/>Service"]
        CS["Clip<br/>Service"]
        SS["Subtitle<br/>Service"]
    end

    subgraph "🔌 Infrastructure Layer"
        YTDLP["yt-dlp<br/>Downloader"]
        WHISPER["Whisper<br/>Engine"]
        OPENAI["OpenAI<br/>Client"]
        GEMINI["Gemini<br/>Client"]
        LOCAL["Local<br/>Detector"]
        FFMPEG["FFmpeg<br/>Editor"]
        SRT["SRT<br/>Generator"]
    end

    subgraph "📋 Interfaces Layer"
        ID["Downloader"]
        ISTT["SpeechToText"]
        IHD["HighlightDetector"]
        IVE["VideoEditor"]
    end

    subgraph "🧱 Core Layer"
        MODELS["Data Models"]
        CONFIG["Configuration"]
        LOG["Logging"]
        ERR["Errors"]
    end

    API --> CP
    CP --> VIS --> YTDLP --> ID
    CP --> TS --> WHISPER --> ISTT
    TS --> FFMPEG
    CP --> HS --> OPENAI --> IHD
    HS --> GEMINI --> IHD
    HS --> LOCAL --> IHD
    CP --> CS --> FFMPEG --> IVE
    CP --> SS --> SRT

    ID --> MODELS
    ISTT --> MODELS
    IHD --> MODELS
    IVE --> MODELS
    CONFIG --> MODELS
```

## Dependency Direction

All dependencies **must** follow this direction (top → bottom):

```
apps → pipelines → services → infra → interfaces → core
```

**Forbidden:**
- `core` importing `services` ❌
- `infra` importing `services` ❌
- `services` importing `pipelines` ❌

## Layer Descriptions

### Core (`core/`)
Fundamental building blocks: data models, configuration, logging, shared exceptions.
Core **must not** depend on any other module.

### Interfaces (`interfaces/`)
Abstract contracts that define system boundaries:
- `Downloader` — video download contract
- `SpeechToText` — transcription contract
- `HighlightDetector` — AI analysis contract
- `VideoEditor` — video editing contract

### Infrastructure (`infra/`)
External integrations that implement interfaces:
- `yt-dlp` — YouTube downloader with multi-strategy fallback
- `Whisper` — OpenAI speech-to-text engine
- `OpenAI / Gemini / Local` — highlight detection engines
- `FFmpeg` — video cutting, encoding, and vertical formatting

### Services (`services/`)
Business logic orchestrating infra components:
- `VideoIngestService` — manages video download flow
- `TranscriptService` — handles audio extraction + transcription
- `HighlightService` — coordinates highlight detection
- `ClipService` — generates clips from highlights
- `SubtitleService` — creates SRT subtitles per clip

### Pipelines (`pipelines/`)
Workflow orchestration calling services in sequence.

### Apps (`apps/`)
Entry points: FastAPI server, background workers.

## Frontend Architecture

```mermaid
graph LR
    subgraph "Next.js 15 App"
        HP["Home Page<br/>(URL Input + Job Submit)"]
        JL["Jobs List<br/>(All Jobs Overview)"]
        JD["Job Detail<br/>(Pipeline Progress + Clip Cards)"]
    end

    subgraph "Backend API"
        JOBS_EP["/api/jobs"]
        DET_EP["/api/detectors"]
        CLIP_EP["/clips/"]
        SUB_EP["/subtitles/"]
    end

    HP -->|POST| JOBS_EP
    HP -->|GET| DET_EP
    JL -->|GET| JOBS_EP
    JD -->|GET| JOBS_EP
    JD -->|GET| CLIP_EP
    JD -->|GET| SUB_EP
```
