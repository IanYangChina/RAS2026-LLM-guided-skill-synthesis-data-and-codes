from __future__ import annotations

from pathlib import Path


def active_experiments_dir() -> Path:
    """Return the public default directory for newly generated results."""
    return Path(__file__).resolve().parents[1] / "runs"
