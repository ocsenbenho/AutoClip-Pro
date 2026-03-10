"""Speech-to-text interface contract."""

from abc import ABC, abstractmethod

from core.models.transcript import Transcript


class SpeechToText(ABC):
    """Abstract base class for speech-to-text engines."""

    @abstractmethod
    def transcribe(self, audio_path: str) -> Transcript:
        """Transcribe an audio file into a timestamped transcript.

        Args:
            audio_path: Path to the audio file.

        Returns:
            Transcript containing timestamped segments.
        """
        ...
