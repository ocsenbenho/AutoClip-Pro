"""Video metadata data model."""

from typing import Optional

from pydantic import BaseModel


class VideoMetadata(BaseModel):
    """Metadata for a downloaded video."""

    id: str
    title: str
    url: str
    file_path: str
    duration: float
    thumbnail_url: Optional[str] = None
    description: Optional[str] = None
