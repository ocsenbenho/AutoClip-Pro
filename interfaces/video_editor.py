"""Video editor interface contract."""

from abc import ABC, abstractmethod


class VideoEditor(ABC):
    """Abstract base class for video editing engines."""

    @abstractmethod
    def cut(self, video_path: str, start: float, end: float, output_path: str) -> str:
        """Cut a segment from a video file.

        Args:
            video_path: Path to the source video.
            start: Start time in seconds.
            end: End time in seconds.
            output_path: Path for the output clip.

        Returns:
            Path to the generated clip file.
        """
        ...

    @abstractmethod
    def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio from a video file.

        Args:
            video_path: Path to the source video.
            output_path: Path for the output audio file.

        Returns:
            Path to the extracted audio file.
        """
        ...

    @abstractmethod
    def format_vertical(self, video_path: str, output_path: str) -> str:
        """Crop a landscape video to a 9:16 vertical aspect ratio.

        Args:
            video_path: Path to the source video.
            output_path: Path for the output vertical clip.

        Returns:
            Path to the vertical clip.
        """
        ...
