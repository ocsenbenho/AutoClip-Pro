"""Transcript data models."""

from typing import List, Optional

from pydantic import BaseModel


class TranscriptSegment(BaseModel):
    """A single segment of transcribed speech with timestamps."""

    start: float
    end: float
    text: str


class Transcript(BaseModel):
    """Complete transcript composed of timestamped segments."""

    segments: List[TranscriptSegment]
    language: Optional[str] = None
    duration: Optional[float] = None
