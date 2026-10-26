"""Application-level startup, settings, language, and pause menus."""

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from panda3d.core import WindowProperties


TEXT = {
    "en": {
        "title": "COMPUTER ENGINEERING SIMULATOR",
        "start": "START GAME", "continue": "CONTINUE", "settings": "SETTINGS",
        "language": "LANGUAGE", "quit": "QUIT", "resume": "RESUME",
        "restart": "RESTART ROOM", "hub": "MAIN HUB", "main": "MAIN MENU",
        "paused": "PAUSED", "confirm": "QUIT THE GAME?", "yes": "YES, QUIT",
        "no": "CANCEL", "back": "BACK",
        "controls": "WASD MOVE  |  MOUSE LOOK  |  LEFT CLICK / E INTERACT  |  ESC PAUSE",
    },
    "th": {
        "title": "เกมจำลองวิศวกรรมคอมพิวเตอร์",
        "start": "เริ่มเกม", "continue": "เล่นต่อ", "settings": "ตั้งค่า",
        "language": "ภาษา", "quit": "ออกจากเกม", "resume": "เล่นต่อ",
        "restart": "เริ่มห้องใหม่", "hub": "ห้องหลัก", "main": "เมนูหลัก",
        "paused": "หยุดชั่วคราว", "confirm": "ต้องการออกจากเกมหรือไม่?",
        "yes": "ยืนยันออกเกม", "no": "ยกเลิก", "back": "กลับ",
        "controls": "WASD เดิน  |  เมาส์หันมอง  |  คลิกซ้าย / E โต้ตอบ  |  Esc หยุดเกม",
    },
}


class MenuController:
    def __init__(self, app, font=None):
        self.app = app
        self.font = font
        self.frame = None
        self.mode = None
        self.return_mode = "main"

    def _text(self, key):
        return TEXT[self.app.session.language][key]

    def _begin(self, title):
        self.hide()
        self._set_cursor(True)
        self.frame = DirectFrame(
            parent=self.app.aspect2d,
            frameSize=(-1.8, 1.8, -1, 1),
            frameColor=(0.008, 0.025, 0.055, 0.96),
            sortOrder=100,
        )
        card = DirectFrame(
            parent=self.frame,
            frameSize=(-0.76, 0.76, -0.78, 0.78),
            frameColor=(0.025, 0.09, 0.16, 0.99),
        )
        DirectLabel(
            parent=card, text=title, text_font=self.font, scale=0.07,
            pos=(0, 0, 0.62), frameColor=(0, 0, 0, 0),
            text_fg=(0.72, 0.96, 1, 1),
        )
        return card

    def _button(self, parent, text, z, command, color=(0.06, 0.43, 0.60, 1)):
        return DirectButton(
            parent=parent, text=text, text_font=self.font, scale=0.055,
            pos=(0, 0, z), frameSize=(-5.7, 5.7, -0.58, 0.72),
            frameColor=color, text_fg=(1, 1, 1, 1), command=command,
        )

    def show_main(self):
        self.mode = "main"
        card = self._begin(self._text("title"))
        z = 0.38
        if self.app.scene_manager.active_room is not None:
            self._button(card, self._text("continue"), z, self.resume)
            z -= 0.16
        self._button(card, self._text("start"), z, self.app.start_new_game)
        self._button(card, self._text("settings"), z - 0.16,
                     lambda: self.show_settings("main"))
        self._button(card, self._text("language"), z - 0.32, self.show_language)
        self._button(card, self._text("quit"), z - 0.48, self.show_quit_confirm,
                     (0.56, 0.16, 0.2, 1))

    def show_pause(self):
        if self.app.scene_manager.active_room is None:
            self.show_main()
            return
        self.app.scene_manager.active_room.pause()
        self.mode = "pause"
        card = self._begin(self._text("paused"))
        self._button(card, self._text("resume"), 0.38, self.resume)
        self._button(card, self._text("restart"), 0.22, self.restart)
        self._button(card, self._text("hub"), 0.06, self.go_hub)
        self._button(card, self._text("main"), -0.10, self.show_main)
        self._button(card, self._text("settings"), -0.26,
                     lambda: self.show_settings("pause"))
        self._button(card, self._text("quit"), -0.42, self.show_quit_confirm,
                     (0.56, 0.16, 0.2, 1))

    def show_language(self):
        self.mode = "language"
        card = self._begin("Choose language / เลือกภาษา")
        self._button(card, "ภาษาไทย", 0.22, lambda: self.set_language("th"))
        self._button(card, "English", 0.02, lambda: self.set_language("en"))
        self._button(card, self._text("back"), -0.30, self.show_main)

    def set_language(self, language):
        self.app.session.set_language(language)
        self.show_main()

    def show_settings(self, return_mode):
        self.return_mode = return_mode
        self.mode = "settings"
        card = self._begin(self._text("settings"))
        DirectLabel(
            parent=card, text=self._text("controls"), text_font=self.font,
            text_wordwrap=28, scale=0.04, pos=(0, 0, 0.22),
            frameColor=(0, 0, 0, 0), text_fg=(0.9, 0.96, 1, 1),
        )
        readiness = self.app.vr_adapter.readiness
        DirectLabel(
            parent=card,
            text=f"VR: {readiness.classification}\n{readiness.detail}",
            text_font=self.font, text_wordwrap=30, scale=0.035,
            pos=(0, 0, -0.05), frameColor=(0, 0, 0, 0),
            text_fg=(0.5, 0.83, 0.92, 1),
        )
        back = self.show_pause if return_mode == "pause" else self.show_main
        self._button(card, self._text("back"), -0.48, back)

    def show_quit_confirm(self):
        previous = self.mode
        self.mode = "confirm"
        card = self._begin(self._text("confirm"))
        self._button(card, self._text("yes"), 0.08, self.app.userExit,
                     (0.56, 0.16, 0.2, 1))
        back = self.show_pause if previous == "pause" else self.show_main
        self._button(card, self._text("no"), -0.16, back)

    def resume(self):
        self.hide()
        room = self.app.scene_manager.active_room
        if room is not None:
            room.resume()

    def restart(self):
        self.hide()
        room = self.app.scene_manager.active_room
        if room is not None:
            room.resume()
            self.app.scene_manager.reset_active()

    def go_hub(self):
        self.hide()
        self.app.scene_manager.go_to("hub")

    def handle_escape(self):
        if self.mode == "pause":
            self.resume()
        elif self.mode in ("settings", "language", "confirm"):
            self.show_main()
        elif self.mode == "main":
            self.show_quit_confirm()
        else:
            self.show_pause()

    def hide(self):
        if self.frame is not None:
            self.frame.destroy()
            self.frame = None
        self.mode = None

    def _set_cursor(self, visible):
        if self.app.win is None or not hasattr(self.app.win, "requestProperties"):
            return
        props = WindowProperties()
        props.setCursorHidden(not visible)
        self.app.win.requestProperties(props)
