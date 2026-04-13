"""Auto Reframe module using OpenCV for dynamic face tracking and cropping."""

import os
import subprocess

import cv2
import numpy as np

from core.errors import ClipError
from core.logging import get_logger, log_operation

logger = get_logger("infra.video.auto_reframe")


class AutoReframe:
    """Dynamically crops a landscape video to a vertical format by tracking faces."""

    def __init__(self, target_aspect_ratio: float = 9 / 16) -> None:
        """Initialize AutoReframe.

        Args:
            target_aspect_ratio: The target aspect ratio (width / height).
        """
        self._target_ratio = target_aspect_ratio
        
        cascades_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._face_cascade = cv2.CascadeClassifier(cascades_path)
        
        if self._face_cascade.empty():
            logger.error("Failed to load OpenCV face cascade from %s", cascades_path)

    def process(self, video_path: str, output_path: str) -> str:
        """Process video and dynamically crop to target aspect ratio.

        Args:
            video_path: Source landscape video.
            output_path: Destination vertical video.

        Returns:
            The output path.
            
        Raises:
            ClipError: If processing or FFmpeg muxing fails.
        """
        with log_operation(logger, f"Auto-reframing {video_path}"):
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ClipError(f"Cannot open video for auto-reframe: {video_path}")

            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # If FPS is 0 or invalid, default to 30
            if fps <= 0:
                fps = 30.0

            target_width = int(height * self._target_ratio)
            # Ensure target_width is even for FFmpeg compatibility
            if target_width % 2 != 0:
                target_width -= 1

            if target_width >= width:
                # Video is already vertical or too narrow, fallback to standard FFmpeg crop
                logger.warning("Video too narrow for auto-reframe, using static crop")
                cap.release()
                return self._fallback_crop(video_path, output_path)

            temp_video_path = f"{output_path}_tmp_video.mp4"
            # Use 'avc1' or 'mp4v' for MP4
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out = cv2.VideoWriter(temp_video_path, fourcc, fps, (target_width, height))

            if not out.isOpened():
                cap.release()
                raise ClipError(f"Failed to open VideoWriter for {temp_video_path}")

            # Smoothing parameters
            alpha = 0.05  # Lower = smoother but slower to track
            current_x_center = width / 2.0
            smoothed_x_center = width / 2.0

            frame_idx = 0
            # Detect faces every half-second instead of every frame to save CPU
            detection_interval = max(1, int(fps / 2))
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % detection_interval == 0 and not self._face_cascade.empty():
                    # Detect face
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    # Optimize detection speed by shrinking the image 50%
                    small_gray = cv2.resize(gray, (0, 0), fx=0.5, fy=0.5)
                    faces = self._face_cascade.detectMultiScale(
                        small_gray, 
                        scaleFactor=1.1, 
                        minNeighbors=5, 
                        minSize=(30, 30)
                    )
                    
                    if len(faces) > 0:
                        # Find the largest face (w * h)
                        largest_face = max(faces, key=lambda f: f[2] * f[3])
                        x, y, w, h = largest_face
                        # Scale coordinates back up
                        current_x_center = (x + w / 2.0) * 2.0

                # Smooth the camera movement
                smoothed_x_center = alpha * current_x_center + (1.0 - alpha) * smoothed_x_center

                # Calculate crop bounds
                start_x = int(smoothed_x_center - target_width / 2.0)
                end_x = start_x + target_width

                # Constrain to frame boundaries
                if start_x < 0:
                    start_x = 0
                    end_x = target_width
                elif end_x > width:
                    end_x = width
                    start_x = width - target_width

                # Crop frame
                cropped_frame = frame[:, start_x:end_x]
                out.write(cropped_frame)
                
                frame_idx += 1

            cap.release()
            out.release()

            # Merge audio back using FFmpeg
            self._merge_audio(video_path, temp_video_path, output_path)
            
            # Cleanup temp video
            if os.path.exists(temp_video_path):
                try:
                    os.remove(temp_video_path)
                except OSError:
                    pass

            return output_path

    def _merge_audio(self, original_video: str, new_video: str, output: str) -> None:
        """Merge the original audio with the newly cropped video."""
        cmd = [
            "ffmpeg", "-y",
            "-i", new_video,
            "-i", original_video,
            "-c:v", "libx264", 
            "-preset", "fast",  # Re-encode video for better web compatibility
            "-c:a", "aac",
            "-map", "0:v:0", 
            "-map", "1:a:0",
            "-shortest", 
            output
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if res.returncode != 0:
                raise ClipError(f"Failed to merge audio after reframe: {res.stderr}")
        except subprocess.TimeoutExpired as exc:
            raise ClipError(f"FFmpeg muxing timed out: {exc}") from exc
        except Exception as exc:
            raise ClipError(f"Merge audio error: {exc}") from exc

    def _fallback_crop(self, video_path: str, output_path: str) -> str:
        """Standard ffmpeg crop if video is already vertical or we can't reframe."""
        cmd = [
            "ffmpeg", "-y", 
            "-i", video_path,
            "-vf", "crop=ih*(9/16):ih",
            "-c:v", "libx264", 
            "-preset", "fast",
            "-c:a", "aac", 
            output_path
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if res.returncode != 0:
                raise ClipError(f"Fallback crop failed: {res.stderr}")
            return output_path
        except Exception as exc:
            raise ClipError(f"Fallback crop error: {exc}") from exc
