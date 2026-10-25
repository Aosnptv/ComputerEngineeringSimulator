"""Single-active-room coordinator for the shared ShowBase application."""

from __future__ import annotations

from typing import Callable, Optional

from .input_router import InputScope
from .room_contract import Room, RoomContext, RoomResult


class SceneManager:
    def __init__(self, app, session, on_result=None, on_error=None,
                 input_scope_factory=InputScope, fallback_room="hub"):
        self.app = app
        self.session = session
        self.on_result = on_result
        self.on_error = on_error
        self.input_scope_factory = input_scope_factory
        self.fallback_room = fallback_room
        self._factories: dict[str, Callable[[], Room]] = {}
        self.active_room: Optional[Room] = None
        self.active_context: Optional[RoomContext] = None
        self.active_room_id: Optional[str] = None
        self._transitioning = False

    def register(self, room_id: str, factory: Callable[[], Room]) -> None:
        if room_id in self._factories:
            raise ValueError(f"room already registered: {room_id}")
        self._factories[room_id] = factory

    def go_to(self, room_id: str) -> bool:
        if self._transitioning:
            return False
        if room_id == self.active_room_id:
            return True
        if room_id not in self._factories:
            raise KeyError(f"unknown room: {room_id}")

        self._transitioning = True
        try:
            self.close_active()
            self._activate(room_id)
            return True
        except Exception as exc:
            self._cleanup_failed_activation()
            if self.on_error:
                self.on_error(room_id, exc)
            if room_id != self.fallback_room and self.fallback_room in self._factories:
                try:
                    self._activate(self.fallback_room)
                except Exception as fallback_exc:
                    self._cleanup_failed_activation()
                    if self.on_error:
                        self.on_error(self.fallback_room, fallback_exc)
            return False
        finally:
            self._transitioning = False

    def close_active(self) -> None:
        room, context = self.active_room, self.active_context
        self.active_room = None
        self.active_context = None
        self.active_room_id = None
        self.session.current_room = ""
        try:
            if room is not None:
                room.exit()
                room.unload()
        finally:
            if context is not None:
                context.close()

    def reset_active(self) -> None:
        if self.active_room is not None:
            self.active_room.reset()

    def _activate(self, room_id: str) -> None:
        scene_root = self.app.render.attachNewNode(f"scene:{room_id}")
        ui_root = self.app.aspect2d.attachNewNode(f"ui:{room_id}")
        try:
            context = RoomContext(
                app=self.app,
                scene_root=scene_root,
                ui_root=ui_root,
                input_scope=self.input_scope_factory(),
                language=self.session.language,
                session=self.session,
                navigate=self.go_to,
                complete=self._record_result,
                report_error=self._report_room_error,
            )
        except Exception:
            ui_root.removeNode()
            scene_root.removeNode()
            raise
        self.active_context = context
        room = self._factories[room_id]()
        self.active_room = room
        self.active_room_id = room_id
        room.load(context)
        room.enter()
        self.session.current_room = room_id

    def _record_result(self, result: RoomResult) -> None:
        self.session.record_result(result)
        if self.on_result:
            self.on_result(result)

    def _report_room_error(self, room_id: str, exc: Exception) -> None:
        if self.on_error:
            self.on_error(room_id, exc)

    def _cleanup_failed_activation(self) -> None:
        room, context = self.active_room, self.active_context
        self.active_room = None
        self.active_context = None
        self.active_room_id = None
        self.session.current_room = ""
        try:
            if room is not None:
                room.unload()
        finally:
            if context is not None:
                context.close()

