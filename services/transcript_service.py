"""Transcript service – extracts audio and transcribes speech."""

import os
import tempfile

from core.errors import TranscriptionError
from core.logging import get_logger, log_operation
from core.models.transcript import Transcript
from interfaces.speech_to_text import SpeechToText
from interfaces.video_editor import VideoEditor

logger = get_logger("services.transcript")


class TranscriptService:
    """Manages audio extraction and speech-to-text transcription."""

    def __init__(self, stt_engine: SpeechToText, video_editor: VideoEditor) -> None:
        self._stt = stt_engine
        self._editor = video_editor

    def transcribe_video(self, video_path: str) -> Transcript:
        """Extract audio from a video and produce a timestamped transcript.

        Args:
            video_path: Path to the video file.

        Returns:
            Transcript with timestamped segments.

        Raises:
            TranscriptionError: If extraction or transcription fails.
        """
        with log_operation(logger, f"Transcribing video: {video_path}"):
            if not os.path.isfile(video_path):
                raise TranscriptionError(f"Video file not found: {video_path}")

            # Extract audio to a temporary WAV file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                audio_path = tmp.name

            try:
                self._editor.extract_audio(video_path, audio_path)
                transcript = self._stt.transcribe(audio_path)
                logger.info(
                    "Transcription complete: %d segments, language=%s",
                    len(transcript.segments),
                    transcript.language,
                )
                return transcript
            finally:
                # Clean up temporary audio file
                if os.path.exists(audio_path):
                    os.unlink(audio_path)
