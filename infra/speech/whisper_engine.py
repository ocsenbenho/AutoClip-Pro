"""Whisper-based speech-to-text engine."""

from typing import Optional

import whisper

from core.errors import TranscriptionError
from core.logging import get_logger, log_operation
from core.models.transcript import Transcript, TranscriptSegment
from interfaces.speech_to_text import SpeechToText

logger = get_logger("infra.speech.whisper")


class WhisperEngine(SpeechToText):
    """Transcribes audio using OpenAI's Whisper model (local)."""

    def __init__(self, model_name: str = "base") -> None:
        """Initialize the Whisper engine.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large).
        """
        self._model_name = model_name
        self._model: Optional[whisper.Whisper] = None

    def _load_model(self) -> whisper.Whisper:
        """Lazily load the Whisper model."""
        if self._model is None:
            with log_operation(logger, f"Loading Whisper model '{self._model_name}'"):
                self._model = whisper.load_model(self._model_name)
        return self._model

    def transcribe(self, audio_path: str) -> Transcript:
        """Transcribe audio file into a timestamped transcript.

        Args:
            audio_path: Path to the audio file (wav, mp3, m4a, etc.).

        Returns:
            Transcript with timestamped segments.

        Raises:
            TranscriptionError: If transcription fails.
        """
        with log_operation(logger, f"Transcribing: {audio_path}"):
            try:
                model = self._load_model()
                result = model.transcribe(
                    audio_path,
                    verbose=False,
                    word_timestamps=False,
                )

                segments = [
                    TranscriptSegment(
                        start=seg["start"],
                        end=seg["end"],
                        text=seg["text"].strip(),
                    )
                    for seg in result.get("segments", [])
                    if seg.get("text", "").strip()
                ]

                return Transcript(
                    segments=segments,
                    language=result.get("language"),
                    duration=segments[-1].end if segments else 0.0,
                )
            except Exception as exc:
                raise TranscriptionError(f"Whisper transcription failed: {exc}") from exc
