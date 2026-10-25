
from direct.showbase.ShowBase import ShowBase
from rooms.main_hub import MainHub
from rooms.minigames import MinigameMenu, MinigameRoom
from screens import IntroScreen, LanguageScreen, ui_font


class ComputerEngineeringApp(ShowBase):
    def __init__(self):
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.025, 0.055, 0.12, 1)

        self.font = ui_font(self.loader)
        self.intro = IntroScreen(self, self.show_language, self.font)
        self.accept("escape", self.userExit)

    def show_language(self):
        self.language_screen = LanguageScreen(self, self.start_hub, self.font)

    def start_hub(self, language):
        if hasattr(self, "minigame_room"):
            self.minigame_room.destroy()
            del self.minigame_room
        self.hub = MainHub(self, self.font)
        self.hub.enter(language)

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
        if hasattr(self, "minigame_room"):
            self.minigame_room.destroy()
            del self.minigame_room
        else:
            self.hub.exit()
        self.minigame_room = MinigameRoom(
            self, self.font, language, room_id,
            lambda: self.start_hub(language),
        )


if __name__ == "__main__":
    app = ComputerEngineeringApp()
    app.run()
