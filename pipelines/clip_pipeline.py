"""Clip generation pipeline – the primary video processing workflow.

Pipeline flow:
    Video URL → Download → Transcribe → Detect Highlights → Cut Clips → Generate Subtitles
"""

from core.config import settings
from core.errors import PipelineError
from core.logging import get_logger, log_operation
from core.models.clip import Clip
from core.models.job import Job, JobStatus
from infra.download.ytdlp_downloader import YtdlpDownloader
from infra.llm.local_detector import LocalHighlightDetector
from infra.llm.openai_client import OpenAIHighlightDetector
from infra.llm.gemini_client import GeminiHighlightDetector
from infra.speech.whisper_engine import WhisperEngine
from infra.subtitle.srt_generator import SrtGenerator
from infra.video.ffmpeg_editor import FfmpegEditor
from interfaces.highlight_detector import HighlightDetector
from services.clip_service import ClipService
from services.highlight_service import HighlightService
from services.subtitle_service import SubtitleService
from services.transcript_service import TranscriptService
from services.video_ingest_service import VideoIngestService

logger = get_logger("pipelines.clip")

# Supported detector types
DETECTOR_LOCAL = "local"
DETECTOR_OPENAI = "openai"
DETECTOR_GEMINI = "gemini"

AVAILABLE_DETECTORS = {
    DETECTOR_LOCAL: "Local Analysis (Free, no API key needed)",
    DETECTOR_OPENAI: "OpenAI GPT (Better quality, requires API key)",
    DETECTOR_GEMINI: "Google Gemini (Fast & free tier, requires API key)",
}


def _create_detector(detector_type: str) -> HighlightDetector:
    """Create the appropriate highlight detector based on type.

    Args:
        detector_type: One of 'local', 'openai', or 'gemini'.

    Returns:
        An initialized HighlightDetector instance.

    Raises:
        PipelineError: If the detector type is invalid or misconfigured.
    """
    if detector_type == DETECTOR_OPENAI:
        if not settings.openai_api_key:
            raise PipelineError(
                "OpenAI API key not configured. "
                "Set AUTOCLIP_OPENAI_API_KEY environment variable, "
                "or use 'local' detector."
            )
        logger.info("Using OpenAI detector (model: %s)", settings.openai_model)
        return OpenAIHighlightDetector(
            api_key=settings.openai_api_key,
            model=settings.openai_model,
        )

    if detector_type == DETECTOR_GEMINI:
        if not settings.gemini_api_key:
            raise PipelineError(
                "Gemini API key not configured. "
                "Set AUTOCLIP_GEMINI_API_KEY environment variable, "
                "or use 'local' detector."
            )
        logger.info("Using Gemini detector (model: %s)", settings.gemini_model)
        return GeminiHighlightDetector(
            api_key=settings.gemini_api_key,
            model=settings.gemini_model,
        )

    if detector_type == DETECTOR_LOCAL:
        logger.info("Using local highlight detector")
        return LocalHighlightDetector()

    raise PipelineError(
        f"Unknown detector type: '{detector_type}'. "
        f"Available: {list(AVAILABLE_DETECTORS.keys())}"
    )


def run_clip_pipeline(
    job: Job,
    on_status_update=None,
    detector_type: str = DETECTOR_LOCAL,
    vertical_format: bool = False,
) -> Job:
    """Execute the full clip generation pipeline.

    Args:
        job: The processing job to execute.
        on_status_update: Optional callback(job) for status updates.
        detector_type: Which highlight detector to use ('local' or 'openai').
        vertical_format: Whether to crop the output clips to 9:16 vertical.

    Returns:
        Updated Job with clips.

    Raises:
        PipelineError: If any pipeline step fails.
    """
    def update_status(status: JobStatus, message: str) -> None:
        job.status = status
        job.progress_message = message
        if on_status_update:
            on_status_update(job)

    with log_operation(logger, f"Clip pipeline for job {job.id}"):
        try:
            # ── Wire up infrastructure ────────────────────────────
            downloader = YtdlpDownloader()
            whisper = WhisperEngine(model_name=settings.whisper_model)
            ffmpeg = FfmpegEditor()
            srt_gen = SrtGenerator()
            highlight_detector = _create_detector(detector_type)

            # ── Wire up services ──────────────────────────────────
            ingest_svc = VideoIngestService(downloader)
            transcript_svc = TranscriptService(whisper, ffmpeg)
            highlight_svc = HighlightService(highlight_detector)
            clip_svc = ClipService(ffmpeg)
            subtitle_svc = SubtitleService(srt_gen)

            # ── Step 1: Download video ────────────────────────────
            update_status(JobStatus.DOWNLOADING, "Downloading video...")
            video = ingest_svc.ingest(job.video_url)
            job.video = video

            # ── Step 2: Transcribe audio ──────────────────────────
            update_status(JobStatus.TRANSCRIBING, "Transcribing audio...")
            transcript = transcript_svc.transcribe_video(video.file_path)

            # ── Step 3: Detect highlights ─────────────────────────
            detector_label = AVAILABLE_DETECTORS.get(detector_type, detector_type)
            update_status(
                JobStatus.DETECTING_HIGHLIGHTS,
                f"Analyzing transcript with {detector_label}...",
            )
            highlights = highlight_svc.detect_highlights(transcript)

            if not highlights:
                update_status(JobStatus.COMPLETED, "No highlights detected")
                return job

            # ── Step 4: Cut clips ─────────────────────────────────
            update_status(JobStatus.CLIPPING, f"Cutting {len(highlights)} clips...")
            clips = clip_svc.generate_clips(video.file_path, video.id, highlights)

            # ── Step 4.5: Format vertical (optional) ──────────────
            if vertical_format:
                update_status(JobStatus.CLIPPING, f"Formatting {len(clips)} clips to vertical 9:16...")
                vertical_clips: list[Clip] = []
                for clip in clips:
                    # Create a new path for the vertical version
                    v_path = clip.file_path.replace(".mp4", "_vertical.mp4")
                    ffmpeg.format_vertical(clip.file_path, v_path)
                    
                    # Optional cleanup of original landscape clip
                    import os
                    try:
                        os.remove(clip.file_path)
                    except OSError:
                        pass
                        
                    clip.file_path = v_path
                    vertical_clips.append(clip)
                clips = vertical_clips

            # ── Step 5: Generate subtitles ────────────────────────
            update_status(JobStatus.GENERATING_SUBTITLES, "Generating subtitles...")
            clips_with_subs: list[Clip] = []
            for clip in clips:
                updated_clip = subtitle_svc.generate_for_clip(clip, transcript)
                clips_with_subs.append(updated_clip)

            # ── Done ──────────────────────────────────────────────
            job.clips = clips_with_subs
            update_status(JobStatus.COMPLETED, f"Done! Generated {len(clips_with_subs)} clips.")
            return job

        except Exception as exc:
            job.status = JobStatus.FAILED
            job.error = str(exc)
            job.progress_message = f"Pipeline failed: {exc}"
            if on_status_update:
                on_status_update(job)
            logger.error("Pipeline failed for job %s: %s", job.id, exc)
            raise PipelineError(f"Clip pipeline failed: {exc}") from exc
