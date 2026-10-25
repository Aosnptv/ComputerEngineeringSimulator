"""Transient visitor-session state; nothing is persisted to disk."""

from dataclasses import dataclass, field
from typing import Optional

from .room_contract import RoomResult


@dataclass
class SessionState:
    language: str = "en"
    current_room: str = ""
    selected_difficulty: Optional[str] = None
    last_result: Optional[RoomResult] = None
    results: dict[str, RoomResult] = field(default_factory=dict)

    def set_language(self, language: str) -> None:
        if language not in ("th", "en"):
            raise ValueError("language must be 'th' or 'en'")
        self.language = language

    def record_result(self, result: RoomResult) -> None:
        self.last_result = result
        self.results[result.room_id] = result

    def reset(self, language: Optional[str] = None) -> None:
        if language is not None:
            self.set_language(language)
        self.current_room = ""
        self.selected_difficulty = None
        self.last_result = None
        self.results.clear()

