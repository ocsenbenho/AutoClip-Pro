"""Clip file serving API routes."""

import os

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from core.config import settings

router = APIRouter(tags=["clips"])


@router.get("/clips/{clip_id}/video")
def serve_clip_video(clip_id: str):
    """Serve a clip video file."""
    file_path = settings.clip_dir / f"{clip_id}.mp4"
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Clip video not found")
    return FileResponse(
        str(file_path),
        media_type="video/mp4",
        filename=f"{clip_id}.mp4",
    )


@router.get("/clips/{clip_id}/subtitle")
def serve_clip_subtitle(clip_id: str):
    """Serve a clip subtitle file."""
    file_path = settings.subtitle_dir / f"{clip_id}.srt"
    if not file_path.is_file():
        raise HTTPException(status_code=404, detail="Subtitle file not found")
    return FileResponse(
        str(file_path),
        media_type="text/plain",
        filename=f"{clip_id}.srt",
    )
