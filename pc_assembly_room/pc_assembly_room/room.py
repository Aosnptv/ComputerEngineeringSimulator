"""PCAssemblyRoom — จุดเชื่อมของห้อง

*** วงจรชีวิต (enter / exit / reset / on_complete) เป็นร่างชั่วคราว ***
ต้องปรับให้ตรงกับ API ที่ผู้ดูแลสถาปัตยกรรมประกาศ
"""
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Filename

from .data import PARTS, RULES, SLOTS
from .logic import AssemblyState, Code
from .pointer import DesktopMousePointer
from .scene import RoomScene
from .strings import make_translator


class PCAssemblyRoom(DirectObject):
    def __init__(self, base, translator=None, font_path=None, pointer=None, on_complete=None):
        """
        base        : ShowBase ของโปรแกรม (ห้องไม่สร้างหน้าต่างเอง)
        translator  : t(key, **kw) -> str  (ไม่ส่ง = ใช้ภาษาไทยของห้องเอง)
        font_path   : ไฟล์ฟอนต์ที่มีตัวอักษรไทย (ฟอนต์ตั้งต้นของ Panda3D แสดงภาษาไทยไม่ได้)
        pointer     : ตัวชี้ (ไม่ส่ง = เมาส์)
        on_complete : callback(result: dict) เรียกครั้งเดียวเมื่อตรวจแล้วถูกต้อง
        """
        super().__init__()
        self.base = base
        self._t = translator or make_translator("th")
        self._font_path = font_path
        self._pointer = pointer or DesktopMousePointer(base)
        self._on_complete = on_complete
        self._font = None
        self._entered = False
        self._completed = False
        self.state = None
        self.scene = None
        self._status = None
        self._mistakes_text = None
        self._hint = None

    # ---------- วงจรชีวิต ----------
    def enter(self, parent):
        if self._entered:
            return
        self._entered = True
        self._completed = False
        if self._font_path:
            try:
                # แปลง path แบบ Windows ให้เป็นรูปแบบที่ Panda3D เข้าใจ
                self._font = self.base.loader.load_font(Filename.from_os_specific(self._font_path))
            except Exception as e:
                self._font = None  # ใช้ฟอนต์ตั้งต้น (ภาษาไทยจะแสดงเป็นกล่อง)
                print(f"[PCAssemblyRoom] โหลดฟอนต์ไม่ได้: {self._font_path} ({e})")
        else:
            print("[PCAssemblyRoom] ไม่ได้ระบุ --font ภาษาไทยจะแสดงเป็นกล่อง")
        self.state = AssemblyState(PARTS, SLOTS, RULES)
        self.scene = RoomScene(parent, self.base.render, PARTS, SLOTS, self._t, self._font)
        kw = dict(parent=self.base.aspect2d, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1),
                  font=self._font, mayChange=True)
        self._hint = OnscreenText(text=self._t("ui.hint"), pos=(0, 0.92), scale=0.045, **kw)
        self._status = OnscreenText(text="", pos=(0, 0.84), scale=0.06, **kw)
        self._mistakes_text = OnscreenText(text="", pos=(-1.2, -0.92), scale=0.05,
                                           align=0, **kw)
        self._refresh_mistakes()
        self.accept(self._pointer.activate_event, self._on_click)

    def exit(self):
        """ปิดห้องและคืนทรัพยากรทั้งหมด"""
        if not self._entered:
            return
        self.ignore_all()
        for w in (self._hint, self._status, self._mistakes_text):
            if w is not None:
                w.destroy()
        self._hint = self._status = self._mistakes_text = None
        if self.scene is not None:
            self.scene.destroy()
        self.scene = None
        self.state = None
        self._entered = False

    def reset(self):
        if not self._entered:
            return
        self.state.reset()
        self.scene.reset_visuals()
        self._completed = False
        self._status.setText("")
        self._refresh_mistakes()

    def set_translator(self, translator):
        self._t = translator
        if self._entered:
            self.scene.set_translator(translator)
            self._hint.setText(self._t("ui.hint"))
            self._refresh_mistakes()

    @property
    def mistakes(self):
        return self.state.mistakes if self.state else 0

    # ---------- การคลิก ----------
    def _on_click(self):
        ray = self._pointer.get_ray()
        if ray is None:
            return
        key = self.scene.pick(*ray)
        if key is None:
            return
        kind, _, ident = key.partition(":")
        if kind == "part":
            self._click_part(ident)
        elif kind == "slot":
            self._click_slot(ident)
        elif kind == "button":
            self._click_check()
        self._refresh_mistakes()

    def _click_part(self, part_id):
        slot_id = self.state.slot_of(part_id)
        if slot_id is not None:  # คลิกชิ้นที่ติดตั้งแล้ว = ถอดออก
            result = self.state.remove(slot_id)
            if result.ok:
                self.scene.show_in_tray(part_id)
            self._say(result, "msg.ok_remove")
        elif self.state.selected == part_id:
            self.state.deselect()
            self.scene.set_selected(None)
            self._status.setText(self._t("msg.deselected"))
        else:
            result = self.state.select(part_id)
            if result.ok:
                self.scene.set_selected(part_id)
            self._say(result, "msg.ok_select")

    def _click_slot(self, slot_id):
        result = self.state.place(slot_id)
        if result.ok:
            self.scene.show_installed(result.part, slot_id)
            self.scene.set_selected(None)
        self._say(result, "msg.ok_place")

    def _click_check(self):
        res = self.state.check()
        if res.complete:
            self._status.setText(self._t("msg.check_complete"))
            if not self._completed:
                self._completed = True
                if self._on_complete:
                    self._on_complete({"mistakes": self.state.mistakes})
        else:
            n = len(res.missing) + len(res.conflicts)
            self._status.setText(self._t("msg.check_incomplete", n=n))

    # ---------- ข้อความ ----------
    def _say(self, result, ok_key):
        key = ok_key if result.code is Code.OK else "msg." + result.code.value
        kw = {}
        if result.part:
            kw["part"] = self._t(f"part.{result.part}")
        if result.slot:
            kw["slot"] = self._t(f"slot.{result.slot}")
        self._status.setText(self._t(key, **kw))

    def _refresh_mistakes(self):
        if self._mistakes_text is not None:
            self._mistakes_text.setText(self._t("ui.mistakes", n=self.state.mistakes))