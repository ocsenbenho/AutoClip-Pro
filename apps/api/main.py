"""FastAPI application for AutoClip Pro."""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from apps.api.routes.clips import router as clips_router
from apps.api.routes.jobs import router as jobs_router
from core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup / shutdown lifecycle."""
    settings.ensure_dirs()
    yield


app = FastAPI(
    title="AutoClip Pro API",
    description="Automated video highlight clip generator",
    version="0.2.0",
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routes ────────────────────────────────────────────────────────
app.include_router(jobs_router, prefix="/api")
app.include_router(clips_router, prefix="/api")

# ── Static file serving for generated clips ───────────────────────
if settings.clip_dir.exists():
    app.mount("/clips", StaticFiles(directory=str(settings.clip_dir)), name="clips")
if settings.subtitle_dir.exists():
    app.mount("/subtitles", StaticFiles(directory=str(settings.subtitle_dir)), name="subtitles")


@app.get("/api/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "0.1.0"}
