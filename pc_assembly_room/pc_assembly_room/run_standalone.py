"""ตัวทดสอบห้องแบบเดี่ยว (ไม่ใช่ entry point ของโปรแกรมหลัก — ห้ามนำไปรวมกับระบบหลัก)

รัน (จากโฟลเดอร์ที่มีโฟลเดอร์ pc_assembly_room อยู่):
    python -m pc_assembly_room.run_standalone --lang th --font C:/Windows/Fonts/tahoma.ttf
คีย์ r = เริ่มใหม่, Esc = ออก (เฉพาะตัวทดสอบนี้)
"""
import argparse
import sys

from direct.showbase.ShowBase import ShowBase

from .room import PCAssemblyRoom
from .strings import make_translator


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lang", default="th", choices=["th", "en"])
    ap.add_argument("--font", default=None, help="ไฟล์ฟอนต์ที่รองรับภาษาไทย")
    args = ap.parse_args()

    app = ShowBase()
    app.disable_mouse()
    app.set_background_color(0.12, 0.14, 0.18)
    app.camera.set_pos(2.2, -24, 3)
    app.camera.look_at(2.2, 0, 3)

    room = PCAssemblyRoom(app, translator=make_translator(args.lang), font_path=args.font,
                          on_complete=lambda r: print("complete:", r))
    room.enter(app.render)

    def quit_():
        room.exit()
        sys.exit()

    app.accept("escape", quit_)
    app.accept("r", room.reset)
    app.run()


if __name__ == "__main__":
    main()
