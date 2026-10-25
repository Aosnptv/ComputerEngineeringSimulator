# main.py
import sys
import os
from direct.showbase.ShowBase import ShowBase
from panda3d.core import AmbientLight, DirectionalLight, Vec4, WindowProperties, TextNode

from lan_logic import LANGameLogic
from lan_ui import LANGameUI
from player import PlayerController
from room import build_room


class MainApp(ShowBase):
    def __init__(self):
        super().__init__()

        props = WindowProperties()
        props.setTitle("LAN Cable Assembly Simulator | 3D Module")
        props.setSize(1280, 720)
        self.win.requestProperties(props)
        self.set_background_color(0.08, 0.1, 0.14)

        self.thai_font = None
        font_paths = [
            "fonts/Prompt-Regular.ttf",
            "fonts/THSarabunNew.ttf",
            "fonts/Kanit-Regular.ttf",
            "C:/Windows/Fonts/angsa.ttf",
            "C:/Windows/Fonts/cordia.ttf",
            "C:/Windows/Fonts/tahoma.ttf"
        ]

        for path in font_paths:
            if os.path.exists(path):
                try:
                    loaded_font = self.loader.loadFont(path)
                    if loaded_font:
                        self.thai_font = loaded_font
                        TextNode.setDefaultFont(loaded_font)
                        break
                except Exception:
                    continue

        self.disableMouse()
        self.setup_lighting()

        # 1. สร้างฉาก 3D Virtual Lab
        self.room_node = build_room(self)

        # 2. ระบบ Logic และ UI
        self.logic = LANGameLogic()
        self.ui = LANGameUI(self, self.logic)

        # 3. ตัวละคร 3D และระบบควบคุม
        self.player = PlayerController(self)

        self.ui.show_difficulty_menu()
        self.accept("escape", sys.exit)

    def setup_lighting(self):
        alight = AmbientLight("ambient_light")
        alight.setColor(Vec4(0.45, 0.48, 0.55, 1))
        alnp = self.render.attachNewNode(alight)
        self.render.setLight(alnp)

        dlight = DirectionalLight("dir_light")
        dlight.setColor(Vec4(0.75, 0.75, 0.7, 1))
        dlnp = self.render.attachNewNode(dlight)
        dlnp.setHpr(-35, -50, 0)
        self.render.setLight(dlnp)

    def reload_room(self, difficulty="easy"):
        if hasattr(self, 'room_node') and self.room_node:
            self.room_node.removeNode()
        self.room_node = build_room(self, difficulty)

if __name__ == "__main__":
    app = MainApp()
    app.run()