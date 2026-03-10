"""Local highlight detector using text analysis heuristics.

Detects highlights without any external API by scoring transcript
windows based on:
- Keyword density (engaging/emotional/interesting words)
- Speech pace (words per second)
- Sentence energy (exclamations, questions)
- Segment density (how much is being said)
"""

import re
from typing import List

from core.config import settings
from core.logging import get_logger, log_operation
from core.models.highlight import Highlight
from core.models.transcript import Transcript
from interfaces.highlight_detector import HighlightDetector

logger = get_logger("infra.llm.local")

# Words/phrases that indicate interesting or engaging content
INTEREST_KEYWORDS = {
    # Emotional triggers
    "amazing", "incredible", "unbelievable", "insane", "crazy", "wow",
    "awesome", "fantastic", "terrible", "horrible", "shocking", "hilarious",
    "beautiful", "gorgeous", "stunning", "brilliant", "genius", "perfect",
    # Action & drama
    "fight", "battle", "explosion", "attack", "destroy", "killed", "died",
    "crash", "broke", "won", "lost", "victory", "defeat", "champion",
    # Surprise & revelation
    "secret", "reveal", "surprise", "twist", "unexpected", "suddenly",
    "discovered", "found", "hidden", "truth", "exposed", "finally",
    # Important & key info
    "important", "critical", "essential", "must", "never", "always",
    "first", "best", "worst", "biggest", "fastest", "record", "history",
    # Emotion
    "love", "hate", "angry", "happy", "sad", "crying", "laughing",
    "scared", "excited", "nervous", "proud", "embarrassed",
    # Emphasis
    "actually", "literally", "seriously", "honestly", "basically",
    "absolutely", "definitely", "exactly", "obviously", "clearly",
}

# Weight multipliers for different scoring factors
KEYWORD_WEIGHT = 0.35
PACE_WEIGHT = 0.20
ENERGY_WEIGHT = 0.25
DENSITY_WEIGHT = 0.20


class LocalHighlightDetector(HighlightDetector):
    """Detects highlights using local text analysis (no API needed).

    Slides a window across the transcript and scores each
    window based on text features to find the most engaging moments.
    """

    def __init__(
        self,
        window_seconds: float = 45.0,
        step_seconds: float = 15.0,
        min_score: float = 0.3,
        max_highlights: int = 0,
    ) -> None:
        self._window = window_seconds
        self._step = step_seconds
        self._min_score = min_score
        # 0 means "use settings.max_clips"
        self._max_highlights = max_highlights or settings.max_clips

    def detect(self, transcript: Transcript) -> List[Highlight]:
        """Detect highlights by sliding a window over the transcript.

        Args:
            transcript: Full video transcript.

        Returns:
            List of highlights sorted by score.
        """
        with log_operation(logger, "Detecting highlights locally"):
            if not transcript.segments:
                return []

            total_duration = transcript.segments[-1].end
            windows = self._generate_windows(transcript, total_duration)

            if not windows:
                return []

            # Normalize scores to 0-1 range
            max_raw = max(w["raw_score"] for w in windows)
            min_raw = min(w["raw_score"] for w in windows)
            score_range = max_raw - min_raw if max_raw > min_raw else 1.0

            highlights = []
            for w in windows:
                score = (w["raw_score"] - min_raw) / score_range
                if score >= self._min_score:
                    highlights.append(
                        Highlight(
                            start=w["start"],
                            end=w["end"],
                            score=round(score, 3),
                            title=self._generate_title(w["text"], w["start"]),
                            reason=f"Score: keyword={w['keyword_score']:.2f}, "
                                   f"energy={w['energy_score']:.2f}, "
                                   f"pace={w['pace_score']:.2f}",
                        )
                    )

            # Sort by score descending, take top N
            highlights.sort(key=lambda h: h.score, reverse=True)
            highlights = highlights[: self._max_highlights]

            logger.info("Found %d highlights from %d windows", len(highlights), len(windows))
            return highlights

    def _generate_windows(self, transcript: Transcript, total_duration: float) -> list:
        """Slide a window across the transcript and score each window."""
        windows = []
        t = 0.0

        while t + self._window <= total_duration:
            window_start = t
            window_end = t + self._window

            # Get segments in this window
            segs = [
                s for s in transcript.segments
                if s.end > window_start and s.start < window_end
            ]

            if segs:
                text = " ".join(s.text for s in segs)
                words = text.lower().split()
                word_count = len(words)

                keyword_score = self._score_keywords(words)
                energy_score = self._score_energy(text)
                pace_score = self._score_pace(word_count, self._window)
                density_score = self._score_density(segs, self._window)

                raw_score = (
                    KEYWORD_WEIGHT * keyword_score
                    + ENERGY_WEIGHT * energy_score
                    + PACE_WEIGHT * pace_score
                    + DENSITY_WEIGHT * density_score
                )

                windows.append({
                    "start": window_start,
                    "end": window_end,
                    "text": text,
                    "raw_score": raw_score,
                    "keyword_score": keyword_score,
                    "energy_score": energy_score,
                    "pace_score": pace_score,
                })

            t += self._step

        return windows

    @staticmethod
    def _score_keywords(words: list) -> float:
        """Score based on interesting keyword density."""
        if not words:
            return 0.0
        hits = sum(1 for w in words if w.strip(".,!?;:") in INTEREST_KEYWORDS)
        # Normalize: ≥10% keywords = score 1.0
        return min(hits / max(len(words) * 0.10, 1), 1.0)

    @staticmethod
    def _score_energy(text: str) -> float:
        """Score based on exclamation marks, questions, caps."""
        score = 0.0
        score += min(text.count("!") * 0.15, 0.4)
        score += min(text.count("?") * 0.10, 0.3)
        # ALL-CAPS words
        caps_words = len(re.findall(r"\b[A-Z]{2,}\b", text))
        score += min(caps_words * 0.1, 0.3)
        return min(score, 1.0)

    @staticmethod
    def _score_pace(word_count: int, window_secs: float) -> float:
        """Score based on speech pace (words per second).

        Faster speech often indicates excitement.
        Normal pace ~2.5 wps, fast ~4+ wps.
        """
        wps = word_count / max(window_secs, 1)
        if wps < 1.0:
            return 0.2  # very slow
        elif wps < 2.5:
            return 0.4  # normal
        elif wps < 4.0:
            return 0.7  # fast — likely engaging
        else:
            return 1.0  # very fast — high energy

    @staticmethod
    def _score_density(segs: list, window_secs: float) -> float:
        """Score based on segment density (more segments = more speech)."""
        speaking_time = sum(s.end - s.start for s in segs)
        ratio = speaking_time / max(window_secs, 1)
        return min(ratio, 1.0)

    @staticmethod
    def _generate_title(text: str, start: float) -> str:
        """Generate a short title from the window text."""
        # Take the first meaningful sentence
        sentences = re.split(r"[.!?]+", text)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 10:
                # Truncate to ~60 chars
                if len(sentence) > 60:
                    sentence = sentence[:57] + "..."
                return sentence

        # Fallback: timestamp-based title
        mins = int(start // 60)
        secs = int(start % 60)
        return f"Highlight at {mins}:{secs:02d}"
