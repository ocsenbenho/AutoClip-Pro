"""Subtitle generator interface contract."""

from abc import ABC, abstractmethod

from core.models.transcript import TranscriptSegment


class SubtitleGenerator(ABC):
    """Abstract base class for subtitle generators."""

    @abstractmethod
    def generate(self, segments: list[TranscriptSegment], output_path: str) -> str:
        """Generate a subtitle file from transcript segments.

        Args:
            segments: List of transcript segments with timestamps.
            output_path: Path to write the subtitle file to.

        Returns:
            Path to the generated subtitle file.
        """
        ...
