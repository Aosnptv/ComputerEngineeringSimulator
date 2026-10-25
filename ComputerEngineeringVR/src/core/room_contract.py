"""Lifecycle and data contracts shared by integrated rooms."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable, Optional


class RoomState(str, Enum):
    UNLOADED = "unloaded"
    LOADED = "loaded"
    ACTIVE = "active"
    PAUSED = "paused"
    INACTIVE = "inactive"


@dataclass(frozen=True)
class RoomResult:
    room_id: str
    difficulty: str
    elapsed_seconds: float
    mistakes: int
    stars: int
    completed: bool = True

    def __post_init__(self) -> None:
        if self.elapsed_seconds < 0:
            raise ValueError("elapsed_seconds cannot be negative")
        if self.mistakes < 0:
            raise ValueError("mistakes cannot be negative")
        if not 1 <= self.stars <= 3:
            raise ValueError("stars must be between 1 and 3")


@dataclass
class RoomContext:
    app: Any
    scene_root: Any
    ui_root: Any
    input_scope: Any
    language: str
    session: Any
    navigate: Callable[[str], None]
    complete: Callable[[RoomResult], None]
    report_error: Callable[[str, Exception], None]

    def close(self) -> None:
        """Release resources owned by the manager after room cleanup."""
        self.input_scope.clear()
        if self.ui_root is not None and not self.ui_root.isEmpty():
            self.ui_root.removeNode()
        if self.scene_root is not None and not self.scene_root.isEmpty():
            self.scene_root.removeNode()


class Room:
    """State-checked base class with idempotent exit and unload operations."""

    room_id = "room"

    def __init__(self) -> None:
        self.state = RoomState.UNLOADED
        self.context: Optional[RoomContext] = None

    def load(self, context: RoomContext) -> None:
        if self.state is not RoomState.UNLOADED:
            raise RuntimeError(f"{self.room_id} cannot load from {self.state.value}")
        self.context = context
        try:
            self._on_load()
        except Exception:
            try:
                self._on_unload()
            finally:
                self.context = None
            raise
        self.state = RoomState.LOADED

    def enter(self) -> None:
        if self.state not in (RoomState.LOADED, RoomState.INACTIVE):
            raise RuntimeError(f"{self.room_id} cannot enter from {self.state.value}")
        self._on_enter()
        self.state = RoomState.ACTIVE

    def pause(self) -> None:
        if self.state is not RoomState.ACTIVE:
            return
        self._on_pause()
        self.state = RoomState.PAUSED

    def resume(self) -> None:
        if self.state is not RoomState.PAUSED:
            return
        self._on_resume()
        self.state = RoomState.ACTIVE

    def reset(self) -> None:
        if self.state not in (RoomState.ACTIVE, RoomState.PAUSED):
            raise RuntimeError(f"{self.room_id} cannot reset from {self.state.value}")
        self._on_reset()

    def exit(self) -> None:
        if self.state not in (RoomState.ACTIVE, RoomState.PAUSED):
            return
        self._on_exit()
        self.state = RoomState.INACTIVE

    def unload(self) -> None:
        if self.state is RoomState.UNLOADED:
            return
        self.exit()
        self._on_unload()
        self.state = RoomState.UNLOADED
        self.context = None

    def _on_load(self) -> None:
        pass

    def _on_enter(self) -> None:
        pass

    def _on_pause(self) -> None:
        pass

    def _on_resume(self) -> None:
        pass

    def _on_reset(self) -> None:
        pass

    def _on_exit(self) -> None:
        pass

    def _on_unload(self) -> None:
        pass

