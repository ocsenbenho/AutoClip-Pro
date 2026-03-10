"""yt-dlp based video downloader implementation.

Implements a multi-strategy download approach to handle YouTube's
SABR streaming enforcement and format restrictions.
"""

import glob
import os
import uuid

import yt_dlp

from core.errors import DownloadError
from core.logging import get_logger, log_operation
from core.models.video import VideoMetadata
from interfaces.downloader import Downloader

logger = get_logger("infra.download.ytdlp")

# Path to cookies file (Netscape format)
COOKIES_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "cookies.txt")


class YtdlpDownloader(Downloader):
    """Downloads videos from YouTube (and other platforms) using yt-dlp.

    Uses a fallback strategy:
    1. Try with cookies + default clients  (best quality if JS runtime available)
    2. Fall back without cookies            (android_vr client, ~240p)
    """

    def download(self, url: str, output_dir: str) -> VideoMetadata:
        video_id = uuid.uuid4().hex[:12]
        output_template = f"{output_dir}/{video_id}.%(ext)s"
        cookies_path = os.path.abspath(COOKIES_FILE)

        # ── Build strategy list ───────────────────────────
        strategies = []

        # Strategy 1: cookies + best format (needs JS runtime for full quality)
        if os.path.isfile(cookies_path):
            strategies.append({
                "name": "cookies + best format",
                "cookiefile": cookies_path,
                "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            })

        # Strategy 2: no cookies (ios / android fallback)
        strategies.append({
            "name": "no-cookies fallback",
            "format": "best[ext=mp4]/best",
            "extractor_args": {
                "youtube": {
                    "player_client": ["ios", "android_vr"]
                }
            }
        })

        with log_operation(logger, f"Downloading video from {url}"):
            last_error = None

            for strategy in strategies:
                name = strategy.pop("name")
                logger.info("Trying strategy: %s", name)

                ydl_opts = {
                    "outtmpl": output_template,
                    "merge_output_format": "mp4",
                    "quiet": True,
                    "no_warnings": True,
                    "noplaylist": True,
                    "retries": 5,
                    "fragment_retries": 5,
                    "http_headers": {
                        "User-Agent": (
                            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                            "AppleWebKit/537.36 (KHTML, like Gecko) "
                            "Chrome/120.0.0.0 Safari/537.36"
                        ),
                    },
                    **strategy,
                }

                try:
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        info = ydl.extract_info(url, download=True)
                        if info is None:
                            raise yt_dlp.utils.DownloadError(
                                "extract_info returned None"
                            )

                        file_path = self._resolve_file_path(
                            ydl, info, output_dir, video_id
                        )

                        logger.info(
                            "✅ Downloaded via '%s': %s (%s)",
                            name,
                            info.get("title"),
                            info.get("format", "?"),
                        )

                        return VideoMetadata(
                            id=video_id,
                            title=info.get("title", "Unknown"),
                            url=url,
                            file_path=file_path,
                            duration=float(info.get("duration", 0)),
                            thumbnail_url=info.get("thumbnail"),
                            description=info.get("description"),
                        )

                except (yt_dlp.utils.DownloadError, yt_dlp.utils.ExtractorError) as exc:
                    last_error = exc
                    logger.warning("Strategy '%s' failed: %s", name, str(exc)[:120])
                    # Clean up partial downloads before trying next strategy
                    for f in glob.glob(f"{output_dir}/{video_id}.*"):
                        os.remove(f)
                    continue

            # All strategies failed
            raise DownloadError(
                f"All download strategies failed. Last error: {last_error}"
            )

    @staticmethod
    def _resolve_file_path(
        ydl: yt_dlp.YoutubeDL, info: dict, output_dir: str, video_id: str
    ) -> str:
        """Determine the actual file path after download."""
        file_path = ydl.prepare_filename(info)

        # yt-dlp may change extension after merge
        if not file_path.endswith(".mp4"):
            base = file_path.rsplit(".", 1)[0]
            mp4_path = base + ".mp4"
            if os.path.isfile(mp4_path):
                file_path = mp4_path

        if not os.path.isfile(file_path):
            matches = glob.glob(f"{output_dir}/{video_id}.*")
            if matches:
                file_path = matches[0]
            else:
                raise DownloadError("Download completed but file not found")

        return file_path
