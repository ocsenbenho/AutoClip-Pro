"""Shared exception definitions for AutoClip Pro."""


class AutoClipError(Exception):
    """Base exception for all AutoClip Pro errors."""


class DownloadError(AutoClipError):
    """Raised when video download fails."""


class TranscriptionError(AutoClipError):
    """Raised when speech-to-text processing fails."""


class HighlightDetectionError(AutoClipError):
    """Raised when highlight detection fails."""


class ClipError(AutoClipError):
    """Raised when video clipping fails."""


class SubtitleError(AutoClipError):
    """Raised when subtitle generation fails."""


class PipelineError(AutoClipError):
    """Raised when a pipeline step fails."""
