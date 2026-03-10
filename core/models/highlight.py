"""Highlight data model."""

from typing import Optional

from pydantic import BaseModel


class Highlight(BaseModel):
    """A detected highlight moment in a video."""

    start: float
    end: float
    score: float
    title: str
    reason: Optional[str] = None
