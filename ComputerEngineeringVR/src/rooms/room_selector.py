"""Room selector for the three integrated hands-on experiences."""

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel


ROOMS = {
    "pc": {
        "en": "1  PC ASSEMBLY", "th": "1  ประกอบคอมพิวเตอร์",
        "color": (0.09, 0.78, 0.96, 1),
    },
    "lan": {
        "en": "2  LAN & NETWORKS", "th": "2  LAN และเครือข่าย",
        "color": (0.29, 0.85, 0.61, 1),
    },
    "code": {
        "en": "3  PROGRAMMING", "th": "3  การเขียนโปรแกรม",
        "color": (0.68, 0.52, 1, 1),
    },
}


class RoomSelector:
    def __init__(self, app, font, language, on_select, on_close):
        self.frame = DirectFrame(
            parent=app.aspect2d, frameSize=(-2, 2, -1, 1),
            frameColor=(0.01, 0.03, 0.07, 0.94),
        )
        DirectLabel(
            parent=self.frame,
            text="CHOOSE A ROOM" if language == "en" else "เลือกห้องฝึก",
            text_font=font, pos=(0, 0, 0.68), scale=0.075,
            text_fg=(0.94, 0.98, 1, 1), frameColor=(0, 0, 0, 0),
        )
        DirectLabel(
            parent=self.frame,
            text=("3 original hands-on labs" if language == "en"
                  else "ห้องปฏิบัติการเดิม 3 ห้อง"),
            text_font=font, pos=(0, 0, 0.56), scale=0.04,
            text_fg=(0.43, 0.76, 0.87, 1), frameColor=(0, 0, 0, 0),
        )
        for index, (room_id, room) in enumerate(ROOMS.items()):
            z = 0.30 - index * 0.24
            DirectFrame(
                parent=self.frame, pos=(0, 0, z),
                frameSize=(-0.78, 0.78, -0.09, 0.09),
                frameColor=(0.055, 0.13, 0.22, 1),
            )
            DirectButton(
                parent=self.frame,
                text=room[language], text_font=font, pos=(0, 0, z - 0.015),
                scale=0.05, frameSize=(-15, 15, -0.9, 0.9),
                frameColor=(0, 0, 0, 0), text_fg=(1, 1, 1, 1), relief=0,
                command=on_select, extraArgs=[room_id],
            )
        DirectButton(
            parent=self.frame,
            text="BACK TO HUB" if language == "en" else "กลับห้องหลัก",
            text_font=font, pos=(0, 0, -0.61), scale=0.05,
            frameSize=(-13.6, 13.6, -0.9, 0.9),
            frameColor=(0.06, 0.43, 0.6, 1), text_fg=(1, 1, 1, 1),
            relief=0, command=on_close,
        )

    def destroy(self):
        self.frame.destroy()
