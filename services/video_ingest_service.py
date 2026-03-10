"""Video ingest service – downloads and stores videos."""

from core.config import settings
from core.errors import DownloadError
from core.logging import get_logger, log_operation
from core.models.video import VideoMetadata
from interfaces.downloader import Downloader

logger = get_logger("services.video_ingest")


class VideoIngestService:
    """Manages video downloading and local storage."""

    def __init__(self, downloader: Downloader) -> None:
        self._downloader = downloader

    def ingest(self, url: str) -> VideoMetadata:
        """Download a video from the given URL and store it locally.

        Args:
            url: Video URL to download.

        Returns:
            VideoMetadata with file path and info.

        Raises:
            DownloadError: If validation or download fails.
        """
        with log_operation(logger, f"Ingesting video: {url}"):
            # Validate URL
            if not url or not url.startswith(("http://", "https://")):
                raise DownloadError(f"Invalid URL: {url}")

            # Ensure output directory exists
            settings.ensure_dirs()

            # Download via infrastructure adapter
            metadata = self._downloader.download(url, str(settings.video_dir))
            logger.info("Video saved: %s (%s, %.0fs)", metadata.title, metadata.file_path, metadata.duration)
            return metadata
