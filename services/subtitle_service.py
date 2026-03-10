"""Subtitle generation service – creates SRT files for clips."""

from core.config import settings
from core.logging import get_logger, log_operation
from core.models.clip import Clip
from core.models.transcript import Transcript, TranscriptSegment
from interfaces.subtitle_generator import SubtitleGenerator

logger = get_logger("services.subtitle")


class SubtitleService:
    """Generates subtitle files for video clips."""

    def __init__(self, generator: SubtitleGenerator) -> None:
        self._generator = generator

    def generate_for_clip(self, clip: Clip, transcript: Transcript) -> Clip:
        """Generate an SRT subtitle file for a clip.

        Extracts transcript segments that fall within the clip's time range,
        adjusts timestamps to be relative to the clip start, and writes SRT.

        Args:
            clip: The clip to generate subtitles for.
            transcript: The full video transcript.

        Returns:
            Updated Clip with subtitle_path set.
        """
        with log_operation(logger, f"Generating subtitles for clip: {clip.title}"):
            settings.ensure_dirs()

            # Extract segments within the clip's time range
            matching_segments = self._extract_segments(transcript, clip.start, clip.end)

            # Adjust timestamps relative to clip start
            adjusted_segments = [
                TranscriptSegment(
                    start=max(0.0, seg.start - clip.start),
                    end=min(clip.duration, seg.end - clip.start),
                    text=seg.text,
                )
                for seg in matching_segments
            ]

            if not adjusted_segments:
                logger.warning("No transcript segments found for clip: %s", clip.title)
                return clip

            # Generate SRT file
            output_path = str(settings.subtitle_dir / f"{clip.id}.srt")
            self._generator.generate(adjusted_segments, output_path)

            # Return updated clip
            return clip.model_copy(update={"subtitle_path": output_path})

    @staticmethod
    def _extract_segments(
        transcript: Transcript,
        start: float,
        end: float,
    ) -> list[TranscriptSegment]:
        """Extract transcript segments that overlap with the given time range."""
        return [
            seg
            for seg in transcript.segments
            if seg.end > start and seg.start < end
        ]
