"""Downloader interface contract."""

from abc import ABC, abstractmethod

from core.models.video import VideoMetadata


class Downloader(ABC):
    """Abstract base class for video downloaders."""

    @abstractmethod
    def download(self, url: str, output_dir: str) -> VideoMetadata:
        """Download a video from the given URL.

        Args:
            url: Video URL to download.
            output_dir: Directory to save the video to.

        Returns:
            VideoMetadata with file path and metadata.
        """
        ...
