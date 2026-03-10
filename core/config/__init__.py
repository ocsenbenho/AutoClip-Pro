"""Centralized application settings loaded from environment variables."""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration. Values are loaded from environment variables."""

    # ── Paths ──────────────────────────────────────────────────────
    project_root: Path = Path(__file__).resolve().parent.parent.parent
    data_dir: Path = Path(__file__).resolve().parent.parent.parent / "data"
    video_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "videos"
    clip_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "clips"
    subtitle_dir: Path = Path(__file__).resolve().parent.parent.parent / "data" / "subtitles"

    # ── Whisper ────────────────────────────────────────────────────
    whisper_model: str = "base"

    # ── OpenAI / Gemini / LLM ────────────────────────────────────
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"

    # ── Clip constraints ──────────────────────────────────────────
    min_clip_duration: float = 15.0
    max_clip_duration: float = 90.0
    max_clips: int = 10

    # ── API ────────────────────────────────────────────────────────
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_origins: list[str] = ["http://localhost:3000"]

    model_config = {"env_prefix": "AUTOCLIP_", "env_file": ".env", "extra": "ignore"}

    def ensure_dirs(self) -> None:
        """Create all required output directories."""
        self.video_dir.mkdir(parents=True, exist_ok=True)
        self.clip_dir.mkdir(parents=True, exist_ok=True)
        self.subtitle_dir.mkdir(parents=True, exist_ok=True)


settings = Settings()
