"""Stable paths across the application shell and sibling room projects."""

from pathlib import Path
import sys


SRC_ROOT = Path(__file__).resolve().parents[1]
APP_ROOT = SRC_ROOT.parent
REPOSITORY_ROOT = APP_ROOT.parent


def enable_room_package_imports() -> Path:
    """Expose sibling room packages without depending on the launch directory."""
    value = str(REPOSITORY_ROOT)
    if value not in sys.path:
        sys.path.insert(0, value)
    return REPOSITORY_ROOT

