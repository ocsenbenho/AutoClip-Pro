"""Google Gemini LLM-based highlight detector."""

import json

from google import genai
from google.genai import types

from core.errors import HighlightDetectionError
from core.logging import get_logger, log_operation
from core.models.highlight import Highlight
from core.models.transcript import Transcript
from interfaces.highlight_detector import HighlightDetector

logger = get_logger("infra.llm.gemini")

SYSTEM_PROMPT = """You are a video highlight detection AI. You analyze video transcripts and identify the most interesting, engaging, or viral-worthy moments.

For each highlight you find, return a JSON object with:
- "start": start timestamp in seconds (float)
- "end": end timestamp in seconds (float)
- "score": how interesting/engaging this moment is from 0.0 to 1.0 (float)
- "title": a short catchy title for this highlight (string)
- "reason": brief explanation of why this is a highlight (string)

Return a JSON array of highlights, sorted by score (highest first).
Focus on moments that are: funny, surprising, emotional, insightful, controversial, or contain key information.
Each highlight should be between 15 and 90 seconds long.
Return at most 10 highlights.

IMPORTANT: Return ONLY the JSON array, no other text."""


class GeminiHighlightDetector(HighlightDetector):
    """Detects highlights in transcripts using Google Gemini models."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash") -> None:
        """Initialize the Gemini highlight detector.

        Args:
            api_key: Gemini API key.
            model: Model name to use.
        """
        self._client = genai.Client(api_key=api_key)
        self._model = model

    def _format_transcript(self, transcript: Transcript) -> str:
        """Format transcript into a readable string for the LLM."""
        lines: list[str] = []
        for seg in transcript.segments:
            start_min = int(seg.start // 60)
            start_sec = int(seg.start % 60)
            lines.append(f"[{start_min:02d}:{start_sec:02d}] ({seg.start:.1f}s-{seg.end:.1f}s) {seg.text}")
        return "\n".join(lines)

    def detect(self, transcript: Transcript) -> list[Highlight]:
        """Analyze transcript and detect highlights using Gemini.

        Args:
            transcript: Full video transcript.

        Returns:
            List of highlights sorted by score.

        Raises:
            HighlightDetectionError: If LLM analysis fails.
        """
        with log_operation(logger, f"Detecting highlights with Gemini ({self._model})"):
            try:
                formatted = self._format_transcript(transcript)

                response = self._client.models.generate_content(
                    model=self._model,
                    contents=f"Analyze this transcript and find the best highlights:\n\n{formatted}",
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.3,
                        response_mime_type="application/json",
                    ),
                )

                content = response.text
                if not content:
                    return []

                data = json.loads(content)

                # Handle both {"highlights": [...]} and direct [...] formats
                if isinstance(data, dict):
                    items = data.get("highlights", data.get("results", []))
                elif isinstance(data, list):
                    items = data
                else:
                    items = []

                highlights = [
                    Highlight(
                        start=float(item["start"]),
                        end=float(item["end"]),
                        score=float(item.get("score", 0.5)),
                        title=item.get("title", "Untitled Highlight"),
                        reason=item.get("reason"),
                    )
                    for item in items
                ]

                # Sort by score descending
                highlights.sort(key=lambda h: h.score, reverse=True)
                return highlights

            except json.JSONDecodeError as exc:
                raise HighlightDetectionError(f"Failed to parse LLM response: {exc}") from exc
            except Exception as exc:
                raise HighlightDetectionError(f"Highlight detection failed: {exc}") from exc
