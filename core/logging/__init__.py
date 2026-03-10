"""Shared logging setup for AutoClip Pro."""

import logging
import sys
import time
from contextlib import contextmanager
from functools import wraps
from typing import Generator


def get_logger(name: str) -> logging.Logger:
    """Return a configured logger for the given module name."""
    logger = logging.getLogger(f"autoclip.{name}")
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s %(name)-30s │ %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    return logger


@contextmanager
def log_operation(logger: logging.Logger, operation: str) -> Generator[None, None, None]:
    """Context manager that logs the start, end, and duration of an operation."""
    logger.info("▶ Starting: %s", operation)
    start = time.perf_counter()
    try:
        yield
    except Exception as exc:
        elapsed = time.perf_counter() - start
        logger.error("✖ Failed: %s after %.2fs — %s", operation, elapsed, exc)
        raise
    else:
        elapsed = time.perf_counter() - start
        logger.info("✔ Completed: %s in %.2fs", operation, elapsed)
