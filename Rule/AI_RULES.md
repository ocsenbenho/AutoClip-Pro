AI Development Rules for AutoClip Pro

1. Purpose

This document defines mandatory rules for any AI coding agent working in this repository.

All generated code must comply with the architecture and folder structure of the project.

AI agents must not change the architecture unless explicitly instructed by a human maintainer.

2. Project Architecture Overview

The project follows a layered architecture.

apps
pipelines
services
infra
interfaces
core

Dependency direction must always be:

core
↑
interfaces
↑
infra
↑
services
↑
pipelines
↑
apps

Lower layers must never depend on higher layers.

Example violation:

core importing services ❌
3. Folder Responsibility

Each folder has a strict purpose.

core

Contains fundamental primitives.

Examples:

data models

utility functions

configuration

logging

Core must not depend on any other module.

interfaces

Defines contracts used across the system.

Examples:

downloader interface

speech-to-text interface

highlight detection interface

video editor interface

Interfaces must remain stable.

AI must never modify interface definitions unless explicitly instructed.

infra

Contains integrations with external systems.

Examples:

yt-dlp

Whisper

LLM APIs

FFmpeg

Infra modules must implement interfaces defined in interfaces.

services

Contains business logic.

Services orchestrate multiple infra components.

Services must not contain external API logic directly.

pipelines

Defines workflows.

Examples:

video processing pipeline

clip generation pipeline

Pipelines orchestrate services.

Pipelines must remain simple and readable.

apps

Application entry points.

Examples:

API server

background worker

CLI tools

Apps call pipelines.

Apps must not implement business logic.

4. Code Generation Constraints

AI agents must follow these constraints.

Do not create new top-level folders.

Do not modify folder structure.

Do not move files between layers.

Do not change interface signatures.

Do not introduce circular dependencies.

All new code must fit inside the existing architecture.

5. Dependency Rules

Allowed dependency direction:

apps → pipelines → services → infra → interfaces → core

Forbidden dependency examples:

services importing apps ❌
infra importing services ❌
core importing infra ❌

Violations must be rejected.

6. Interface Implementation Rules

When implementing a feature that interacts with external tools:

Check if an interface already exists.

Implement the interface in the infra layer.

Do not modify the interface unless instructed.

Example:

interfaces/speech_to_text.py

Implementation:

infra/speech/whisper_engine.py
7. Configuration Rules

All configuration must be placed inside:

configs/

Hardcoded configuration is not allowed.

Example violation:

max_clip_length = 60

Correct approach:

settings.max_clip_length
8. Pipeline Rules

Pipelines must:

orchestrate services

avoid business logic

remain simple

Example pipeline:

download video
transcribe audio
detect highlights
cut clips
generate subtitles

Each step should call a service.

9. Logging and Error Handling

All modules must use the shared logging system.

core/logging/logger.py

Exceptions must be defined in:

core/errors

Do not define custom exceptions elsewhere.

10. Testing Requirements

Every new feature must include tests.

Test locations:

tests/unit
tests/integration
tests/pipeline

Unit tests must cover services and infra modules.

11. Code Style

Language:

Python 3.11

Formatting:

black
ruff

Naming conventions:

snake_case for functions

PascalCase for classes

12. AI Behavior Rules

Before generating code, the AI agent must:

Analyze existing architecture.

Locate the correct module.

Ensure no architecture violation occurs.

If a requested change conflicts with architecture:

The AI must refuse to implement and report the conflict.

13. Example Task Instruction

Correct instruction:

Implement WhisperSpeechEngine in infra/speech/whisper_engine.py.
The class must implement SpeechToText interface.
Do not modify interface definitions.

Incorrect instruction:

Create a new speech system anywhere in the project.
14. Architecture Stability Principle

Architecture stability has priority over speed of implementation.

AI agents must prefer:

structural consistency

maintainability

modular design

over rapid code generation.

15. Final Rule

If uncertain where code belongs:

Do not generate code.

Instead ask for clarification.