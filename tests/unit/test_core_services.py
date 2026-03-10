"""Unit tests for SRT generation, subtitle service, and highlight service."""

import os
import tempfile

from core.models.clip import Clip
from core.models.highlight import Highlight
from core.models.transcript import Transcript, TranscriptSegment
from infra.subtitle.srt_generator import SrtGenerator, _format_srt_time
from services.subtitle_service import SubtitleService


# ── SRT Format Tests ────────────────────────────────────────────────


class TestSrtTimeFormat:
    def test_zero(self):
        assert _format_srt_time(0.0) == "00:00:00,000"

    def test_seconds_only(self):
        assert _format_srt_time(5.5) == "00:00:05,500"

    def test_minutes_and_seconds(self):
        assert _format_srt_time(125.25) == "00:02:05,250"

    def test_hours(self):
        assert _format_srt_time(3661.123) == "01:01:01,123"


class TestSrtGenerator:
    def test_generate_creates_file(self):
        segments = [
            TranscriptSegment(start=0.0, end=2.5, text="Hello world"),
            TranscriptSegment(start=3.0, end=5.0, text="This is a test"),
        ]
        gen = SrtGenerator()

        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as f:
            output = f.name

        try:
            result = gen.generate(segments, output)
            assert result == output
            assert os.path.isfile(output)

            with open(output, "r") as f:
                content = f.read()

            assert "1\n" in content
            assert "2\n" in content
            assert "00:00:00,000 --> 00:00:02,500" in content
            assert "Hello world" in content
            assert "This is a test" in content
        finally:
            os.unlink(output)

    def test_empty_segments(self):
        gen = SrtGenerator()
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as f:
            output = f.name
        try:
            gen.generate([], output)
            with open(output, "r") as f:
                content = f.read()
            assert content == ""
        finally:
            os.unlink(output)


# ── Subtitle Service Tests ──────────────────────────────────────────


class TestSubtitleServiceExtraction:
    def test_extract_matching_segments(self):
        transcript = Transcript(
            segments=[
                TranscriptSegment(start=0.0, end=5.0, text="A"),
                TranscriptSegment(start=5.0, end=10.0, text="B"),
                TranscriptSegment(start=10.0, end=15.0, text="C"),
                TranscriptSegment(start=15.0, end=20.0, text="D"),
            ]
        )
        result = SubtitleService._extract_segments(transcript, 4.0, 12.0)
        texts = [s.text for s in result]
        assert "A" in texts  # overlaps at end
        assert "B" in texts
        assert "C" in texts
        assert "D" not in texts

    def test_no_matching_segments(self):
        transcript = Transcript(
            segments=[
                TranscriptSegment(start=0.0, end=5.0, text="A"),
            ]
        )
        result = SubtitleService._extract_segments(transcript, 10.0, 20.0)
        assert len(result) == 0


# ── Highlight Service Tests ─────────────────────────────────────────


class TestHighlightServiceOverlaps:
    def test_remove_overlapping_highlights(self):
        from services.highlight_service import HighlightService

        highlights = [
            Highlight(start=0.0, end=30.0, score=0.9, title="A"),
            Highlight(start=20.0, end=50.0, score=0.8, title="B"),  # overlaps A
            Highlight(start=60.0, end=90.0, score=0.7, title="C"),  # no overlap
        ]
        result = HighlightService._remove_overlaps(highlights)
        titles = [h.title for h in result]
        assert "A" in titles
        assert "B" not in titles  # removed due to overlap with A
        assert "C" in titles

    def test_no_overlaps(self):
        from services.highlight_service import HighlightService

        highlights = [
            Highlight(start=0.0, end=20.0, score=0.9, title="A"),
            Highlight(start=30.0, end=50.0, score=0.8, title="B"),
        ]
        result = HighlightService._remove_overlaps(highlights)
        assert len(result) == 2

    def test_empty_highlights(self):
        from services.highlight_service import HighlightService

        result = HighlightService._remove_overlaps([])
        assert result == []
