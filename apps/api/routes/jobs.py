"""Job management API routes."""

import os
import shutil
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from pydantic import BaseModel

from core.config import settings
from core.logging import get_logger
from core.models.job import Job, JobStatus
from core.models.video import VideoMetadata
from pipelines.clip_pipeline import run_clip_pipeline, AVAILABLE_DETECTORS, DETECTOR_LOCAL
from infra.video.ffmpeg_editor import FfmpegEditor

logger = get_logger("apps.api.jobs")
router = APIRouter(tags=["jobs"])

# ── In-memory job store ───────────────────────────────────────────
_jobs: dict[str, Job] = {}
_job_detectors: dict[str, str] = {}  # job_id → detector type
_job_vertical_formats: dict[str, bool] = {}  # job_id → vertical format choice
# max_workers=4: cho ph\u00e9p x\u1eed l\u00fd \u0111\u1ed3ng th\u1eddi nhi\u1ec1u job h\u01a1n.
# Whisper singleton warm s\u1eb5n tr\u00ean MPS \u2192 CPU contention th\u1ea5p \u2192 an to\u00e0n t\u0103ng workers.
_executor = ThreadPoolExecutor(max_workers=4)


# ── Request / Response schemas ────────────────────────────────────
class CreateJobRequest(BaseModel):
    video_url: str
    detector: str = DETECTOR_LOCAL
    vertical_format: bool = False
    task_type: str = "clip"
    video_language: str = "auto"


class JobResponse(BaseModel):
    id: str
    video_url: str
    status: JobStatus
    created_at: datetime
    updated_at: datetime
    video_title: Optional[str] = None
    video_duration: Optional[float] = None
    clips_count: int = 0
    error: Optional[str] = None
    progress_message: Optional[str] = None
    detector: Optional[str] = None
    vertical_format: bool = False
    transcript_url: Optional[str] = None
    task_type: str = "clip"
    video_language: str = "auto"

class JobDetailResponse(JobResponse):
    clips: List[dict] = []


# ── Helpers ───────────────────────────────────────────────────────
def _job_to_response(job: Job) -> JobResponse:
    return JobResponse(
        id=job.id,
        video_url=job.video_url,
        status=job.status,
        created_at=job.created_at,
        updated_at=job.updated_at,
        video_title=job.video.title if job.video else None,
        video_duration=job.video.duration if job.video else None,
        clips_count=len(job.clips),
        error=job.error,
        progress_message=job.progress_message,
        detector=_job_detectors.get(job.id),
        vertical_format=_job_vertical_formats.get(job.id, False),
        transcript_url=job.transcript_url,
        task_type=job.task_type,
        video_language=job.video_language,
    )


def _job_to_detail(job: Job) -> JobDetailResponse:
    clips_data = [
        {
            "id": c.id,
            "title": c.title,
            "start": c.start,
            "end": c.end,
            "duration": c.duration,
            "score": c.score,
            "reason": c.reason,
            "video_url": f"/clips/{c.id}.mp4",
            "subtitle_url": f"/subtitles/{c.id}.srt" if c.subtitle_path else None,
        }
        for c in job.clips
    ]
    base = _job_to_response(job)
    return JobDetailResponse(**base.model_dump(), clips=clips_data)


def _on_status_update(job: Job) -> None:
    """Callback to persist status updates during pipeline execution."""
    job.updated_at = datetime.now()
    _jobs[job.id] = job


def _run_pipeline(job_id: str, detector_type: str, vertical_format: bool) -> None:
    """Run the clip pipeline in a background thread."""
    job = _jobs.get(job_id)
    if not job:
        return
    try:
        run_clip_pipeline(
            job,
            on_status_update=_on_status_update,
            detector_type=detector_type,
            vertical_format=vertical_format,
        )
    except Exception as exc:
        logger.error("Pipeline failed for job %s: %s", job_id, exc)
        job.status = JobStatus.FAILED
        job.error = str(exc)
        job.updated_at = datetime.now()
        _jobs[job_id] = job


# ── Endpoints ─────────────────────────────────────────────────────
@router.post("/jobs", response_model=JobResponse, status_code=201)
def create_job(req: CreateJobRequest):
    """Submit a new video processing job."""
    # Validate detector type
    if req.detector not in AVAILABLE_DETECTORS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid detector '{req.detector}'. Available: {list(AVAILABLE_DETECTORS.keys())}",
        )

    job_id = uuid.uuid4().hex[:12]
    job = Job(id=job_id, video_url=req.video_url, task_type=req.task_type, video_language=req.video_language)
    
    _jobs[job_id] = job
    # Store choices for response
    _job_detectors[job_id] = req.detector
    _job_vertical_formats[job_id] = req.vertical_format

    logger.info(
        "Created job %s for URL: %s (detector: %s, vertical: %s)",
        job_id, req.video_url, req.detector, req.vertical_format
    )

    # Run pipeline in background
    _executor.submit(_run_pipeline, job_id, req.detector, req.vertical_format)

    return _job_to_response(job)


@router.post("/jobs/upload", response_model=JobResponse, status_code=201)
def upload_job(
    file: UploadFile = File(...),
    detector: str = Form(DETECTOR_LOCAL),
    vertical_format: bool = Form(False),
    task_type: str = Form("clip"),
    video_language: str = Form("auto")
):
    """Submit a new video processing job from a file upload."""
    if detector not in AVAILABLE_DETECTORS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid detector '{detector}'. Available: {list(AVAILABLE_DETECTORS.keys())}",
        )

    job_id = uuid.uuid4().hex[:12]
    
    # Save the file
    settings.ensure_dirs()
    safe_filename = file.filename.replace(" ", "_")
    file_path = settings.video_dir / f"{job_id}_{safe_filename}"
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Get metadata using FfmpegEditor
    ffmpeg = FfmpegEditor()
    duration = 0.0
    try:
        info = ffmpeg.get_info(str(file_path))
        duration = info.get("duration", 0.0)
    except Exception as e:
        logger.warning(f"Could not get duration for uploaded file: {e}")

    job = Job(
        id=job_id, 
        video_url="local_upload",
        task_type=task_type,
        video_language=video_language,
        video=VideoMetadata(
            id=job_id,
            title=file.filename,
            url="local_upload",
            file_path=str(file_path),
            duration=duration
        )
    )
    
    _jobs[job_id] = job
    _job_detectors[job_id] = detector
    _job_vertical_formats[job_id] = vertical_format

    logger.info(
        "Created job %s for uploaded file: %s (detector: %s, vertical: %s)",
        job_id, file.filename, detector, vertical_format
    )

    # Run pipeline in background
    _executor.submit(_run_pipeline, job_id, detector, vertical_format)

    return _job_to_response(job)


@router.get("/jobs", response_model=list[JobResponse])
def list_jobs():
    """List all processing jobs."""
    sorted_jobs = sorted(_jobs.values(), key=lambda j: j.created_at, reverse=True)
    return [_job_to_response(j) for j in sorted_jobs]


@router.get("/jobs/{job_id}", response_model=JobDetailResponse)
def get_job(job_id: str):
    """Get detailed information about a specific job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return _job_to_detail(job)


@router.delete("/jobs/{job_id}", status_code=204)
def delete_job(job_id: str):
    """Delete a job. Only completed or failed jobs can be deleted."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in (JobStatus.COMPLETED, JobStatus.FAILED):
        raise HTTPException(status_code=409, detail="Cannot delete a running job")
    del _jobs[job_id]
    _job_detectors.pop(job_id, None)
    _job_vertical_formats.pop(job_id, None)


@router.get("/detectors")
def list_detectors():
    """List available highlight detection methods."""
    return [
        {"id": key, "name": name}
        for key, name in AVAILABLE_DETECTORS.items()
    ]
