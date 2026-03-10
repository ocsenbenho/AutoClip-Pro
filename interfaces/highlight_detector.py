"""Highlight detector interface contract."""

from abc import ABC, abstractmethod

from core.models.highlight import Highlight
from core.models.transcript import Transcript


class HighlightDetector(ABC):
    """Abstract base class for highlight detection engines."""

    @abstractmethod
    def detect(self, transcript: Transcript) -> list[Highlight]:
        """Analyze a transcript and detect highlight-worthy moments.

        Args:
            transcript: The full video transcript.

        Returns:
            List of detected highlights with timestamps and scores.
        """
        ...
