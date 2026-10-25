# lan_ui.py
import sys
import os
import random
from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from panda3d.core import TexturePool, PNMImage, Texture, Vec4
from lan_logic import COLOR_HEX_MAP, T568B_CORRECT_ORDER, T568A_CORRECT_ORDER, EQUIPMENT_INFO


class LANGameUI:
    def __init__(self, app, logic, timer=None, player=None):
        self.app = app
        self.logic = logic
        self.timer = timer
        self.player = player

        self.selected_color = None
        self.active_station = None
        self.time_left = 120
        self.is_timer_running = False

        self.st1_ready = False
        self.st2_selected_items = set()
        self.st3_steps = {"strip": False, "untwist": False, "straighten": False}
        self.st5_steps = {"cut": False, "insert": False, "crimp": False}
        self.st6_tested = False
        self.st7_connections = {"pc_switch": False, "switch_router": False}
        self.st8_net = {"ip_set": False, "ping_ok": False}

        self.mini_game_widgets = []
        self.palette_buttons = []
        self.slot_buttons = []
        self.tracker_labels = []
        self.result_star_frames = []

        self.bg_frame = None
        self.difficulty_frame = None
        self.game_frame = None
        self.result_frame = None
        self.info_card_frame = None
        self.tracker_frame = None

        self.build_difficulty_menu()
        self.build_game_ui()
        self.build_result_ui()
        self.build_info_card_ui()
        self.build_mission_tracker_ui()

        self.show_difficulty_menu()

    def font_kwargs(self):
        if hasattr(self.app, "thai_font") and self.app.thai_font:
            return {"text_font": self.app.thai_font}
        return {}

    def generate_procedural_icon(self, icon_type):
        pnm = PNMImage(256, 256, 4)
        pnm.fill(0.08, 0.12, 0.2)

        if icon_type == "utp":
            for y in range(256):
                for x in range(256):
                    dist = ((x - 128)**2 + (y - 128)**2)**0.5
                    if 60 <= dist <= 95:
                        pnm.setXel(x, y, 0.0, 0.6, 1.0)
                    elif 35 <= dist <= 55:
                        pnm.setXel(x, y, 0.0, 0.4, 0.8)
        elif icon_type == "rj45":
            for y in range(60, 200):
                for x in range(60, 196):
                    pnm.setXel(x, y, 0.6, 0.8, 0.95)
            for i in range(8):
                x_start = 72 + (i * 14)
                for y in range(70, 110):
                    for x in range(x_start, x_start + 8):
                        pnm.setXel(x, y, 0.95, 0.75, 0.1)
        elif icon_type == "crimper":
            for y in range(40, 100):
                for x in range(80, 176):
                    pnm.setXel(x, y, 0.5, 0.55, 0.6)
            for y in range(110, 230):
                for x in range(80, 115):
                    pnm.setXel(x, y, 1.0, 0.4, 0.0)
                for x in range(141, 176):
                    pnm.setXel(x, y, 1.0, 0.4, 0.0)
        elif icon_type == "tester":
            for y in range(40, 220):
                for x in range(60, 196):
                    pnm.setXel(x, y, 0.1, 0.55, 0.25)
            for i in range(8):
                cy = 55 + (i * 19)
                for y in range(cy, cy + 10):
                    for x in range(85, 115):
                        pnm.setXel(x, y, 0.1, 1.0, 0.4)

        tex = Texture()
        tex.load(pnm)
        return tex

    def build_difficulty_menu(self):
        bg_tex = None
        if os.path.exists("textures/lab_bg.jpg"):
            bg_tex = TexturePool.loadTexture("textures/lab_bg.jpg")

        self.bg_frame = DirectFrame(
            frameSize=(-1.78, 1.78, -1.0, 1.0), pos=(0, 0, 0),
            frameTexture=bg_tex if bg_tex else None,
            frameColor=(1, 1, 1, 1) if bg_tex else (0.08, 0.1, 0.15, 1)
        )

        self.difficulty_frame = DirectFrame(
            parent=self.bg_frame, frameColor=(0.02, 0.06, 0.14, 0.92),
            frameSize=(-0.75, 0.75, -0.55, 0.55), pos=(0, 0, 0), relief=1
        )

        DirectLabel(
            parent=self.difficulty_frame,
            text="SELECT DIFFICULTY\nเลือกระดับความยากเพื่อเริ่มภารกิจ",
            text_scale=0.06, text_fg=(0.0, 0.9, 1.0, 1.0),
            frameColor=(0, 0, 0, 0), pos=(0, 0, 0.35), **self.font_kwargs()
        )

        DirectButton(
            parent=self.difficulty_frame, text="ง่าย (Easy - เวลา 120 วินาที | มีเส้นนำทาง )",
            scale=0.046, command=self.start_game, extraArgs=["easy"], pos=(0, 0, 0.12),
            frameColor=(0.1, 0.75, 0.35, 1), text_fg=(1, 1, 1, 1), **self.font_kwargs()
        )
        DirectButton(
            parent=self.difficulty_frame, text="ปานกลาง (Medium - เวลา 90 วินาที | ไร้เส้นนำทาง )",
            scale=0.046, command=self.start_game, extraArgs=["medium"], pos=(0, 0, -0.06),
            frameColor=(0.9, 0.6, 0.0, 1), text_fg=(1, 1, 1, 1), **self.font_kwargs()
        )
        DirectButton(
            parent=self.difficulty_frame, text="ยาก (Hard - เวลา 60 วินาที | ซ่อนคำใบ้ | สุ่ม )",
            scale=0.046, command=self.start_game, extraArgs=["hard"], pos=(0, 0, -0.24),
            frameColor=(0.85, 0.15, 0.15, 1), text_fg=(1, 1, 1, 1), **self.font_kwargs()
        )

        DirectButton(
            parent=self.difficulty_frame, text=" ออกจากเกม (Exit Game)", scale=0.045,
            pos=(0, 0, -0.42), frameColor=(0.4, 0.1, 0.1, 1), text_fg=(1, 1, 1, 1),
            command=sys.exit, **self.font_kwargs()
        )

    def build_mission_tracker_ui(self):
        self.tracker_frame = DirectFrame(
            frameColor=(0.02, 0.05, 0.12, 0.85),
            frameSize=(-0.40, 0.40, -0.45, 0.45), pos=(-1.35, 0, 0.45)
        )
        self.tracker_frame.hide()

        self.timer_label = DirectLabel(
            parent=self.tracker_frame, text="เวลาคงเหลือ: 00:00", text_scale=0.038,
            text_fg=(1.0, 0.8, 0.2, 1), frameColor=(0, 0, 0, 0),
            pos=(-0.36, 0, 0.38), text_align=0, **self.font_kwargs()
        )

        names = [
            "1. เริ่มภารกิจ LAN", "2. เลือกอุปกรณ์", "3. เตรียมสาย UTP",
            "4. เรียงสีสาย LAN", "5. ตัดและย้ำหัว", "6. ทดสอบสัญญาณ",
            "7. ต่อเครือข่าย", "8. ตั้งค่า IP/Ping", "9. สรุปคะแนน"
        ]

        self.tracker_labels = []
        for i, name in enumerate(names):
            lbl = DirectLabel(
                parent=self.tracker_frame, text=f"[ ล็อก ] {name}", text_scale=0.028,
                text_fg=(0.6, 0.6, 0.6, 1), frameColor=(0, 0, 0, 0),
                pos=(-0.36, 0, 0.28 - (i * 0.075)), text_align=0, **self.font_kwargs()
            )
            self.tracker_labels.append(lbl)

        self.hud_exit_btn = DirectButton(
            text=" ออกจากห้อง (Exit)", scale=0.04, pos=(1.35, 0, 0.88),
            frameColor=(0.7, 0.15, 0.15, 0.9), text_fg=(1, 1, 1, 1),
            command=self.show_difficulty_menu, **self.font_kwargs()
        )
        self.hud_exit_btn.hide()

    def update_mission_tracker(self):
        for st_num in range(1, 10):
            lbl = self.tracker_labels[st_num - 1]
            if st_num in self.logic.completed_stations:
                lbl["text_fg"] = (0.1, 0.9, 0.3, 1)
                lbl["text"] = f"[ สำเร็จ ] {st_num}. ผ่านแล้ว"
            elif st_num == self.logic.unlocked_station:
                lbl["text_fg"] = (1.0, 0.8, 0.1, 1)
                lbl["text"] = f"[ กำลังทำ ] {st_num}. กำลังทำภารกิจ"
            else:
                lbl["text_fg"] = (0.5, 0.5, 0.5, 1)
                lbl["text"] = f"[ ล็อก ] {st_num}. ล็อก"

    def build_info_card_ui(self):
        self.info_card_frame = DirectFrame(
            frameSize=(-0.55, 0.55, -0.40, 0.40), pos=(0, 0, 0.1),
            frameColor=(0.04, 0.08, 0.18, 0.95)
        )
        self.info_card_frame.hide()

        self.info_title = DirectLabel(
            parent=self.info_card_frame, text="", text_scale=0.05,
            text_fg=(0.0, 0.9, 1.0, 1), frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.28), **self.font_kwargs()
        )

        self.info_image_frame = DirectFrame(
            parent=self.info_card_frame, frameSize=(-0.22, 0.22, -0.18, 0.18),
            pos=(-0.26, 0, -0.04), frameColor=(1, 1, 1, 1)
        )

        self.info_desc = DirectLabel(
            parent=self.info_card_frame, text="", text_scale=0.032,
            text_fg=(0.9, 0.9, 0.9, 1), frameColor=(0, 0, 0, 0),
            pos=(0.02, 0, 0.08), text_align=0, **self.font_kwargs()
        )

        DirectButton(
            parent=self.info_card_frame, text="ตกลง / ปิดหน้าต่าง", scale=0.04,
            pos=(0, 0, -0.30), frameColor=(0.0, 0.5, 0.8, 1), text_fg=(1, 1, 1, 1),
            command=self.info_card_frame.hide, **self.font_kwargs()
        )

    def show_item_info_card(self, item_name):
        info = EQUIPMENT_INFO.get(item_name, None)
        if not info:
            return

        self.info_title["text"] = f"ข้อมูลอุปกรณ์: {item_name}"
        self.info_desc["text"] = info["desc"]

        icon_name = info['icon']
        png_path = f"textures/items/{icon_name}.png"
        jpg_path = f"textures/items/{icon_name}.jpg"

        if os.path.exists(png_path):
            tex = TexturePool.loadTexture(png_path)
        elif os.path.exists(jpg_path):
            tex = TexturePool.loadTexture(jpg_path)
        else:
            tex = self.generate_procedural_icon(icon_name)

        self.info_image_frame["frameTexture"] = tex
        self.info_image_frame["frameColor"] = (1, 1, 1, 1)
        self.info_card_frame.show()

    def build_game_ui(self):
        self.game_frame = DirectFrame(
            frameColor=(0.02, 0.05, 0.12, 0.95),
            frameSize=(-0.95, 0.95, -0.32, 0.32), pos=(0, 0, -0.62)
        )
        self.game_frame.hide()

        self.st_title_label = DirectLabel(
            parent=self.game_frame, text="", text_scale=0.045,
            text_fg=(0.0, 0.9, 1.0, 1), frameColor=(0, 0, 0, 0),
            pos=(-0.9, 0, 0.22), text_align=0, **self.font_kwargs()
        )
        self.st_desc_label = DirectLabel(
            parent=self.game_frame, text="", text_scale=0.035,
            text_fg=(0.9, 0.9, 0.9, 1), frameColor=(0, 0, 0, 0),
            pos=(-0.9, 0, 0.14), text_align=0, **self.font_kwargs()
        )

        x_start = -0.77
        for idx, (c_name, hex_val) in enumerate(COLOR_HEX_MAP.items()):
            btn = DirectButton(
                parent=self.game_frame, text=c_name[:3], scale=0.035,
                pos=(x_start + (idx * 0.15), 0, -0.04), frameColor=hex_val,
                command=self.select_color, extraArgs=[c_name]
            )
            self.palette_buttons.append(btn)

        for i in range(8):
            btn = DirectButton(
                parent=self.game_frame, text=f"Pin {i+1}", scale=0.035,
                pos=(x_start + (i * 0.15), 0, -0.16), frameColor=(0.25, 0.28, 0.35, 1),
                command=self.place_color, extraArgs=[i]
            )
            self.slot_buttons.append(btn)

        self.action_btn = DirectButton(
            parent=self.game_frame, text="ยืนยันการปฏิบัติภารกิจ ➔", scale=0.042,
            pos=(0.65, 0, -0.22), frameColor=(0.0, 0.65, 0.9, 1),
            text_fg=(1, 1, 1, 1), command=self.do_station_action, **self.font_kwargs()
        )

    def build_result_ui(self):
        self.result_frame = DirectFrame(
            frameColor=(0.04, 0.08, 0.18, 0.96),
            frameSize=(-0.85, 0.85, -0.5, 0.5), pos=(0, 0, 0)
        )
        self.result_frame.hide()

        # สร้างรูปดาว 2D สีเหลือง 5 ดวงตรงกลางหน้าต่าง
        self.result_star_frames = []
        start_x = -0.36
        for i in range(5):
            star_bg = DirectFrame(
                parent=self.result_frame,
                frameSize=(-0.06, 0.06, -0.06, 0.06),
                pos=(start_x + (i * 0.18), 0, 0.28),
                frameColor=(1.0, 0.85, 0.1, 1.0)
            )
            star_lbl = DirectLabel(
                parent=star_bg, text="STAR", text_scale=0.024,
                text_fg=(0.1, 0.1, 0.1, 1), frameColor=(0, 0, 0, 0), pos=(0, 0, -0.008)
            )
            self.result_star_frames.append(star_bg)

        self.result_stars_summary = DirectLabel(
            parent=self.result_frame, text="", text_scale=0.042,
            text_fg=(1.0, 0.85, 0.1, 1), frameColor=(0, 0, 0, 0), pos=(0, 0, 0.15),
            **self.font_kwargs()
        )

        self.result_text = DirectLabel(
            parent=self.result_frame, text="", text_scale=0.04,
            text_fg=(1, 1, 1, 1), frameColor=(0, 0, 0, 0), pos=(0, 0, 0.0),
            **self.font_kwargs()
        )

        DirectButton(
            parent=self.result_frame, text=" กลับสู่เมนูหลัก (ออกจากห้อง)", scale=0.055,
            pos=(0, 0, -0.28), frameColor=(0.85, 0.2, 0.2, 1), text_fg=(1, 1, 1, 1),
            command=self.show_difficulty_menu, **self.font_kwargs()
        )

    def hide_all(self):
        if self.bg_frame: self.bg_frame.hide()
        self.game_frame.hide()
        self.result_frame.hide()
        if self.tracker_frame: self.tracker_frame.hide()
        if self.info_card_frame: self.info_card_frame.hide()
        if hasattr(self, 'hud_exit_btn'): self.hud_exit_btn.hide()

    def show_difficulty_menu(self):
        self.stop_timer()
        self.hide_all()
        if self.bg_frame: self.bg_frame.show()

    def start_game(self, level):
        self.hide_all()
        if hasattr(self.app, 'reload_room'): self.app.reload_room(level)
        self.logic.set_difficulty(level)
        
        self.time_left = float(self.logic.max_time)
        self.is_timer_running = True
        
        if hasattr(self.app, 'taskMgr'):
            self.app.taskMgr.remove("timer_task")
            self.app.taskMgr.add(self.update_timer_task, "timer_task")

        self.tracker_frame.show()
        if hasattr(self, 'hud_exit_btn'): self.hud_exit_btn.show()
        self.update_mission_tracker()

    def update_timer_task(self, task):
        if not self.is_timer_running:
            return task.done

        dt = globalClock.getDt()
        self.time_left -= dt

        if self.time_left <= 0:
            self.time_left = 0
            self.is_timer_running = False
            self.on_time_out()
            return task.done

        mins = int(self.time_left) // 60
        secs = int(self.time_left) % 60
        self.timer_label["text"] = f"เวลาคงเหลือ: {mins:02d}:{secs:02d}"
        return task.cont

    def stop_timer(self):
        self.is_timer_running = False
        if hasattr(self.app, 'taskMgr'):
            self.app.taskMgr.remove("timer_task")

    def on_time_out(self):
        self.stop_timer()
        self.game_frame.hide()
        self.info_card_frame.hide()
        
        for star in self.result_star_frames:
            star.hide()
        self.result_stars_summary["text"] = "FAILED (0 ดาว)"
        self.result_stars_summary["text_fg"] = (0.9, 0.2, 0.2, 1)

        msg = "[ TIME OUT ] ภารกิจล้มเหลว!\n\nคุณหมดเวลาในการทำภารกิจ ระบบให้ออกจากห้องทันที"
        self.result_text["text"] = msg
        self.result_frame.show()

    def clear_mini_games(self):
        for w in self.mini_game_widgets:
            w.destroy()
        self.mini_game_widgets.clear()
        for btn in self.palette_buttons + self.slot_buttons:
            btn.hide()

    def open_station_ui(self, station_num):
        self.active_station = station_num
        self.clear_mini_games()
        self.update_mission_tracker()

        if not self.logic.can_access_station(station_num):
            return

        self.action_btn.show()

        if self.logic.difficulty == "hard":
            self.st_title_label["text"] = f"สถานีที่ {station_num}: [สังเกตอุปกรณ์บนโต๊ะด้วยตนเอง]"
            self.st_desc_label["text"] = f"ภารกิจแบบสุ่มเรียงสายมาตรฐาน {self.logic.target_standard}"
        else:
            names = {
                1: "เริ่มภารกิจ LAN", 2: "เลือกและหยิบจับอุปกรณ์ LAN", 3: "เตรียมสาย UTP",
                4: f"เรียงสีสาย LAN มาตรฐาน {self.logic.target_standard}", 5: "ตัดและเข้าหัว RJ45", 6: "ทดสอบสัญญาณสาย",
                7: "ต่อสายอุปกรณ์เครือข่าย", 8: "ตั้งค่า Network IP & Ping", 9: "สรุปคะแนนภารกิจ"
            }
            self.st_title_label["text"] = f"สถานีที่ {station_num}: {names.get(station_num, '')}"
            self.st_desc_label["text"] = f"กำลังทำภารกิจเซสชันที่ {station_num} / 9"

        if station_num == 1:
            self.st1_ready = False
            self.st1_btn = DirectButton(
                parent=self.game_frame, text="[ คลิกเพื่อลงชื่อเริ่มภารกิจ ]", scale=0.045,
                pos=(0, 0, 0.02), frameColor=(0.2, 0.25, 0.35, 1),
                command=self.do_st1_action, **self.font_kwargs()
            )
            self.mini_game_widgets.append(self.st1_btn)

        elif station_num == 2:
            self.st2_selected_items.clear()
            items = ["สาย UTP", "หัว RJ45", "คีมย้ำ RJ45", "Cable Tester"]
            self.item_btns = {}
            for i, item in enumerate(items):
                btn = DirectButton(
                    parent=self.game_frame, text=f"หยิบ {item}", scale=0.038,
                    pos=(-0.65 + (i * 0.42), 0, 0.02), frameColor=(0.2, 0.25, 0.35, 1),
                    command=self.interact_and_select_item, extraArgs=[item], **self.font_kwargs()
                )
                self.item_btns[item] = btn
                self.mini_game_widgets.append(btn)

        elif station_num == 3:
            self.st3_steps = {"strip": False, "untwist": False, "straighten": False}
            self.st3_btns = {}
            steps = [("strip", "1. ปอกเปลือกนอก", -0.5), ("untwist", "2. คลายเกลียวสาย 4 คู่", 0.0), ("straighten", "3. รีดสายให้ตรง", 0.5)]
            for key, label, x_pos in steps:
                btn = DirectButton(
                    parent=self.game_frame, text=label, scale=0.038, pos=(x_pos, 0, 0.02),
                    frameColor=(0.2, 0.25, 0.35, 1), command=self.process_st3_step,
                    extraArgs=[key], **self.font_kwargs()
                )
                self.st3_btns[key] = btn
                self.mini_game_widgets.append(btn)

        elif station_num == 4:
            # ล้างค่าช่อง Pin 1-8 ให้เป็นค่าว่างทั้งหมดก่อนเริ่มกดเลือกสี
            self.logic.reset_pins()
            self.selected_color = None

            colors_items = list(COLOR_HEX_MAP.items())
            x_start = -0.77
            for idx, (c_name, hex_val) in enumerate(colors_items):
                btn = self.palette_buttons[idx]
                btn["text"] = c_name[:3]
                btn["frameColor"] = hex_val
                btn["extraArgs"] = [c_name]
                btn.show()

            for btn in self.slot_buttons:
                btn.show()

            # อัปเดตการแสดงผลหน้าจอให้ Pin 1-8 เป็นช่องว่างสีเทา
            self.update_slots_display()

        elif station_num == 5:
            self.st5_steps = {"cut": False, "insert": False, "crimp": False}
            self.st5_btns = {}
            steps = [("cut", "1. ตัดปลายสายให้เสมอ", -0.5), ("insert", "2. เสียบสายเข้าหัว RJ45", 0.0), ("crimp", "3. กดย้ำหัวด้วยคีมย้ำ", 0.5)]
            for key, label, x_pos in steps:
                btn = DirectButton(
                    parent=self.game_frame, text=label, scale=0.036, pos=(x_pos, 0, 0.02),
                    frameColor=(0.2, 0.25, 0.35, 1), command=self.process_st5_step,
                    extraArgs=[key], **self.font_kwargs()
                )
                self.st5_btns[key] = btn
                self.mini_game_widgets.append(btn)

        elif station_num == 6:
            self.st6_tested = False
            self.st6_btn = DirectButton(
                parent=self.game_frame, text="เสียบ Cable Tester & กดตรวจสัญญาณ (LED 1-8)", scale=0.04,
                pos=(0, 0, 0.02), frameColor=(0.2, 0.25, 0.35, 1),
                command=self.do_st6_action, **self.font_kwargs()
            )
            self.mini_game_widgets.append(self.st6_btn)

        elif station_num == 7:
            self.st7_connections = {"pc_switch": False, "switch_router": False}
            self.st7_btns = {}
            self.st7_btns["pc_switch"] = DirectButton(parent=self.game_frame, text="เสียบสาย: PC -> Switch", scale=0.038, pos=(-0.35, 0, 0.02), frameColor=(0.2, 0.25, 0.35, 1), command=lambda: self.do_st7_step("pc_switch"), **self.font_kwargs())
            self.st7_btns["switch_router"] = DirectButton(parent=self.game_frame, text="เสียบสาย: Switch -> Router", scale=0.038, pos=(0.35, 0, 0.02), command=lambda: self.do_st7_step("switch_router"), **self.font_kwargs())
            self.mini_game_widgets.extend(list(self.st7_btns.values()))

        elif station_num == 8:
            self.st8_net = {"ip_set": False, "ping_ok": False}
            self.st8_btns = {}
            self.st8_btns["ip_set"] = DirectButton(parent=self.game_frame, text="1. ตั้งค่า IP (192.168.1.100)", scale=0.038, pos=(-0.35, 0, 0.02), command=lambda: self.do_st8_step("ip_set"), **self.font_kwargs())
            self.st8_btns["ping_ok"] = DirectButton(parent=self.game_frame, text="2. ทดสอบ Ping Gateway", scale=0.038, pos=(0.35, 0, 0.02), command=lambda: self.do_st8_step("ping_ok"), **self.font_kwargs())
            self.mini_game_widgets.extend(list(self.st8_btns.values()))

        self.game_frame.show()

    def interact_and_select_item(self, item_name):
        if item_name in self.st2_selected_items:
            self.st2_selected_items.remove(item_name)
        else:
            self.st2_selected_items.add(item_name)

        btn = self.item_btns[item_name]
        if item_name in self.st2_selected_items:
            btn["frameColor"] = (0.0, 0.7, 0.3, 1)
            btn["text"] = f"หยิบสำเร็จ: {item_name}"
        else:
            btn["frameColor"] = (0.2, 0.25, 0.35, 1)
            btn["text"] = f"หยิบ {item_name}"

        self.show_item_info_card(item_name)

    def do_st1_action(self):
        self.st1_ready = True
        self.st1_btn["frameColor"] = (0.0, 0.7, 0.3, 1)
        self.st1_btn["text"] = "ลงชื่อเริ่มภารกิจสำเร็จ"
        self.st_desc_label["text"] = "ลงชื่อเรียบร้อยแล้ว! กดปุ่ม 'ยืนยันการปฏิบัติภารกิจ' ด้านล่าง"

    def process_st3_step(self, step):
        if step == "strip":
            self.st3_steps["strip"] = True
            self.st_desc_label["text"] = "ปอกเปลือกนอกสำเร็จ! กด '2. คลายเกลียวสาย 4 คู่'"
        elif step == "untwist":
            if not self.st3_steps["strip"]:
                self.st_desc_label["text"] = "ต้องกด '1. ปอกเปลือกนอก' ก่อน!"
                return
            self.st3_steps["untwist"] = True
            self.st_desc_label["text"] = "คลายเกลียวสายสำเร็จ! กด '3. รีดสายให้ตรง'"
        elif step == "straighten":
            if not self.st3_steps["untwist"]:
                self.st_desc_label["text"] = "ต้องกด '2. คลายเกลียวสาย 4 คู่' ก่อน!"
                return
            self.st3_steps["straighten"] = True
            self.st_desc_label["text"] = "เตรียมสาย UTP สมบูรณ์! กดยืนยันการปฏิบัติภารกิจ"

        btn = self.st3_btns[step]
        btn["frameColor"] = (0.0, 0.7, 0.3, 1)

    def process_st5_step(self, step):
        if step == "cut":
            self.st5_steps["cut"] = True
            self.st_desc_label["text"] = "ตัดสายเสมอกันแล้ว! กด '2. เสียบสายเข้าหัว RJ45'"
        elif step == "insert":
            if not self.st5_steps["cut"]:
                self.st_desc_label["text"] = "ต้องกด '1. ตัดปลายสายให้เสมอกัน' ก่อน!"
                return
            self.st5_steps["insert"] = True
            self.st_desc_label["text"] = "เสียบหัว RJ45 แล้ว! กด '3. กดย้ำหัวด้วยคีมย้ำ'"
        elif step == "crimp":
            if not self.st5_steps["insert"]:
                self.st_desc_label["text"] = "ต้องกด '2. เสียบสายเข้าหัว RJ45' ก่อน!"
                return
            self.st5_steps["crimp"] = True
            self.st_desc_label["text"] = "ย้ำหัว RJ45 เรียบร้อยแล้ว! กดยืนยันการปฏิบัติภารกิจ"

        btn = self.st5_btns[step]
        btn["frameColor"] = (0.0, 0.7, 0.3, 1)

    def do_st6_action(self):
        self.st6_tested = True
        self.st6_btn["frameColor"] = (0.0, 0.7, 0.3, 1)
        self.st6_btn["text"] = "LED 1-8 ติดครบทุกเส้น! สายใช้งานได้ปกติ"
        self.st_desc_label["text"] = "ทดสอบสัญญาณผ่าน! กดยืนยันการปฏิบัติภารกิจ"

    def do_st7_step(self, connection):
        self.st7_connections[connection] = True
        btn = self.st7_btns[connection]
        btn["frameColor"] = (0.0, 0.7, 0.3, 1)
        btn["text"] = "เชื่อมต่อสายเรียบร้อย"

    def do_st8_step(self, action):
        if action == "ip_set":
            self.st8_net["ip_set"] = True
            self.st8_btns["ip_set"]["frameColor"] = (0.0, 0.7, 0.3, 1)
            self.st_desc_label["text"] = "ตั้งค่า IP 192.168.1.100 เรียบร้อย! กด '2. ทดสอบ Ping Gateway'"
        elif action == "ping_ok":
            if not self.st8_net["ip_set"]:
                self.st_desc_label["text"] = "ต้องกด '1. ตั้งค่า IP' ก่อนทำการ Ping!"
                return
            self.st8_net["ping_ok"] = True
            self.st8_btns["ping_ok"]["frameColor"] = (0.0, 0.7, 0.3, 1)
            self.st_desc_label["text"] = "Ping Gateway สำเร็จ! Link Active 100 Mbps"

    def close_station_ui(self):
        self.game_frame.hide()
        self.active_station = None

    def select_color(self, color_name):
        self.selected_color = color_name

    def place_color(self, index):
        if self.selected_color:
            self.logic.set_pin(index, self.selected_color)
            self.update_slots_display()

    def update_slots_display(self):
        for i, color_name in enumerate(self.logic.current_pins):
            if color_name and color_name in COLOR_HEX_MAP:
                # ถ้ามีการกดเลือกสีแล้ว ให้เปลี่ยนปุ่มตามสีนั้น
                self.slot_buttons[i]["frameColor"] = COLOR_HEX_MAP[color_name]
                self.slot_buttons[i]["text"] = color_name[:3]
            else:
                # ถ้ายังไม่ได้เลือก (เป็น None / ค่าว่าง) ให้ตั้งเป็นสีเทาและแสดง P1-P8
                self.slot_buttons[i]["frameColor"] = (0.25, 0.28, 0.35, 1)
                self.slot_buttons[i]["text"] = f"P{i+1}"

    def do_station_action(self):
        if not self.active_station:
            return
        st = self.active_station

        if not self.logic.can_access_station(st):
            self.st_desc_label["text"] = f"สถานีนี้ยังไม่ปลดล็อก! ต้องผ่านสถานีที่ {self.logic.unlocked_station} ก่อน"
            return

        if st == 1 and not self.st1_ready:
            self.st_desc_label["text"] = "โปรดคลิกปุ่ม '[ ลงชื่อเริ่มภารกิจ ]' ก่อนกดผ่าน!"
            return
        elif st == 2 and len(self.st2_selected_items) < 4:
            self.st_desc_label["text"] = "เลือกและหยิบจับอุปกรณ์ยังไม่ครบทั้ง 4 ชิ้น!"
            return
        elif st == 3 and not all(self.st3_steps.values()):
            self.st_desc_label["text"] = "ต้องกดทำขั้นตอน (1. ปอก -> 2. คลายเกลียว -> 3. รีดสาย) ให้ครบ!"
            return
        elif st == 4 and not self.logic.check_pin_correctness():
            self.st_desc_label["text"] = f"การเรียงสี Pin 1-8 ยังไม่ถูกต้องตามมาตรฐาน {self.logic.target_standard}!"
            return
        elif st == 5 and not all(self.st5_steps.values()):
            self.st_desc_label["text"] = "ต้องกดทำขั้นตอน (1. ตัด -> 2. เสียบหัว -> 3. ย้ำหัว) ให้ครบ!"
            return
        elif st == 6 and not self.st6_tested:
            self.st_desc_label["text"] = "ต้องกดปุ่ม 'ตรวจสัญญาณ' เพื่อทดสอบก่อน!"
            return
        elif st == 7 and not all(self.st7_connections.values()):
            self.st_desc_label["text"] = "ต้องกดเชื่อมต่อสาย LAN ทั้ง 2 ปุ่มให้ครบ!"
            return
        elif st == 8 and not all(self.st8_net.values()):
            self.st_desc_label["text"] = "ต้องกดตั้งค่า IP และ Ping ให้ผ่านก่อน!"
            return

        self.logic.complete_station(st)
        self.update_mission_tracker()

        if st == 9:
            self.finish_game()
        else:
            self.st_desc_label["text"] = f"ภารกิจสถานีที่ {st} สำเร็จแล้ว! ปลดล็อกสถานีที่ {st + 1} เรียบร้อย เดินไปทำต่อได้เลย"

    def finish_game(self):
        res = self.logic.evaluate(self.time_left)
        self.stop_timer()
        self.game_frame.hide()

        stars_count = res.get("stars", 0)

        # อัปเดตดาวสีเหลืองตามจำนวนดาวที่ได้จริง
        for i, star_frame in enumerate(self.result_star_frames):
            star_frame.show()
            if i < stars_count:
                star_frame["frameColor"] = (1.0, 0.85, 0.1, 1.0) # สีเหลืองสด (ดวงที่ได้รับ)
            else:
                star_frame["frameColor"] = (0.3, 0.3, 0.35, 1.0) # สีเทาเข้ม (ดวงที่ไม่ได้รับ)

        self.result_stars_summary["text"] = f"( ได้รับ {stars_count} ดาว )"
        self.result_stars_summary["text_fg"] = (1.0, 0.85, 0.1, 1)

        msg_text = res.get("message", "")
        self.result_text["text"] = msg_text
        self.result_frame.show()