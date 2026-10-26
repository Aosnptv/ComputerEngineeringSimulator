"""Embed the original Programming Room in the shared ShowBase application."""

from __future__ import annotations

from core.asset_paths import enable_room_package_imports
from core.room_contract import Room, RoomResult
from rooms.adapters.pc_assembly_adapter import CameraSnapshot

enable_room_package_imports()

from programming_room.main import ProgrammingLab  # noqa: E402


class ProgrammingAdapter(Room):
    room_id = "programming"

    def __init__(self):
        super().__init__()
        self.lab = None
        self.camera_snapshot = None
        self._paused_scene = None

    def _on_load(self):
        self.camera_snapshot = CameraSnapshot.capture(self.context.app)
        self.lab = ProgrammingLab(
            host_app=self.context.app,
            context=self.context,
            on_complete=self._complete,
        )

    def _on_pause(self):
        if not self.lab:
            return
        self._paused_scene = self.lab.current_scene
        self.lab.stop_animation()
        self.lab.classroom.disable()
        self.lab.hub_controller.disable()

    def _on_resume(self):
        if not self.lab:
            return
        if self._paused_scene == "room":
            self.lab.classroom.enable()
        elif self._paused_scene == "hub":
            self.lab.hub_controller.enable()
        self._paused_scene = None

    def _on_reset(self):
        if not self.lab:
            return
        if self.lab.current_scene == "mission":
            self.lab.start_level(self.lab.mission.level_index)
        else:
            self.lab.show_room()

    def _on_exit(self):
        if self.lab:
            self.lab.destroy_embedded()
        if self.camera_snapshot:
            self.camera_snapshot.restore(self.context.app)

    def _on_unload(self):
        self.lab = None
        self.camera_snapshot = None

    def _complete(self, data):
        self.context.complete(RoomResult(
            room_id=self.room_id,
            difficulty=data["difficulty"],
            elapsed_seconds=data["elapsed_seconds"],
            mistakes=data["mistakes"],
            stars=max(1, min(3, data["stars"])),
        ))
