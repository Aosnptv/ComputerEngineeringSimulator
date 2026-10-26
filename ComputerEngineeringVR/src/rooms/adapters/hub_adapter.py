"""Room-contract wrapper for the existing Main Hub."""

from core.room_contract import Room
from rooms.main_hub import MainHub


class HubAdapter(Room):
    room_id = "hub"

    def __init__(self, font=None):
        super().__init__()
        self.font = font
        self.hub = None

    def _on_load(self):
        self.hub = MainHub(
            self.context.app,
            self.font,
            parent=self.context.scene_root,
        )

    def _on_enter(self):
        self.hub.enter(self.context.language)

    def _on_pause(self):
        self.hub.pause()

    def _on_resume(self):
        self.hub.resume()

    def _on_exit(self):
        self.hub.exit()

    def _on_unload(self):
        if self.hub is not None:
            self.hub.destroy()
            self.hub = None

