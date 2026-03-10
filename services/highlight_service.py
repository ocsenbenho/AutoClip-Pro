"""Highlight detection service – analyzes transcript to find interesting moments."""

from core.config import settings
from core.logging import get_logger, log_operation
from core.models.highlight import Highlight
from core.models.transcript import Transcript
from interfaces.highlight_detector import HighlightDetector

logger = get_logger("services.highlight")


class HighlightService:
    """Orchestrates highlight detection and filters results."""

    def __init__(self, detector: HighlightDetector) -> None:
        self._detector = detector

    def detect_highlights(self, transcript: Transcript) -> list[Highlight]:
        """Analyze a transcript and return filtered, ranked highlights.

        Args:
            transcript: Full video transcript.

        Returns:
            List of highlights, filtered by duration constraints and capped at max_clips.
        """
        with log_operation(logger, "Detecting and filtering highlights"):
            raw_highlights = self._detector.detect(transcript)
            logger.info("Raw highlights detected: %d", len(raw_highlights))

            # Filter by duration constraints
            filtered: list[Highlight] = []
            for h in raw_highlights:
                duration = h.end - h.start
                if duration < settings.min_clip_duration:
                    logger.debug("Skipping highlight (too short: %.1fs): %s", duration, h.title)
                    continue
                if duration > settings.max_clip_duration:
                    logger.debug("Skipping highlight (too long: %.1fs): %s", duration, h.title)
                    continue
                filtered.append(h)

            # Remove overlapping highlights (keep higher-scored ones)
            filtered = self._remove_overlaps(filtered)

            # Cap at max clips
            result = filtered[: settings.max_clips]
            logger.info("Final highlights after filtering: %d", len(result))
            return result

    @staticmethod
    def _remove_overlaps(highlights: list[Highlight]) -> list[Highlight]:
        """Remove overlapping highlights, keeping the higher-scored one."""
        if not highlights:
            return []

        # Already sorted by score (descending) from detector
        kept: list[Highlight] = []
        for h in highlights:
            overlaps = any(
                h.start < existing.end and h.end > existing.start
                for existing in kept
            )
            if not overlaps:
                kept.append(h)
        return kept
