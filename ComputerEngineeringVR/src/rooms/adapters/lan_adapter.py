"""Scene-manager adapter for the original nine-station LAN lab."""

from __future__ import annotations

import sys

from panda3d.core import WindowProperties

from core.asset_paths import REPOSITORY_ROOT
from core.room_contract import Room, RoomResult
from rooms.adapters.pc_assembly_adapter import CameraSnapshot


LAN_ROOT = REPOSITORY_ROOT / "LAN_Room_3D - D"
if str(LAN_ROOT) not in sys.path:
    sys.path.insert(0, str(LAN_ROOT))

from lan_logic import LANGameLogic  # noqa: E402
from lan_ui import LANGameUI  # noqa: E402
from player import PlayerController  # noqa: E402
from room import build_room  # noqa: E402


class LANAdapter(Room):
    room_id = "lan"

    def __init__(self, font=None):
        super().__init__()
        self.font = font
        self.logic = None
        self.ui = None
        self.player = None
        self.room_root = None
        self.camera_snapshot = None
        self.difficulty = None

    def _on_load(self):
        app = self.context.app
        self.camera_snapshot = CameraSnapshot.capture(app)
        app.thai_font = self.font
        self.logic = LANGameLogic()
        self.ui = LANGameUI(
            app,
            self.logic,
            parent=self.context.ui_root,
            on_exit=lambda: self.context.navigate("hub"),
            on_complete=self._complete,
            on_started=self._start,
        )
        self.room_root = build_room(app, parent=self.context.scene_root)
        self.player = PlayerController(
            app,
            parent=self.context.scene_root,
            input_scope=self.context.input_scope,
            ui=self.ui,
        )
        self.player.set_enabled(False)

    def _on_enter(self):
        self._set_cursor(True)
        self.ui.show_difficulty_menu()

    def _on_pause(self):
        if self.player:
            self.player.set_enabled(False)
        if self.ui:
            self.ui.set_paused(True)

    def _on_resume(self):
        if self.player and self.difficulty:
            self.player.set_enabled(True)
        if self.ui and self.difficulty:
            self.ui.set_paused(False)

    def _on_reset(self):
        if self.difficulty:
            self.ui.start_game(self.difficulty)
        else:
            self.ui.show_difficulty_menu()

    def _on_exit(self):
        if self.player:
            self.player.set_enabled(False)
        self._set_cursor(True)
        if self.camera_snapshot:
            self.camera_snapshot.restore(self.context.app)

    def _on_unload(self):
        if self.player:
            self.player.destroy()
            self.player = None
        if self.ui:
            self.ui.destroy()
            self.ui = None
        if self.room_root and not self.room_root.isEmpty():
            self.room_root.removeNode()
        self.room_root = None
        self.logic = None
        self.camera_snapshot = None

    def _start(self, difficulty):
        self.difficulty = difficulty
        self.context.session.selected_difficulty = difficulty
        if self.room_root and not self.room_root.isEmpty():
            self.room_root.removeNode()
        self.room_root = build_room(
            self.context.app,
            difficulty,
            parent=self.context.scene_root,
        )
        self.player.reset()
        self.player.set_enabled(True)
        self._set_cursor(True)

    def _complete(self, data):
        result = RoomResult(
            room_id=self.room_id,
            difficulty=data["difficulty"],
            elapsed_seconds=data["elapsed_seconds"],
            mistakes=data["mistakes"],
            stars=max(1, min(3, data["stars"])),
        )
        self.context.complete(result)
        self.player.set_enabled(False)
        self._set_cursor(True)

    def _set_cursor(self, visible):
        app = self.context.app
        if app.win is None or not hasattr(app.win, "requestProperties"):
            return
        properties = WindowProperties()
        properties.setCursorHidden(not visible)
        app.win.requestProperties(properties)
