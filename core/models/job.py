"""Job data model for tracking video processing tasks."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

from core.models.clip import Clip
from core.models.video import VideoMetadata


class JobStatus(str, Enum):
    """Processing status of a job."""

    PENDING = "pending"
    DOWNLOADING = "downloading"
    TRANSCRIBING = "transcribing"
    DETECTING_HIGHLIGHTS = "detecting_highlights"
    CLIPPING = "clipping"
    GENERATING_SUBTITLES = "generating_subtitles"
    COMPLETED = "completed"
    FAILED = "failed"


class Job(BaseModel):
    """A video processing job."""

    id: str
    video_url: str
    status: JobStatus = JobStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    video: Optional[VideoMetadata] = None
    clips: List[Clip] = Field(default_factory=list)
    error: Optional[str] = None
    progress_message: Optional[str] = None
