
from direct.showbase.ShowBase import ShowBase
from rooms.minigames import MinigameMenu, MinigameRoom
from rooms.adapters.hub_adapter import HubAdapter
from rooms.adapters.pc_assembly_adapter import PCAssemblyAdapter
from screens import IntroScreen, LanguageScreen, ui_font
from core.scene_manager import SceneManager
from core.session_state import SessionState


class ComputerEngineeringApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.025, 0.055, 0.12, 1)

        self.font = ui_font(self.loader)
        self.session = SessionState()
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
        self.intro = IntroScreen(self, self.show_language, self.font)
        self.accept("escape", self.handle_escape)

    def show_language(self):
        self.language_screen = LanguageScreen(self, self.start_hub, self.font)

    def start_hub(self, language=None):
        self.close_minigame_menu()
        if hasattr(self, "minigame_room"):
            self.minigame_room.destroy()
            del self.minigame_room
        if language is not None:
            self.session.set_language(language)
        self.scene_manager.go_to("hub")

    def show_minigame_menu(self, language):
        if hasattr(self, "minigame_menu"):
            return
        self.minigame_menu = MinigameMenu(
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

        # LAN and Programming remain the existing placeholder rooms in B.1.
        self.scene_manager.close_active()
        self.minigame_room = MinigameRoom(
            self, self.font, language, room_id,
            self.start_hub,
        )

    def handle_escape(self):
        if hasattr(self, "minigame_menu"):
            self.close_minigame_menu()
        elif hasattr(self, "minigame_room"):
            self.start_hub()
        elif self.scene_manager.active_room_id == "pc_assembly":
            self.scene_manager.go_to("hub")
        else:
            self.userExit()

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
    app = ComputerEngineeringApp()
    app.run()
