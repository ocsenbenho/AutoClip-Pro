"""Clip data model."""

from typing import Optional

from pydantic import BaseModel


class Clip(BaseModel):
    """A generated video clip from a highlight."""

    id: str
    source_video_id: str
    title: str
    start: float
    end: float
    duration: float
    file_path: str
    subtitle_path: Optional[str] = None
    score: Optional[float] = None
    reason: Optional[str] = None
