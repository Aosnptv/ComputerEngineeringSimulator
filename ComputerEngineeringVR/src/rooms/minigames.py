"""Three small, connected learning rooms for the main hub."""

from typing import TypedDict

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from panda3d.core import AmbientLight, DirectionalLight


class Challenge(TypedDict):
    en: tuple[str, tuple[str, str, str]]
    th: tuple[str, tuple[str, str, str]]
    answer: int


class Room(TypedDict):
    en: str
    th: str
    color: tuple[float, float, float, float]
    questions: list[Challenge]


ROOMS: dict[str, Room] = {
    "pc": {
        "en": "1  PC ASSEMBLY",
        "th": "1  ประกอบคอมพิวเตอร์",
        "color": (0.09, 0.78, 0.96, 1),
        "questions": [
            {
                "en": ("Which part stores data while a program is running?", ("RAM", "SSD", "Power supply")),
                "th": ("ชิ้นส่วนใดเก็บข้อมูลขณะโปรแกรมทำงาน?", ("RAM", "SSD", "พาวเวอร์ซัพพลาย")),
                "answer": 0,
            },
            {
                "en": ("Which part performs most calculations?", ("Case fan", "CPU", "Monitor")),
                "th": ("ชิ้นส่วนใดทำหน้าที่คำนวณหลัก?", ("พัดลมเคส", "CPU", "จอภาพ")),
                "answer": 1,
            },
            {
                "en": ("Which part supplies electricity to the PC?", ("GPU", "RAM", "Power supply")),
                "th": ("ชิ้นส่วนใดจ่ายไฟให้คอมพิวเตอร์?", ("GPU", "RAM", "พาวเวอร์ซัพพลาย")),
                "answer": 2,
            },
        ],
    },
    "lan": {
        "en": "2  LAN & NETWORKS",
        "th": "2  LAN และเครือข่าย",
        "color": (0.29, 0.85, 0.61, 1),
        "questions": [
            {
                "en": ("Which connector is commonly used for Ethernet?", ("USB-C", "RJ45", "HDMI")),
                "th": ("หัวต่อใดใช้กับสาย Ethernet โดยทั่วไป?", ("USB-C", "RJ45", "HDMI")),
                "answer": 1,
            },
            {
                "en": ("Which device connects computers within one LAN?", ("Switch", "Keyboard", "Projector")),
                "th": ("อุปกรณ์ใดเชื่อมคอมพิวเตอร์ภายใน LAN?", ("สวิตช์", "แป้นพิมพ์", "โปรเจกเตอร์")),
                "answer": 0,
            },
            {
                "en": ("Which device links a LAN to another network?", ("Mouse", "Monitor", "Router")),
                "th": ("อุปกรณ์ใดเชื่อม LAN ไปยังเครือข่ายอื่น?", ("เมาส์", "จอภาพ", "เราเตอร์")),
                "answer": 2,
            },
        ],
    },
    "code": {
        "en": "3  PROGRAMMING",
        "th": "3  การเขียนโปรแกรม",
        "color": (0.68, 0.52, 1, 1),
        "questions": [
            {
                "en": ("What does a variable store?", ("A value", "A cable", "A screen")),
                "th": ("ตัวแปรใช้เก็บอะไร?", ("ค่า", "สายสัญญาณ", "จอภาพ")),
                "answer": 0,
            },
            {
                "en": ("What does an if statement do?", ("Repeats forever", "Checks a condition", "Deletes a file")),
                "th": ("คำสั่ง if ทำหน้าที่อะไร?", ("วนซ้ำตลอด", "ตรวจสอบเงื่อนไข", "ลบไฟล์")),
                "answer": 1,
            },
            {
                "en": ("What does print(2 + 3) display?", ("2 + 3", "23", "5")),
                "th": ("print(2 + 3) แสดงผลอะไร?", ("2 + 3", "23", "5")),
                "answer": 2,
            },
        ],
    },
}


def label(parent, text, font, pos, scale=0.05, color=(0.94, 0.98, 1, 1)):
    return DirectLabel(parent=parent, text=text, text_font=font, pos=pos,
                       scale=scale, text_fg=color, frameColor=(0, 0, 0, 0))


def button(parent, text, font, pos, command, color, width=0.68):
    return DirectButton(parent=parent, text=text, text_font=font, pos=pos,
                        scale=0.05, frameSize=(-width / 0.05, width / 0.05, -0.9, 0.9),
                        frameColor=color, text_fg=(1, 1, 1, 1),
                        relief=0, command=command)


class MinigameMenu:
    def __init__(self, app, font, language, on_select, on_close):
        self.on_select = on_select
        self.on_close = on_close
        self.language = language
        self.frame = DirectFrame(parent=app.aspect2d,
                                 frameSize=(-2, 2, -1, 1),
                                 frameColor=(0.01, 0.03, 0.07, 0.94))
        label(self.frame, "CHOOSE A ROOM" if language == "en" else "เลือกห้องมินิเกม",
              font, (0, 0, 0.68), 0.075)
        label(self.frame, "3 rooms  /  3 challenges each" if language == "en"
              else "3 ห้อง  /  ห้องละ 3 คำถาม", font, (0, 0, 0.56), 0.04,
              (0.43, 0.76, 0.87, 1))
        for i, room_id in enumerate(ROOMS):
            room = ROOMS[room_id]
            z = 0.30 - i * 0.24
            DirectFrame(parent=self.frame, pos=(0, 0, z),
                        frameSize=(-0.78, 0.78, -0.09, 0.09),
                        frameColor=(0.055, 0.13, 0.22, 1))
            DirectFrame(parent=self.frame, pos=(-0.77, 0, z),
                        frameSize=(-0.008, 0.008, -0.08, 0.08),
                        frameColor=room["color"])
            button(self.frame, room["th"] if language == "th" else room["en"],
                   font, (0, 0, z - 0.015),
                   lambda selected=room_id: self.on_select(selected),
                   (0, 0, 0, 0), 0.75)
        DirectFrame(parent=self.frame, pos=(0, 0, -0.61),
                    frameSize=(-0.68, 0.68, -0.055, 0.055),
                    frameColor=(0.06, 0.43, 0.6, 1))
        button(self.frame, "BACK TO HUB" if language == "en" else "กลับห้องหลัก",
               font, (0, 0, -0.61), on_close, (0.06, 0.43, 0.6, 1))

    def destroy(self):
        self.frame.destroy()


class MinigameRoom:
    def __init__(self, app, font, language, room_id, on_home):
        self.app = app
        self.font = font
        self.language = language
        self.room_id = room_id
        self.room = ROOMS[room_id]
        self.on_home = on_home
        self.level = 0
        self.answered = False
        self.root = app.render.attachNewNode("minigame_" + room_id)
        self.ui = []
        self.build_scene()
        self.build_ui()

    def box(self, name, pos, size, color):
        model = self.app.loader.loadModel("models/box")
        model.reparentTo(self.root)
        model.setName(name)
        model.setPos(*(pos[i] - size[i] for i in range(3)))
        model.setScale(*(2 * n for n in size))
        model.setTextureOff(1)
        model.setColor(*color)
        return model

    def build_scene(self):
        accent = self.room["color"]
        self.box("Floor", (0, 2, -0.18), (9, 10, 0.18), (0.13, 0.2, 0.31, 1))
        self.box("Back Wall", (0, 10, 3), (9, 0.2, 3), (0.075, 0.15, 0.25, 1))
        self.box("Ceiling", (0, 2, 6), (9, 10, 0.2), (0.055, 0.1, 0.18, 1))
        for x in (-9, 9):
            self.box("Side Wall", (x, 2, 3), (0.2, 10, 3), (0.09, 0.17, 0.28, 1))
            rail = self.box("Light Rail", (x * 0.97, 2, 4.7),
                            (0.025, 9, 0.045), accent)
            rail.setLightOff()
        self.box("Work Table", (0, 5.7, 0.95), (3.2, 1.1, 0.12),
                 (0.17, 0.31, 0.45, 1))
        self.box("Work Table Base", (0, 5.7, 0.46), (2.7, 0.8, 0.45),
                 (0.05, 0.11, 0.2, 1))
        self.box("Display Frame", (0, 8.9, 2.8), (2.5, 0.13, 1.45),
                 (0.02, 0.07, 0.14, 1))
        screen = self.box("Display Screen", (0, 8.73, 2.8),
                          (2.25, 0.02, 1.2), (accent[0] * 0.28,
                                                   accent[1] * 0.28,
                                                   accent[2] * 0.28, 1))
        screen.setLightOff()
        for i in range(3):
            bar = self.box("Display Line", (-0.65, 8.69, 3.3 - i * 0.35),
                           (0.8 - i * 0.1, 0.01, 0.035), accent)
            bar.setLightOff()
        if self.room_id == "pc":
            self.box("Computer Case", (-1.5, 5.7, 1.55), (0.5, 0.42, 0.47),
                     (0.03, 0.09, 0.16, 1))
            for z in (1.35, 1.6, 1.85):
                self.box("Computer Component", (-1.5, 5.22, z),
                         (0.26, 0.025, 0.06), accent)
        elif self.room_id == "lan":
            self.box("Network Switch", (0, 5.6, 1.22), (1.25, 0.38, 0.2),
                     (0.03, 0.09, 0.16, 1))
            for x in (-0.8, -0.4, 0, 0.4, 0.8):
                self.box("Network Port", (x, 5.19, 1.25),
                         (0.12, 0.015, 0.07), accent)
        else:
            self.box("Code Laptop", (0, 5.65, 1.5), (1.2, 0.08, 0.6),
                     (0.03, 0.09, 0.16, 1))
            for i in range(4):
                self.box("Code Line", (-0.3, 5.55, 1.75 - i * 0.19),
                         (0.55 - i * 0.06, 0.01, 0.025), accent)
        ambient = AmbientLight("room_ambient")
        ambient.setColor((0.5, 0.6, 0.7, 1))
        self.root.setLight(self.root.attachNewNode(ambient))
        sun = DirectionalLight("room_key")
        sun.setColor((0.55, 0.65, 0.75, 1))
        sun_node = self.root.attachNewNode(sun)
        sun_node.setHpr(-30, -50, 0)
        self.root.setLight(sun_node)
        self.app.camera.setPos(0, -5, 2.5)
        self.app.camera.setHpr(0, -3, 0)

    def build_ui(self):
        frame = DirectFrame(parent=self.app.aspect2d,
                            frameSize=(-2, 2, -1, 1),
                            frameColor=(0, 0, 0, 0))
        self.ui.append(frame)
        DirectFrame(parent=frame, pos=(0, 0, 0.82),
                    frameSize=(-1.2, 1.2, -0.11, 0.11),
                    frameColor=(0.02, 0.07, 0.14, 0.96))
        label(frame, self.room["th"] if self.language == "th" else self.room["en"],
              self.font, (0, 0, 0.79), 0.066)
        DirectFrame(parent=frame, pos=(1.34, 0, 0.82),
                    frameSize=(-0.25, 0.25, -0.055, 0.055),
                    frameColor=(0.06, 0.43, 0.6, 1))
        button(frame, "HUB" if self.language == "en" else "ห้องหลัก",
               self.font, (1.34, 0, 0.82), self.on_home,
               (0.06, 0.43, 0.6, 1), 0.25)

        self.panel = DirectFrame(parent=frame, pos=(0, 0, -0.28),
                                 frameSize=(-0.9, 0.9, -0.59, 0.58),
                                 frameColor=(0.015, 0.05, 0.1, 0.95))
        self.level_label = label(self.panel, "", self.font, (0, 0, 0.46),
                                 0.044, self.room["color"])
        self.question_label = label(self.panel, "", self.font, (0, 0, 0.30),
                                    0.051)
        self.choice_buttons = []
        self.choice_cards = []
        for i in range(3):
            card = DirectFrame(parent=self.panel,
                               pos=(0, 0, 0.09 - i * 0.18),
                               frameSize=(-0.7, 0.7, -0.065, 0.065),
                               frameColor=(0.07, 0.2, 0.32, 1))
            self.choice_cards.append(card)
            choice = button(self.panel, "", self.font,
                            (0, 0, 0.09 - i * 0.18),
                            lambda selected=i: self.choose(selected),
                            (0, 0, 0, 0), 0.7)
            self.choice_buttons.append(choice)
        self.feedback = label(self.panel, "", self.font,
                              (0, 0, -0.43), 0.044)
        self.next_card = DirectFrame(parent=self.panel,
                                     pos=(0, 0, -0.53),
                                     frameSize=(-0.45, 0.45, -0.055, 0.055),
                                     frameColor=(0.06, 0.43, 0.6, 1))
        self.next_button = button(self.panel, "", self.font,
                                  (0, 0, -0.53), self.advance,
                                  (0.06, 0.43, 0.6, 1), 0.45)
        self.replay_card = DirectFrame(parent=self.panel,
                                       pos=(0, 0, -0.25),
                                       frameSize=(-0.45, 0.45, -0.055, 0.055),
                                       frameColor=(0.09, 0.25, 0.38, 1))
        self.replay_button = button(self.panel, "", self.font,
                                    (0, 0, -0.25), self.restart,
                                    (0, 0, 0, 0), 0.45)
        self.render_level()

    def render_level(self):
        self.answered = False
        questions = self.room["questions"]
        challenge = questions[self.level]
        question, choices = (challenge["th"] if self.language == "th"
                             else challenge["en"])
        self.level_label["text"] = (f"LEVEL {self.level + 1} / {len(questions)}"
                                    if self.language == "en" else
                                    f"ระดับ {self.level + 1} / {len(questions)}")
        self.question_label["text"] = question
        self.feedback["text"] = ""
        self.next_button.hide()
        self.next_card.hide()
        self.replay_button.hide()
        self.replay_card.hide()
        for i, choice in enumerate(self.choice_buttons):
            choice["text"] = choices[i]
            self.choice_cards[i]["frameColor"] = (0.07, 0.2, 0.32, 1)
            self.choice_cards[i].show()
            choice.show()

    def choose(self, index):
        if self.answered:
            return
        answer = self.room["questions"][self.level]["answer"]
        if index == answer:
            self.answered = True
            self.choice_cards[index]["frameColor"] = (0.12, 0.46, 0.34, 1)
            self.feedback["text"] = "Correct!" if self.language == "en" else "ถูกต้อง!"
            self.feedback["text_fg"] = (0.43, 0.95, 0.67, 1)
            self.next_button["text"] = (
                "FINISH" if self.level == 2 and self.language == "en" else
                "เสร็จสิ้น" if self.level == 2 else
                "NEXT" if self.language == "en" else "ถัดไป"
            )
            self.next_button.show()
            self.next_card.show()
        else:
            self.choice_cards[index]["frameColor"] = (0.55, 0.15, 0.24, 1)
            self.feedback["text"] = "Try again" if self.language == "en" else "ลองอีกครั้ง"
            self.feedback["text_fg"] = (1, 0.6, 0.65, 1)

    def advance(self):
        if not self.answered:
            return
        if self.level < 2:
            self.level += 1
            self.render_level()
        else:
            self.level_label["text"] = (
                "COMPLETE 3 / 3" if self.language == "en" else "สำเร็จ 3 / 3")
            self.question_label["text"] = (
                "Room complete!" if self.language == "en" else "ผ่านห้องนี้แล้ว!")
            for choice, card in zip(self.choice_buttons, self.choice_cards):
                choice.hide()
                card.hide()
            self.feedback["text"] = (
                "All 3 challenges complete" if self.language == "en"
                else "ทำครบทั้ง 3 คำถาม")
            self.replay_button["text"] = (
                "PLAY AGAIN" if self.language == "en" else "เล่นอีกครั้ง")
            self.replay_button.show()
            self.replay_card.show()
            next_room = {"pc": "lan", "lan": "code"}.get(self.room_id)
            if next_room:
                self.next_button["text"] = (
                    "NEXT ROOM" if self.language == "en" else "ไปห้องถัดไป")
                self.next_button["command"] = lambda: self.app.start_minigame(
                    next_room, self.language)
            else:
                self.next_button["text"] = (
                    "BACK TO HUB" if self.language == "en" else "กลับห้องหลัก")
                self.next_button["command"] = self.on_home

    def restart(self):
        self.level = 0
        self.next_button["command"] = self.advance
        self.render_level()

    def destroy(self):
        for widget in self.ui:
            widget.destroy()
        self.root.removeNode()
