"""SRT subtitle file generator."""

from core.errors import SubtitleError
from core.logging import get_logger, log_operation
from core.models.transcript import TranscriptSegment
from interfaces.subtitle_generator import SubtitleGenerator

logger = get_logger("infra.subtitle.srt")


def _format_srt_time(seconds: float) -> str:
    """Convert seconds to SRT timestamp format (HH:MM:SS,mmm).

    Args:
        seconds: Time in seconds.

    Returns:
        SRT-formatted timestamp string.
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"


class SrtGenerator(SubtitleGenerator):
    """Generates SRT subtitle files from transcript segments."""

    def generate(self, segments: list[TranscriptSegment], output_path: str) -> str:
        """Generate an SRT subtitle file from transcript segments.

        Args:
            segments: List of transcript segments with timestamps.
            output_path: Path to write the SRT file.

        Returns:
            Path to the generated SRT file.

        Raises:
            SubtitleError: If file writing fails.
        """
        with log_operation(logger, f"Generating SRT: {output_path}"):
            try:
                srt_blocks: list[str] = []
                for idx, seg in enumerate(segments, start=1):
                    start_ts = _format_srt_time(seg.start)
                    end_ts = _format_srt_time(seg.end)
                    block = f"{idx}\n{start_ts} --> {end_ts}\n{seg.text}\n"
                    srt_blocks.append(block)

                srt_content = "\n".join(srt_blocks)

                with open(output_path, "w", encoding="utf-8") as f:
                    f.write(srt_content)

                logger.info("Generated SRT with %d segments", len(segments))
                return output_path
            except Exception as exc:
                raise SubtitleError(f"SRT generation failed: {exc}") from exc
