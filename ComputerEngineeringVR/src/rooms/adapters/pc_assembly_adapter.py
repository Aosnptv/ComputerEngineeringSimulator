"""Integrate the real PC Assembly room into the shared ShowBase."""

from dataclasses import dataclass

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
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
        self.navigation_hint = None
        self.navigation_panel = None
        self.difficulty = None

    def _on_load(self):
        self.translator = make_translator(self.context.language)
        self.camera_snapshot = CameraSnapshot.capture(self.context.app)

    def _on_enter(self):
        self.context.input_scope.bind("r", self.reset)
        self.context.input_scope.bind("tab", self._toggle_navigation)
        self._show_menu()

    def _on_reset(self):
        if self.difficulty is None:
            self._show_menu()
        else:
            self._start(self.difficulty)

    def _on_pause(self):
        if self.controller is not None:
            self.controller.set_enabled(False)

    def _on_resume(self):
        if self.controller is not None and self.result_panel is None:
            self.controller.set_enabled(True)

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
            self._diagnose(
                "pc.activity.started",
                track={
                    "pc.room": self.room,
                    "pc.scene": self.room.scene,
                    "pc.controller": self.controller,
                },
            )
            self.context.app.camLens.setFov(75)
            self.context.app.camLens.setNearFar(0.05, 50)
            self.navigation_hint = DirectLabel(
                parent=self.context.ui_root,
                text="NAVIGATION [TAB]" if self.context.language == "en" else "เมนูนำทาง [TAB]",
                text_font=self.font,
                scale=0.034,
                pos=(-1.16, 0, 0.94),
                frameSize=(-3.6, 3.6, -0.62, 0.72),
                frameColor=(0.025, 0.07, 0.11, 0.96),
                text_fg=(0.40, 0.90, 1.0, 1),
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
        self._destroy_navigation_ui()
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
        for name in ("menu", "result_panel", "navigation_hint", "navigation_panel"):
            widget = getattr(self, name)
            if widget is not None:
                widget.destroy()
                setattr(self, name, None)

    def _toggle_navigation(self):
        if self.controller is None or self.room is None or self.result_panel is not None:
            return
        if self.navigation_panel is None:
            self._show_navigation_menu()
        else:
            self._hide_navigation_menu()

    def _show_navigation_menu(self):
        if self.navigation_panel is not None:
            return
        self.controller.set_enabled(False)
        self._set_cursor(True)
        title = "NAVIGATION" if self.context.language == "en" else "เมนูนำทาง"
        subtitle = (
            "First-person controls are paused"
            if self.context.language == "en"
            else "หยุดการควบคุมมุมมองชั่วคราว"
        )
        resume = "RESUME" if self.context.language == "en" else "เล่นต่อ"
        back = "BACK TO MAIN HUB" if self.context.language == "en" else "กลับห้องหลัก"
        self.navigation_panel = DirectFrame(
            parent=self.context.ui_root,
            frameColor=(0.008, 0.02, 0.04, 0.82),
            frameSize=(-1.78, 1.78, -1, 1),
        )
        card = DirectFrame(
            parent=self.navigation_panel,
            frameColor=(0.025, 0.07, 0.11, 0.98),
            frameSize=(-0.68, 0.68, -0.48, 0.48),
        )
        DirectLabel(
            parent=card,
            text=title,
            text_font=self.font,
            text_scale=0.075,
            pos=(0, 0, 0.28),
            frameColor=(0, 0, 0, 0),
            text_fg=(0.94, 0.97, 1, 1),
        )
        DirectLabel(
            parent=card,
            text=subtitle,
            text_font=self.font,
            text_scale=0.038,
            pos=(0, 0, 0.14),
            frameColor=(0, 0, 0, 0),
            text_fg=(0.40, 0.90, 1.0, 1),
        )
        button_style = dict(
            parent=card,
            text_font=self.font,
            scale=0.06,
            frameSize=(-5.2, 5.2, -0.62, 0.72),
            frameColor=(0.06, 0.43, 0.60, 0.98),
            text_fg=(1, 1, 1, 1),
            relief=1,
        )
        DirectButton(text=resume, pos=(0, 0, -0.03), command=self._hide_navigation_menu, **button_style)
        DirectButton(text=back, pos=(0, 0, -0.25), command=self._navigate_hub, **button_style)

    def _hide_navigation_menu(self):
        if self.navigation_panel is not None:
            self.navigation_panel.destroy()
            self.navigation_panel = None
        if self.controller is not None and self.result_panel is None:
            self.controller.set_enabled(True)
            self._set_cursor(False)

    def _destroy_navigation_ui(self):
        if self.navigation_panel is not None:
            self.navigation_panel.destroy()
            self.navigation_panel = None
        if self.navigation_hint is not None:
            self.navigation_hint.destroy()
            self.navigation_hint = None

    def _navigate_hub(self):
        self.context.navigate("hub")

    def _cleanup_activity(self):
        self._diagnose(
            "pc.activity.cleanup.before",
            track={
                "pc.room": self.room,
                "pc.scene": getattr(self.room, "scene", None),
                "pc.controller": self.controller,
            },
        )
        if self.controller is not None:
            self.controller.destroy()
            self.controller = None
        if self.room is not None:
            self.room.exit()
            self.room = None
        self._diagnose("pc.activity.cleaned")

    def _diagnose(self, phase, **kwargs):
        diagnostics = getattr(self.context.app, "resource_diagnostics", None)
        if diagnostics is not None:
            diagnostics.snapshot(
                phase,
                scene_name=self.room_id,
                context=self.context,
                room=self,
                **kwargs,
            )

    def _set_cursor(self, visible):
        app = self.context.app
        if app.win is None or not hasattr(app.win, "requestProperties"):
            return
        properties = WindowProperties()
        properties.setCursorHidden(not visible)
        app.win.requestProperties(properties)

