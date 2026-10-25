"""Integrate the real PC Assembly room into the shared ShowBase."""

from dataclasses import dataclass

from direct.gui.DirectGui import DirectButton
from panda3d.core import WindowProperties

from core.asset_paths import enable_room_package_imports
from core.room_contract import Room, RoomResult

enable_room_package_imports()

from pc_assembly_room.pc_assembly_room.room3d import PCAssemblyRoom3D
from pc_assembly_room.pc_assembly_room.scene3d import START_POS
from pc_assembly_room.pc_assembly_room.score_policy import trial_stars
from pc_assembly_room.pc_assembly_room.session_ui import MainMenu, ResultPanel
from pc_assembly_room.pc_assembly_room.strings import make_translator
from pc_assembly_room.pc_assembly_room.walk import FirstPersonController, FirstPersonPointer


@dataclass
class CameraSnapshot:
    parent: object
    position: object
    orientation: object
    fov: object
    near: float
    far: float

    @classmethod
    def capture(cls, app):
        parent = app.camera.getParent()
        return cls(
            parent=parent,
            position=app.camera.getPos(parent),
            orientation=app.camera.getHpr(parent),
            fov=app.camLens.getFov(),
            near=app.camLens.getNear(),
            far=app.camLens.getFar(),
        )

    def restore(self, app):
        app.camera.reparentTo(self.parent)
        app.camera.setPos(self.position)
        app.camera.setHpr(self.orientation)
        app.camLens.setFov(self.fov)
        app.camLens.setNearFar(self.near, self.far)


class PCAssemblyAdapter(Room):
    room_id = "pc_assembly"

    def __init__(self, font=None):
        super().__init__()
        self.font = font
        self.translator = None
        self.camera_snapshot = None
        self.room = None
        self.controller = None
        self.menu = None
        self.result_panel = None
        self.back_button = None
        self.difficulty = None

    def _on_load(self):
        self.translator = make_translator(self.context.language)
        self.camera_snapshot = CameraSnapshot.capture(self.context.app)

    def _on_enter(self):
        self.context.input_scope.bind("r", self.reset)
        self._show_menu()

    def _on_reset(self):
        if self.difficulty is None:
            self._show_menu()
        else:
            self._start(self.difficulty)

    def _on_exit(self):
        self._cleanup_ui()
        self._cleanup_activity()
        self._set_cursor(True)
        if self.camera_snapshot is not None:
            self.camera_snapshot.restore(self.context.app)

    def _on_unload(self):
        self.camera_snapshot = None
        self.translator = None

    def _show_menu(self):
        self._cleanup_ui()
        self._cleanup_activity()
        self.difficulty = None
        self._set_cursor(True)
        self.menu = MainMenu(
            self.context.app,
            self.translator,
            self.font,
            self._start,
            lambda: self.context.navigate("hub"),
            parent=self.context.ui_root,
            exit_key="menu.back_hub",
        )

    def _start(self, difficulty):
        if difficulty not in ("easy", "medium"):
            raise ValueError(f"unsupported PC Assembly difficulty: {difficulty}")
        self._cleanup_ui()
        self._cleanup_activity()
        self.difficulty = difficulty
        self.context.session.selected_difficulty = difficulty
        try:
            self.room = PCAssemblyRoom3D(
                self.context.app,
                FirstPersonPointer(self.context.app),
                translator=self.translator,
                on_complete=self._complete,
                difficulty=difficulty,
                font=self.font,
                ui_parent=self.context.ui_root,
            )
            self.room.enter(self.context.scene_root)
            self.controller = FirstPersonController(
                self.context.app,
                start=START_POS,
                heading=0,
                bounds=self.room.scene.walk_bounds,
                obstacles=self.room.scene.walk_obstacles,
            )
            self.context.app.camLens.setFov(75)
            self.context.app.camLens.setNearFar(0.05, 50)
            self.back_button = DirectButton(
                parent=self.context.ui_root,
                text="BACK TO HUB" if self.context.language == "en" else "กลับห้องหลัก",
                text_font=self.font,
                scale=0.045,
                pos=(1.20, 0, 0.90),
                frameSize=(-2.8, 2.8, -0.55, 0.65),
                frameColor=(0.06, 0.43, 0.60, 0.96),
                text_fg=(1, 1, 1, 1),
                command=lambda: self.context.navigate("hub"),
            )
        except Exception as exc:
            self._cleanup_ui()
            self._cleanup_activity()
            self.context.report_error(self.room_id, exc)
            self.context.navigate("hub")

    def _complete(self, raw_result):
        if self.result_panel is not None:
            return
        result_data = dict(raw_result)
        stars = trial_stars(
            result_data["difficulty"],
            result_data["elapsed_seconds"],
            result_data["mistakes"],
        )
        result = RoomResult(
            room_id=self.room_id,
            difficulty=result_data["difficulty"],
            elapsed_seconds=result_data["elapsed_seconds"],
            mistakes=result_data["mistakes"],
            stars=stars,
            completed=True,
        )
        self.context.complete(result)
        if self.controller is not None:
            self.controller.set_enabled(False)
        self._set_cursor(True)
        self.result_panel = ResultPanel(
            self.context.app,
            self.translator,
            self.font,
            result_data,
            lambda: self._start(self.difficulty),
            self._show_menu,
            parent=self.context.ui_root,
        )

    def _cleanup_ui(self):
        for name in ("menu", "result_panel", "back_button"):
            widget = getattr(self, name)
            if widget is not None:
                widget.destroy()
                setattr(self, name, None)

    def _cleanup_activity(self):
        if self.controller is not None:
            self.controller.destroy()
            self.controller = None
        if self.room is not None:
            self.room.exit()
            self.room = None

    def _set_cursor(self, visible):
        app = self.context.app
        if app.win is None:
            return
        properties = WindowProperties()
        properties.setCursorHidden(not visible)
        app.win.requestProperties(properties)

