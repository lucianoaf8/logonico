"""Utility functions for tracking generation progress so the UI can display a real-time
progress bar via /api/progress.

The functions below write a small JSON file (logs/progress.json) that contains
information about the currently-running generation job:

{
    "status": "running" | "complete",
    "total_tasks": 120,
    "completed": 40,
    "success_rate": 33.3
}

This file is deliberately very small and is overwritten atomically on every
update so that it can be read frequently by the Flask API route without causing
locking issues.  If no job is running the file will still exist but will have
``status = "complete"`` and ``completed = total_tasks``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from ..core.config import Config

# Path to <project_root>/logs/progress.json
PROGRESS_FILE: Path = Config.LOGS_DIR / "progress.json"


def _atomic_write(path: Path, data: dict) -> None:
    """Write *data* to *path* atomically to avoid partial writes.
    A simple strategy is used: write to a temporary file in the same directory
    and then replace it.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(path)


def write_progress(
    total_tasks: int, 
    completed: int, 
    status: Literal["running", "complete"],
    current_prompt: str = None,
    prompt_progress: dict = None,
    current_model: str = None,
    model_progress: dict = None,
    endpoint: str = None,
    latest_image: str = None
) -> None:
    """Create/overwrite the progress JSON file with detailed tracking.

    Args:
        total_tasks: The total number of images/tasks that will be processed.
        completed:   How many tasks have completed so far (successful _or_ failed).
        status:      "running" while the pipeline is executing, "complete" when finished.
        current_prompt: The prompt ID currently being processed.
        prompt_progress: Dict with "current" and "total" for prompt counter.
        current_model: The model currently being used.
        model_progress: Dict with "current" and "total" for model counter.
        endpoint: The API endpoint/provider being used.
        latest_image: Filename of the most recently generated image.
    """
    if total_tasks <= 0:
        # Avoid division by zero; treat as 100 % complete.
        total_tasks = 1
        completed = 1
        status = "complete"

    success_rate = round((completed / total_tasks) * 100, 1)
    data = {
        "status": status,
        "total_tasks": total_tasks,
        "completed": completed,
        "success_rate": success_rate,
    }
    
    # Add detailed progress info if provided
    if current_prompt:
        data["current_prompt"] = current_prompt
    if prompt_progress:
        data["prompt_progress"] = prompt_progress
    if current_model:
        data["current_model"] = current_model
    if model_progress:
        data["model_progress"] = model_progress
    if endpoint:
        data["endpoint"] = endpoint
    if latest_image:
        data["latest_image"] = latest_image
    
    # Ensure parent dir exists (it should, but be safe).
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    _atomic_write(PROGRESS_FILE, data)


def read_progress() -> dict:
    """Return the latest progress information or sensible defaults if none."""
    if PROGRESS_FILE.exists():
        try:
            return json.loads(PROGRESS_FILE.read_text())
        except Exception:
            pass  # fall through to default
    # Default: everything complete so the UI shows 100 %.
    return {
        "status": "complete",
        "total_tasks": 1,
        "completed": 1,
        "success_rate": 100.0,
    }


def reset_progress() -> None:
    """Remove the progress file so the next job starts clean."""
    if PROGRESS_FILE.exists():
        PROGRESS_FILE.unlink()
