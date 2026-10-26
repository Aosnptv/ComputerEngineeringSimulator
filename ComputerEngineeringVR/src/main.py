
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties
from rooms.room_selector import RoomSelector
from rooms.adapters.hub_adapter import HubAdapter
from rooms.adapters.lan_adapter import LANAdapter
from rooms.adapters.pc_assembly_adapter import PCAssemblyAdapter
from rooms.adapters.programming_adapter import ProgrammingAdapter
from screens import ui_font
from core.menu_controller import MenuController
from core.scene_manager import SceneManager
from core.session_state import SessionState
from core.runtime_diagnostics import install_runtime_diagnostics
from core.vr_mode import create_optional_vr_adapter


class ComputerEngineeringApp(ShowBase):
    def __init__(self, vr_requested=False):
        super().__init__()
        properties = WindowProperties()
        properties.setTitle("Computer Engineering Simulator")
        self.win.requestProperties(properties)
        self.disableMouse()
        self.setBackgroundColor(0.025, 0.055, 0.12, 1)

        self.font = ui_font(self.loader)
        self.session = SessionState()
        self.vr_adapter = create_optional_vr_adapter(vr_requested)
        self.vr_adapter.start(self)
        if vr_requested:
            status = self.vr_adapter.readiness
            print(f"[VR] {status.classification}: {status.detail}")
        self.resource_diagnostics = install_runtime_diagnostics(self)
        self.scene_manager = SceneManager(
            self,
            self.session,
            on_result=self.on_room_result,
            on_error=self.on_room_error,
        )
        self.scene_manager.register("hub", lambda: HubAdapter(self.font))
        self.scene_manager.register(
            "pc_assembly", lambda: PCAssemblyAdapter(self.font)
        )
        self.scene_manager.register("lan", lambda: LANAdapter(self.font))
        self.scene_manager.register("programming", ProgrammingAdapter)
        self.menu_controller = MenuController(self, self.font)
        self.accept("escape", self.handle_escape)
        self.menu_controller.show_main()

    def start_hub(self, language=None):
        self.menu_controller.hide()
        self.close_minigame_menu()
        if hasattr(self, "minigame_room"):
            self.minigame_room.destroy()
            del self.minigame_room
        if language is not None:
            self.session.set_language(language)
        self.scene_manager.go_to("hub")

    def start_new_game(self):
        self.scene_manager.close_active()
        self.session.reset(language=self.session.language)
        self.start_hub()

    def show_minigame_menu(self, language):
        if hasattr(self, "minigame_menu"):
            return
        self.minigame_menu = RoomSelector(
            self, self.font, language,
            lambda room_id: self.start_minigame(room_id, language),
            self.close_minigame_menu,
        )

    def close_minigame_menu(self):
        if hasattr(self, "minigame_menu"):
            self.minigame_menu.destroy()
            del self.minigame_menu

    def start_minigame(self, room_id, language):
        self.close_minigame_menu()
        self.session.set_language(language)
        if hasattr(self, "minigame_room"):
            self.minigame_room.destroy()
            del self.minigame_room
        if room_id == "pc":
            self.scene_manager.go_to("pc_assembly")
            return

        target = {"lan": "lan", "code": "programming"}.get(room_id)
        if target is None:
            raise KeyError(f"unknown room selection: {room_id}")
        self.scene_manager.go_to(target)

    def handle_escape(self):
        if hasattr(self, "minigame_menu"):
            self.close_minigame_menu()
        else:
            self.menu_controller.handle_escape()

    def reset_session(self):
        language = self.session.language
        self.close_minigame_menu()
        if hasattr(self, "minigame_room"):
            self.minigame_room.destroy()
            del self.minigame_room
        self.scene_manager.close_active()
        self.session.reset(language=language)
        self.scene_manager.go_to("hub")

    def on_room_result(self, result):
        # SceneManager already stored the result in transient session state.
        pass

    def on_room_error(self, room_id, error):
        print(f"[SceneManager] {room_id}: {error}")


if __name__ == "__main__":
    import sys

    app = ComputerEngineeringApp(vr_requested="--vr" in sys.argv[1:])
    app.run()
