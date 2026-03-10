AI Agent Development Workflow

1. Purpose

This document defines the workflow AI agents must follow when implementing code in this repository.

AI agents must follow this workflow before generating any code.

2. Task Analysis

Before coding, the AI agent must analyze the task.

The agent must determine:

What feature is requested

Which layer the feature belongs to

Which modules are affected

Example:

Feature: video transcription.

Correct module:

interfaces/speech_to_text.py
infra/speech/whisper_engine.py
services/transcript_service.py
3. Architecture Validation

Before implementing code, the agent must verify:

no architecture rule will be violated

dependencies remain valid

interfaces are respected

If architecture conflict exists:

The agent must stop and report the issue.

4. Implementation Order

When implementing a new capability, follow this order.

Step 1

Check existing interface.

Step 2

Implement infra adapter.

Step 3

Create service logic.

Step 4

Add pipeline integration.

Step 5

Expose functionality via API or CLI.

Example workflow:

interface → infra → service → pipeline → app
5. Example Development Flow

Feature request:

Add Whisper speech-to-text support.

Workflow:

Step 1

Check interface:

interfaces/speech_to_text.py

Step 2

Implement engine:

infra/speech/whisper_engine.py

Step 3

Integrate service:

services/transcript_service.py

Step 4

Update pipeline:

pipelines/clip_pipeline.py
6. Code Generation Rules

AI agents must follow these rules.

Do not modify:

interfaces

architecture layers

folder structure

All new logic must be placed inside the correct layer.

7. File Creation Rules

AI agents may only create files in these directories:

infra/
services/
pipelines/
tests/

New files must follow existing naming conventions.

Example:

whisper_engine.py
highlight_service.py
clip_pipeline.py
8. Testing Workflow

Every new feature must include tests.

Steps:

Implement feature

Write unit tests

Validate pipeline integration

Testing ensures architectural stability.

9. Logging and Observability

All services must use the shared logger.

Location:

core/logging/logger.py

Logs must include:

module name

operation

execution time

error context

10. Error Handling

Errors must use shared exceptions.

Location:

core/errors

Custom exceptions should be defined there.

11. AI Safety Rule

If a request requires:

architecture changes

interface modification

dependency rule violation

The AI agent must stop and request maintainer approval.

12. Code Review Self-Check

Before finalizing generated code, the agent must verify:

Architecture consistency

Dependency correctness

Interface compliance

Test coverage