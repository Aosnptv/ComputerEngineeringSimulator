"""ตัวชี้ (pointer) — ชั้นแยกอินพุตออกจากห้อง เพื่อเปลี่ยนเป็นคอนโทรลเลอร์ VR ภายหลัง

ทุก Pointer ต้องมี:
  activate_event : ชื่อ event ที่ใช้ "กดเลือก"
  get_ray()      : คืน (origin, direction) ใน world space หรือ None
ห้องใช้เพียงสองอย่างนี้ จึงไม่ผูกกับเมาส์
"""
from panda3d.core import Point3, Vec3


class DesktopMousePointer:
    activate_event = "mouse1"

    def __init__(self, base):
        self._base = base

    def get_ray(self):
        b = self._base
        if not b.mouseWatcherNode.has_mouse():
            return None
        near, far = Point3(), Point3()
        if not b.camLens.extrude(b.mouseWatcherNode.get_mouse(), near, far):
            return None
        near_w = b.render.get_relative_point(b.cam, near)
        far_w = b.render.get_relative_point(b.cam, far)
        direction = Vec3(far_w - near_w)
        direction.normalize()
        return near_w, direction
