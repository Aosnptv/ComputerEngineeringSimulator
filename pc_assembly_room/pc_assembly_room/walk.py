"""การเดิน/มองรอบแบบบุคคลที่หนึ่งบนจอ Desktop + ตัวชี้ (pointer) แบบกึ่งกลางจอ

*** กล้อง/การควบคุมเป็นของระบบกลาง *** ไฟล์นี้ใช้ในตัวทดสอบเดี่ยว (run_walkthrough.py) เท่านั้น
เมื่อระบบกลางมีกล้อง/การควบคุมแล้ว ให้ใช้ของกลางแทน แล้วเขียน pointer ที่มี 4 อย่างเดียวกัน:
  activate_event, cancel_event, get_ray(), get_hold_pose()
(ภายหลัง VR: คอนโทรลเลอร์คืนค่าสี่อย่างนี้แทน — ห้องไม่ต้องแก้)
"""
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Point3, Vec3, WindowProperties


class FirstPersonController:
    def __init__(self, base, start=(0.0, 0.0), heading=0.0, bounds=None, obstacles=(),
                 eye_height=1.65, speed=2.0, sensitivity=0.12):
        self.enabled = True
        self.base = base
        self.x, self.y = start
        self.heading, self.pitch = heading, 0.0
        self.bounds = bounds
        self.obstacles = list(obstacles)
        self.eye = eye_height
        self.speed = speed
        self.sens = sensitivity
        self._keys = {"w": False, "a": False, "s": False, "d": False}
        self._skip = 2  # ข้ามเฟรมแรก ๆ เพื่อไม่ให้กล้องกระโดด
        self._obj = DirectObject()
        for k in self._keys:
            self._obj.accept(k, self._set, [k, True])
            self._obj.accept(k + "-up", self._set, [k, False])
        base.disable_mouse()
        props = WindowProperties()
        props.set_cursor_hidden(True)
        base.win.request_properties(props)
        self._task = base.task_mgr.add(self._update, "walk_update")
        self._apply()

    def set_enabled(self, enabled):
        self.enabled = enabled
        self._skip = 2
        for key in self._keys:
            self._keys[key] = False
        props = WindowProperties()
        props.set_cursor_hidden(enabled)
        self.base.win.request_properties(props)

    def _set(self, key, value):
        self._keys[key] = value if self.enabled else False

    def _blocked(self, x, y):
        if self.bounds:
            x0, x1, y0, y1 = self.bounds
            if not (x0 <= x <= x1 and y0 <= y <= y1):
                return True
        for ax0, ax1, ay0, ay1 in self.obstacles:
            if ax0 < x < ax1 and ay0 < y < ay1:
                return True
        return False

    def _apply(self):
        cam = self.base.camera
        cam.set_pos(self.x, self.y, self.eye)
        cam.set_hpr(self.heading, self.pitch, 0)

    def _update(self, task):
        if not self.enabled:
            return task.cont
        from direct.showbase.ShowBaseGlobal import globalClock
        base = self.base
        props = base.win.get_properties()
        if props.get_foreground():
            cx, cy = props.get_x_size() // 2, props.get_y_size() // 2
            md = base.win.get_pointer(0)
            if self._skip > 0:
                self._skip -= 1
            else:
                self.heading -= (md.get_x() - cx) * self.sens
                self.pitch = max(-80.0, min(80.0, self.pitch - (md.get_y() - cy) * self.sens))
            base.win.move_pointer(0, cx, cy)
        else:
            self._skip = 2
            for key in self._keys:
                self._keys[key] = False
        dt = min(globalClock.get_dt(), 0.05)
        fwd = (1 if self._keys["w"] else 0) - (1 if self._keys["s"] else 0)
        strafe = (1 if self._keys["d"] else 0) - (1 if self._keys["a"] else 0)
        if fwd or strafe:
            import math
            h = math.radians(self.heading)
            fx, fy = -math.sin(h), math.cos(h)      # ทิศหน้า
            rx, ry = math.cos(h), math.sin(h)       # ทิศขวา
            dx = (fx * fwd + rx * strafe) * self.speed * dt
            dy = (fy * fwd + ry * strafe) * self.speed * dt
            if not self._blocked(self.x + dx, self.y):
                self.x += dx
            if not self._blocked(self.x, self.y + dy):
                self.y += dy
        self._apply()
        return task.cont

    def destroy(self):
        self._obj.ignore_all()
        if self._task is not None:
            self._task.remove()
            self._task = None
        props = WindowProperties()
        props.set_cursor_hidden(False)
        self.base.win.request_properties(props)


class FirstPersonPointer:
    """ตัวชี้ที่กึ่งกลางจอ: ซ้าย = หยิบ/วาง, ขวา = คืนชิ้นส่วนที่ถืออยู่"""
    activate_event = "mouse1"
    cancel_event = "mouse3"

    def __init__(self, base):
        self._base = base

    def get_ray(self):
        b = self._base
        origin = b.camera.get_pos(b.render)
        direction = Vec3(b.render.get_relative_vector(b.camera, Vec3(0, 1, 0)))
        direction.normalize()
        return Point3(origin), direction

    def get_hold_pose(self):
        """(ตำแหน่งที่ถือชิ้นส่วนใน world, ทิศ heading)"""
        b = self._base
        pos = b.render.get_relative_point(b.camera, Point3(0.18, 0.7, -0.2))
        return pos, b.camera.get_h(b.render)
