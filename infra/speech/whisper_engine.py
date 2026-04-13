"""Whisper-based speech-to-text engine."""

from typing import Optional

import torch
import whisper

from core.errors import TranscriptionError
from core.logging import get_logger, log_operation
from core.models.transcript import Transcript, TranscriptSegment
from interfaces.speech_to_text import SpeechToText

logger = get_logger("infra.speech.whisper")

# Initial prompt cho tiếng Việt – giúp Whisper nhận diện đúng
# từ ngữ, dấu thanh, và bối cảnh ngay từ đầu.
_VIETNAMESE_INITIAL_PROMPT = (
    "Đây là nội dung hội thoại tiếng Việt. "
    "Vui lòng ghi lại chính xác các từ, bao gồm dấu thanh và dấu câu."
)


def _select_device() -> str:
    """Tự động chọn thiết bị tính toán tốt nhất có sẵn.

    Thứ tự ưu tiên: MPS (Apple Silicon) → CUDA (NVIDIA) → CPU.

    Returns:
        Tên device hợp lệ cho torch: 'mps', 'cuda', hoặc 'cpu'.
    """
    if torch.backends.mps.is_available():
        return "mps"
    if torch.cuda.is_available():
        return "cuda"
    return "cpu"


class WhisperEngine(SpeechToText):
    """Transcribes audio using OpenAI's Whisper model (local).

    Tự động sử dụng MPS (Apple Silicon) hoặc CUDA (NVIDIA) nếu có,
    giúp tăng tốc độ transcription 3-5× so với CPU.
    """

    def __init__(self, model_name: str = "medium", device: Optional[str] = None) -> None:
        """Initialize the Whisper engine.

        Args:
            model_name: Whisper model size (tiny, base, small, medium, large-v3).
            device: Thiết bị tính toán ('mps', 'cuda', 'cpu'). Nếu None,
                    tự động chọn thiết bị tốt nhất có sẵn.
        """
        self._model_name = model_name
        self._device = device or _select_device()
        self._model: Optional[whisper.Whisper] = None
        logger.info(
            "WhisperEngine configured: model='%s', device='%s'",
            self._model_name,
            self._device,
        )

    def _load_model(self) -> whisper.Whisper:
        """Lazily load và cache Whisper model lên đúng device."""
        if self._model is None:
            with log_operation(
                logger,
                f"Loading Whisper model '{self._model_name}' on device: {self._device}",
            ):
                self._model = whisper.load_model(self._model_name, device=self._device)
        return self._model

    def transcribe(self, audio_path: str, language: str = "auto") -> Transcript:
        """Transcribe audio file into a timestamped transcript.

        Args:
            audio_path: Path to the audio file (wav, mp3, m4a, etc.).
            language: The language to transcribe in, or "auto" to detect.
                      Dùng "vi" để nhận dạng tiếng Việt chính xác nhất.

        Returns:
            Transcript with timestamped segments.

        Raises:
            TranscriptionError: If transcription fails.
        """
        with log_operation(logger, f"Transcribing: {audio_path} (language={language})"):
            try:
                model = self._load_model()

                # ── Tham số decoding ──────────────────────────────
                # temperature=0 → deterministic greedy decoding.
                # Loại bỏ hoàn toàn ngẫu nhiên, giảm hallucination tối đa.
                temperature = 0

                kwargs: dict = {
                    "audio": audio_path,
                    "verbose": False,
                    "temperature": temperature,
                    # beam_size=5: tìm kiếm beam search để chọn câu hoàn chỉnh nhất.
                    "beam_size": 5,
                    # best_of chỉ có hiệu lực khi temperature > 0 (sampling mode).
                    # Khi temperature=0 (greedy), best_of không dùng → bỏ để tiết kiệm.
                    # "best_of": 5,  # ← đã loại bỏ vì vô nghĩa với temperature=0
                    # word_timestamps=True → timestamp chính xác đến từng từ.
                    "word_timestamps": True,
                    # Ngưỡng lọc: loại đoạn im lặng & hallucination.
                    "no_speech_threshold": 0.6,
                    "compression_ratio_threshold": 2.4,
                    "logprob_threshold": -1.0,
                    # Dùng context câu trước để cải thiện câu sau.
                    "condition_on_previous_text": True,
                }

                # ── Xử lý ngôn ngữ ────────────────────────────────
                if language and language.lower() != "auto":
                    kwargs["language"] = language
                    # Khi ngôn ngữ là tiếng Việt, thêm initial_prompt để
                    # Whisper nhận diện đúng dấu thanh và từ ngữ từ đầu.
                    if language.lower() in ("vi", "vietnamese"):
                        kwargs["initial_prompt"] = _VIETNAMESE_INITIAL_PROMPT
                        logger.info("Vietnamese mode: applied initial_prompt for diacritics accuracy")

                result = model.transcribe(**kwargs)

                segments = [
                    TranscriptSegment(
                        start=seg["start"],
                        end=seg["end"],
                        text=seg["text"].strip(),
                    )
                    for seg in result.get("segments", [])
                    if seg.get("text", "").strip()
                ]

                detected_lang = result.get("language", language)
                logger.info(
                    "Transcription done: %d segments, detected_language=%s, device=%s",
                    len(segments),
                    detected_lang,
                    self._device,
                )
                return Transcript(
                    segments=segments,
                    language=detected_lang,
                    duration=segments[-1].end if segments else 0.0,
                )
            except Exception as exc:
                raise TranscriptionError(f"Whisper transcription failed: {exc}") from exc
