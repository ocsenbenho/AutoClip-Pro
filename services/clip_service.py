"""Clip generation service – cuts video into highlight clips."""

import uuid

from core.config import settings
from core.logging import get_logger, log_operation
from core.models.clip import Clip
from core.models.highlight import Highlight
from interfaces.video_editor import VideoEditor

logger = get_logger("services.clip")


class ClipService:
    """Generates individual video clips from detected highlights."""

    def __init__(self, editor: VideoEditor) -> None:
        self._editor = editor

    def generate_clips(
        self,
        video_path: str,
        video_id: str,
        highlights: list[Highlight],
    ) -> list[Clip]:
        """Cut video into clips based on highlight timestamps.

        Args:
            video_path: Path to the source video.
            video_id: ID of the source video.
            highlights: List of highlights with timestamps.

        Returns:
            List of generated Clip objects.
        """
        with log_operation(logger, f"Generating {len(highlights)} clips"):
            settings.ensure_dirs()
            clips: list[Clip] = []

            for idx, highlight in enumerate(highlights, start=1):
                clip_id = uuid.uuid4().hex[:12]
                output_path = str(settings.clip_dir / f"{clip_id}.mp4")

                # Add 0.5s padding to prevent audio cutting off abruptly
                start_padded = max(0.0, highlight.start - 0.5)
                end_padded = highlight.end + 0.5

                logger.info(
                    "Cutting clip %d/%d: %s (%.1fs-%.1fs)",
                    idx, len(highlights), highlight.title, start_padded, end_padded,
                )

                self._editor.cut(video_path, start_padded, end_padded, output_path)

                clip = Clip(
                    id=clip_id,
                    source_video_id=video_id,
                    title=highlight.title,
                    start=start_padded,
                    end=end_padded,
                    duration=end_padded - start_padded,
                    file_path=output_path,
                    score=highlight.score,
                    reason=highlight.reason,
                )
                clips.append(clip)

            logger.info("Generated %d clips successfully", len(clips))
            return clips
