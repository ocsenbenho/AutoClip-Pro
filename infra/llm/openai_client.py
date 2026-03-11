"""OpenAI LLM-based highlight detector."""

import json

from openai import OpenAI

from core.errors import HighlightDetectionError
from core.logging import get_logger, log_operation
from core.models.highlight import Highlight
from core.models.transcript import Transcript
from interfaces.highlight_detector import HighlightDetector

logger = get_logger("infra.llm.openai")

SYSTEM_PROMPT = """You are an expert Social Media Video Editor specializing in viral content for TikTok, YouTube Shorts, and Instagram Reels. 
Your task is to analyze video transcripts and extract the most engaging, viral-worthy highlights.

A perfect highlight MUST have:
1. THE HOOK (First 3 seconds): Must start with a curious statement, a strong opinion, an emotional reaction, or an unanswered question.
2. THE BODY (Context): A cohesive, uninterrupted narrative. Do not cut someone off mid-sentence.
3. THE PUNCHLINE (Ending): A strong, satisfying conclusion, realization, or joke.

For each highlight, return a JSON object with:
- "start": precise start timestamp in seconds (float). Must align with the start of a sentence.
- "end": precise end timestamp in seconds (float).
- "score": viral potential score from 0.0 to 1.0 (float). Be extremely strict. Only truly viral moments get >0.8.
- "title": a clickbait-style, engaging short title (<50 chars).
- "reason": professional justification on why this specific moment will retain viewer attention.

Rules:
- Length: strictly between 15 and 90 seconds. 30-45s is the sweet spot.
- Return ONLY a JSON array, sorted by highest score first. Ensure valid JSON format."""


class OpenAIHighlightDetector(HighlightDetector):
    """Detects highlights in transcripts using OpenAI's GPT models."""

    def __init__(self, api_key: str, model: str = "gpt-4o-mini") -> None:
        """Initialize the OpenAI highlight detector.

        Args:
            api_key: OpenAI API key.
            model: Model name to use.
        """
        self._client = OpenAI(api_key=api_key)
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
        """Analyze transcript and detect highlights using GPT.

        Args:
            transcript: Full video transcript.

        Returns:
            List of highlights sorted by score.

        Raises:
            HighlightDetectionError: If LLM analysis fails.
        """
        with log_operation(logger, "Detecting highlights with OpenAI"):
            try:
                formatted = self._format_transcript(transcript)

                response = self._client.chat.completions.create(
                    model=self._model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"Analyze this transcript and find the best highlights:\n\n{formatted}",
                        },
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"},
                )

                content = response.choices[0].message.content
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
