"""FFmpeg-based video editor implementation."""

import subprocess

from core.errors import ClipError
from core.logging import get_logger, log_operation
from interfaces.video_editor import VideoEditor

logger = get_logger("infra.video.ffmpeg")


class FfmpegEditor(VideoEditor):
    """Edits videos using FFmpeg via subprocess."""

    def cut(self, video_path: str, start: float, end: float, output_path: str) -> str:
        """Cut a segment from a video using FFmpeg.

        Uses stream copy for speed (no re-encoding). Falls back to
        re-encoding if stream copy produces artifacts.

        Args:
            video_path: Path to the source video.
            start: Start time in seconds.
            end: End time in seconds.
            output_path: Path for the output clip.

        Returns:
            Path to the generated clip.

        Raises:
            ClipError: If FFmpeg fails.
        """
        duration = end - start

        with log_operation(logger, f"Cutting clip {start:.1f}s-{end:.1f}s"):
            cmd = [
                "ffmpeg",
                "-y",
                "-ss", str(start),
                "-i", video_path,
                "-t", str(duration),
                "-c", "copy",
                "-avoid_negative_ts", "make_zero",
                output_path,
            ]
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode != 0:
                    logger.warning("Stream copy failed, falling back to re-encode")
                    cmd_reencode = [
                        "ffmpeg",
                        "-y",
                        "-ss", str(start),
                        "-i", video_path,
                        "-t", str(duration),
                        "-c:v", "libx264",
                        "-preset", "fast",
                        "-c:a", "aac",
                        output_path,
                    ]
                    result = subprocess.run(
                        cmd_reencode,
                        capture_output=True,
                        text=True,
                        timeout=300,
                    )
                    if result.returncode != 0:
                        raise ClipError(f"FFmpeg re-encode failed: {result.stderr}")

                return output_path
            except subprocess.TimeoutExpired as exc:
                raise ClipError(f"FFmpeg timed out: {exc}") from exc
            except FileNotFoundError:
                raise ClipError("FFmpeg not found. Please install FFmpeg: brew install ffmpeg")
            except Exception as exc:
                raise ClipError(f"FFmpeg error: {exc}") from exc

    def extract_audio(self, video_path: str, output_path: str) -> str:
        """Extract audio track from a video file.

        Args:
            video_path: Path to the source video.
            output_path: Path for the output audio file.

        Returns:
            Path to the extracted audio file.

        Raises:
            ClipError: If FFmpeg fails.
        """
        with log_operation(logger, f"Extracting audio from {video_path}"):
            cmd = [
                "ffmpeg",
                "-y",
                "-i", video_path,
                "-vn",
                "-acodec", "pcm_s16le",
                "-ar", "16000",
                "-ac", "1",
                output_path,
            ]
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                )
                if result.returncode != 0:
                    raise ClipError(f"Audio extraction failed: {result.stderr}")
                return output_path
            except subprocess.TimeoutExpired as exc:
                raise ClipError(f"FFmpeg audio extraction timed out: {exc}") from exc
            except FileNotFoundError:
                raise ClipError("FFmpeg not found. Please install FFmpeg: brew install ffmpeg")
            except Exception as exc:
                raise ClipError(f"Audio extraction error: {exc}") from exc

    def format_vertical(self, video_path: str, output_path: str) -> str:
        """Crop a landscape video to a 9:16 vertical aspect ratio dynamically.

        Uses the AutoReframe module to track faces and pan smoothly instead
        of a static center crop.

        Args:
            video_path: Path to the source video.
            output_path: Path for the output vertical clip.

        Returns:
            Path to the vertical clip.

        Raises:
            ClipError: If processing fails.
        """
        from infra.video.auto_reframe import AutoReframe
        
        reframe = AutoReframe(target_aspect_ratio=9/16)
        return reframe.process(video_path, output_path)

    def get_info(self, video_path: str) -> dict:
        """Get video metadata using ffprobe.
        
        Args:
            video_path: Path to the video file.
            
        Returns:
            Dictionary containing 'duration' and other metadata.
            
        Raises:
            ClipError: If ffprobe fails.
        """
        import json
        with log_operation(logger, f"Getting info for {video_path}"):
            cmd = [
                "ffprobe",
                "-v", "quiet",
                "-print_format", "json",
                "-show_format",
                "-show_streams",
                video_path
            ]
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30,
                )
                if result.returncode != 0:
                    raise ClipError(f"ffprobe failed: {result.stderr}")
                
                data = json.loads(result.stdout)
                format_info = data.get("format", {})
                duration = float(format_info.get("duration", 0.0))
                return {
                    "duration": duration,
                    "format_name": format_info.get("format_name"),
                    "tags": format_info.get("tags", {})
                }
            except Exception as exc:
                raise ClipError(f"ffprobe error: {exc}") from exc
