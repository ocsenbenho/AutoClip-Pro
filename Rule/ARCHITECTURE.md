AutoClip Pro System Architecture

1. Architecture Philosophy

AutoClip Pro follows a layered clean architecture.

The system is designed so that:

business logic is isolated

external tools are replaceable

pipelines remain simple

AI agents cannot accidentally break architecture

Every module must respect the dependency direction.

Architecture stability is more important than implementation speed.

2. High-Level System Overview

The system processes long videos and produces short clips.

Processing pipeline:

Video Input
↓
Download / Ingest
↓
Speech to Text
↓
Transcript Analysis
↓
Highlight Detection
↓
Clip Generation
↓
Subtitle Generation
↓
Final Video Output

Each stage is implemented as a service inside the architecture.

3. Repository Structure

Project directory layout:

autoclip-pro/

apps/
pipelines/
services/
infra/
interfaces/
core/

configs/
scripts/
tests/
docs/

Each directory has a strict responsibility.

4. Layer Responsibilities
core

Core contains the fundamental building blocks.

Examples:

data models

logging

configuration

utilities

shared exceptions

Core must not depend on any other module.

interfaces

Interfaces define system contracts.

Examples:

Downloader interface

Speech-to-text interface

Highlight detection interface

Video editing interface

Interfaces ensure interchangeable implementations.

Example:

SpeechToText
HighlightDetector
VideoEditor

AI agents must never modify interfaces unless explicitly instructed.

infra

Infra contains external integrations.

Examples:

yt-dlp downloader

Whisper speech engine

OpenAI / Gemini client

FFmpeg editor

storage adapters

Infra modules must implement interfaces.

services

Services contain business logic.

Examples:

video ingest service

transcript service

highlight detection service

clip generation service

subtitle generation service

Services coordinate infra components.

Services must not contain direct infrastructure code.

pipelines

Pipelines orchestrate workflows.

Examples:

clip generation pipeline

subtitle pipeline

publishing pipeline

Pipelines call services in sequence.

Pipelines must remain simple.

apps

Apps are entrypoints.

Examples:

FastAPI server

background worker

CLI commands

Apps call pipelines.

Apps must not contain business logic.

5. Dependency Direction

All dependencies must follow this direction:

apps
↓
pipelines
↓
services
↓
infra
↓
interfaces
↓
core

Forbidden dependency examples:

core importing services
infra importing services
services importing pipelines

Circular dependencies are not allowed.

6. Pipeline Architecture

A typical video processing pipeline:

Video Download
↓
Speech Transcription
↓
Transcript Analysis
↓
Highlight Detection
↓
Video Clipping
↓
Subtitle Generation

Each step calls a service.

Example pipeline logic:

download video
generate transcript
detect highlight timestamps
cut video clips
generate subtitles
return clips

Pipelines should only orchestrate steps.

7. Replaceable Infrastructure

All external integrations must be replaceable.

Examples:

Speech-to-text engines:

Whisper
Deepgram
Google Speech

Video processing engines:

FFmpeg
GPU video pipeline

LLM providers:

OpenAI
Gemini
Anthropic

Switching providers must not affect services or pipelines.

8. Configuration Strategy

All configuration must be centralized.

Location:

configs/

Examples:

model.yaml
pipeline.yaml
app.yaml

Hardcoded values are not allowed.

9. Testing Strategy

Testing structure:

tests/

unit/
integration/
pipeline/

Unit tests verify:

services

infra modules

Integration tests verify:

pipeline execution

10. Architecture Stability Rule

Architecture changes must be deliberate.

AI agents must not:

modify folder structure

create new architecture layers

change interface contracts

Architecture decisions belong to maintainers.