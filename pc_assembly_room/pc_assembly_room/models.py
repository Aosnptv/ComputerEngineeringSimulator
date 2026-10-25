"""โมเดลชิ้นส่วนคอมพิวเตอร์ที่สร้างจากทรงพื้นฐานด้วยโค้ด (หน่วย = เมตร, ขนาดจริง)

แกนของโมเดลเป็นแบบ "ติดตั้งในเคส": ด้านหน้า (ด้านที่ผู้เล่นเห็นตอนติดตั้ง) คือ -Y
จุดกึ่งกลางโมเดลอยู่ที่ origin และอยู่ภายในกรอบขนาดเดียวกับ slot
ไม่ใช้ไฟล์โมเดลหรือ Dependency ใด ๆ
"""
import math

from panda3d.core import (
    Geom, GeomNode, GeomTriangles, GeomVertexData, GeomVertexFormat,
    GeomVertexWriter, NodePath,
)

from .logic import Kind
from .scene import make_box

# ท่านอนบนโต๊ะ (hpr) เพื่อให้ด้านที่ดูรู้เรื่องหงายขึ้น; ค่าตั้งต้น = ด้านหน้า (-Y) หงายขึ้น
TRAY_HPR = {Kind.GPU: (0, 0, 180), Kind.RAM: (0, 0, 90)}
DEFAULT_TRAY_HPR = (0, -90, 0)
# ท่าตอนถือ (offset ของ h,p,r เทียบกับทิศมองของผู้เล่น) ให้ด้านที่ดูรู้เรื่องหันเข้าหาตา
HOLD_HPR = {Kind.GPU: (0, -90, 0), Kind.RAM: (90, 0, 0)}
# กล่องสำหรับคลิก (ขนาด, จุดกึ่งกลาง) ถ้าต่างจากกรอบเต็ม — เมนบอร์ดใช้เฉพาะแผ่น PCB
# เพื่อไม่ให้บังการคลิกชิ้นส่วนที่ติดตั้งอยู่บนบอร์ด
PICK_OVERRIDE = {Kind.MOTHERBOARD: ((0.244, 0.004, 0.305), (0, 0.008, 0))}


def rest_half_height(kind, size):
    """ครึ่งหนึ่งของความสูงเมื่อวางบนโต๊ะตามท่า TRAY_HPR"""
    sx, sy, sz = size
    if kind is Kind.GPU:
        return sz / 2
    if kind is Kind.RAM:
        return sx / 2
    return sy / 2


# ---------------------------------------------------------------- เรขาคณิต
def _mesh(name, verts, tris, color):
    vdata = GeomVertexData(name, GeomVertexFormat.get_v3n3c4(), Geom.UH_static)
    vw = GeomVertexWriter(vdata, "vertex")
    nw = GeomVertexWriter(vdata, "normal")
    cw = GeomVertexWriter(vdata, "color")
    for p, n in verts:
        vw.add_data3(*p)
        nw.add_data3(*n)
        cw.add_data4(*color)
    prim = GeomTriangles(Geom.UH_static)
    for a, b, c in tris:
        prim.add_vertices(a, b, c)
    geom = Geom(vdata)
    geom.add_primitive(prim)
    node = GeomNode(name)
    node.add_geom(geom)
    return node


def make_cylinder(name, radius, height, color, segments=20):
    """ทรงกระบอกแกน Z กึ่งกลางที่ origin"""
    h = height / 2
    verts, tris = [], []
    for i in range(segments + 1):
        a = 2 * math.pi * i / segments
        c, s = math.cos(a), math.sin(a)
        verts.append(((radius * c, radius * s, -h), (c, s, 0)))
        verts.append(((radius * c, radius * s, h), (c, s, 0)))
    for i in range(segments):
        b = i * 2
        tris.append((b, b + 2, b + 1))
        tris.append((b + 1, b + 2, b + 3))
    for z, nz in ((h, 1), (-h, -1)):
        center = len(verts)
        verts.append(((0, 0, z), (0, 0, nz)))
        for i in range(segments + 1):
            a = 2 * math.pi * i / segments
            verts.append(((radius * math.cos(a), radius * math.sin(a), z), (0, 0, nz)))
        for i in range(segments):
            tris.append((center, center + 1 + i, center + 2 + i))
    return _mesh(name, verts, tris, color)


class _B:
    """ตัวช่วยประกอบโมเดลจากกล่อง/ทรงกระบอก"""

    def __init__(self, name):
        self.np = NodePath(name)

    def box(self, size, pos, color, parent=None):
        n = (parent or self.np).attach_new_node(make_box("b", size, color))
        n.set_pos(*pos)
        return n

    def cyl(self, radius, height, pos, color, axis="z", segments=20, parent=None):
        n = (parent or self.np).attach_new_node(make_cylinder("c", radius, height, color, segments))
        n.set_pos(*pos)
        if axis == "y":
            n.set_p(90)
        elif axis == "x":
            n.set_r(90)
        return n

    def fan(self, center, radius, axis, disc_color, blade_color, blades=7):
        """พัดลม: แผ่นหลัง + แกนกลาง + ใบพัด (ด้านหน้าของพัดลมหันไปทาง -Y เมื่อ axis='y')"""
        o = self.np.attach_new_node("fan")
        o.set_pos(*center)
        if axis == "y":
            o.set_p(90)
        self.cyl(radius, 0.002, (0, 0, 0), disc_color, parent=o)
        self.cyl(radius * 0.28, 0.005, (0, 0, 0.002), blade_color, parent=o)
        for i in range(blades):
            piv = o.attach_new_node("blade")
            piv.set_h(360.0 * i / blades)
            blade = self.box((radius * 0.62, radius * 0.3, 0.0012), (radius * 0.58, 0, 0.002), blade_color, parent=piv)
            blade.set_r(18)
        return o


STYLE = {
    "mobo_lga": dict(pcb=(0.05, 0.26, 0.12, 1), accent=(0.2, 0.6, 0.95, 1)),
    "mobo_am5": dict(pcb=(0.07, 0.07, 0.09, 1), accent=(0.9, 0.2, 0.2, 1)),
    "cpu_intel": dict(ihs=(0.78, 0.8, 0.84, 1), sub=(0.1, 0.35, 0.2, 1)),
    "cpu_amd": dict(ihs=(0.72, 0.7, 0.66, 1), sub=(0.1, 0.3, 0.18, 1)),
    "ram_ddr4": dict(spreader=(0.12, 0.12, 0.14, 1), accent=(0.95, 0.8, 0.2, 1)),
    "ram_ddr5": dict(spreader=(0.85, 0.85, 0.88, 1), accent=(0.7, 0.35, 0.9, 1)),
}
DEFAULT_STYLE = dict(pcb=(0.1, 0.1, 0.1, 1), accent=(0.8, 0.8, 0.8, 1))
SILVER = (0.78, 0.79, 0.82, 1)
DARK = (0.1, 0.1, 0.12, 1)
GOLD = (0.85, 0.7, 0.25, 1)


# ---------------------------------------------------------------- ชิ้นส่วน
def _motherboard(part):
    st = STYLE.get(part.id, DEFAULT_STYLE)
    b = _B(part.id)
    b.box((0.244, 0.002, 0.305), (0, 0.008, 0), st["pcb"])

    def on(h):  # กลาง y ของชิ้นที่สูง h วางบนหน้า PCB (หน้า PCB อยู่ที่ y=0.007)
        return 0.007 - h / 2

    b.box((0.058, 0.004, 0.058), (0.055, on(0.004), 0.0675), (0.15, 0.15, 0.17, 1))  # ซ็อกเก็ต CPU
    b.box((0.09, 0.012, 0.014), (0.045, on(0.012), 0.125), (0.3, 0.3, 0.33, 1))      # ฮีตซิงก์ VRM บน
    b.box((0.014, 0.012, 0.09), (0.095, on(0.012), 0.045), (0.3, 0.3, 0.33, 1))      # ฮีตซิงก์ VRM ข้าง
    b.box((0.02, 0.016, 0.1), (0.112, on(0.016), 0.06), SILVER)                       # ช่อง I/O ด้านหลัง
    for dx in (-0.06, -0.045, -0.03, -0.015):                                         # ช่อง RAM
        b.box((0.0085, 0.008, 0.133), (dx, on(0.008), 0.0675), (0.1, 0.1, 0.12, 1))
    b.box((0.16, 0.011, 0.0125), (-0.03, on(0.011), -0.0725), (0.08, 0.08, 0.09, 1))  # PCIe x16
    b.box((0.05, 0.009, 0.011), (-0.07, on(0.009), -0.1), (0.9, 0.9, 0.88, 1))        # PCIe x1
    b.box((0.012, 0.014, 0.05), (-0.11, on(0.014), 0.03), (0.92, 0.92, 0.88, 1))      # ขั้ว 24 พิน
    b.box((0.035, 0.01, 0.03), (0.08, on(0.01), -0.125), st["accent"])                # ชิปเซ็ต
    for i in range(3):                                                                # ตัวเก็บประจุ
        b.cyl(0.0035, 0.012, (-0.11 + 0.015 * i, on(0.012), 0.12), DARK, axis="y", segments=10)
    return b.np


def _cpu(part):
    st = STYLE.get(part.id, DEFAULT_STYLE)
    b = _B(part.id)
    b.box((0.045, 0.002, 0.045), (0, 0.004, 0), st["sub"])
    b.box((0.038, 0.004, 0.038), (0, 0.001, 0), st["ihs"])
    for sx in (-1, 1):  # รอยบากมุม
        b.box((0.004, 0.0005, 0.004), (sx * 0.02, 0.0028, 0.02), GOLD)
    return b.np


def _cooler(part):
    b = _B(part.id)
    b.box((0.05, 0.006, 0.05), (0, 0.027, 0), (0.75, 0.45, 0.25, 1))                  # แผ่นฐานทองแดง
    for dx in (-0.015, -0.005, 0.005, 0.015):                                         # ท่อความร้อน
        b.cyl(0.003, 0.006, (dx, 0.023, 0), (0.7, 0.42, 0.22, 1), axis="y", segments=10)
    for i in range(9):                                                                # ครีบ
        b.box((0.11, 0.0025, 0.11), (0, 0.020 - i * 0.0055, 0), SILVER)
    b.box((0.12, 0.004, 0.12), (0, -0.028, 0), DARK)                                  # กรอบพัดลม
    b.fan((0, -0.031, 0), 0.05, "y", (0.07, 0.07, 0.08, 1), (0.2, 0.2, 0.22, 1))
    return b.np


def _ram(part):
    st = STYLE.get(part.id, DEFAULT_STYLE)
    b = _B(part.id)
    b.box((0.0016, 0.032, 0.133), (0, 0, 0), (0.05, 0.25, 0.12, 1))                   # PCB
    b.box((0.0018, 0.003, 0.12), (0, 0.0145, 0), GOLD)                                # ขาทอง
    for sx in (-1, 1):                                                                # ฮีตสเปรดเดอร์ 2 ด้าน
        b.box((0.0032, 0.026, 0.128), (sx * 0.0024, -0.002, 0), st["spreader"])
    b.box((0.0068, 0.004, 0.12), (0, -0.0155, 0), st["accent"])                       # แถบสีด้านบน
    return b.np


def _gpu(part):
    b = _B(part.id)
    b.box((0.30, 0.11, 0.002), (0, 0, 0.019), (0.08, 0.08, 0.09, 1))                  # แบ็กเพลท (+Z)
    b.box((0.285, 0.105, 0.002), (0, 0, 0.016), (0.05, 0.28, 0.12, 1))                # PCB
    b.box((0.30, 0.11, 0.034), (0, 0, -0.003), (0.12, 0.12, 0.14, 1))                 # โครงฮีตซิงก์/ชรูด
    for x in (-0.09, 0.0, 0.09):                                                      # พัดลม 3 ตัว (หันลง -Z)
        o = b.fan((x, 0, -0.0200), 0.04, "z", (0.04, 0.04, 0.05, 1), (0.22, 0.22, 0.25, 1), blades=9)
        o.set_p(180)
    b.box((0.26, 0.002, 0.006), (0, -0.0545, 0), (0.2, 0.9, 0.4, 1))                  # แถบ LED ด้านหน้า
    b.box((0.06, 0.001, 0.012), (-0.1, -0.0548, 0), SILVER)                           # ป้ายยี่ห้อ
    b.box((0.002, 0.10, 0.04), (0.149, 0, 0), SILVER)                                 # แผ่นเหล็กท้ายการ์ด
    b.box((0.075, 0.002, 0.003), (-0.03, 0.054, 0.016), GOLD)                         # ขาทอง PCIe
    return b.np


def _ssd(part):
    b = _B(part.id)
    b.box((0.10, 0.0095, 0.07), (0, 0, 0), (0.7, 0.72, 0.75, 1))
    b.box((0.085, 0.0008, 0.055), (0, -0.0049, 0), DARK)
    b.box((0.085, 0.0009, 0.008), (0, -0.0052, 0.0225), (0.95, 0.5, 0.1, 1))
    for sx in (-1, 1):
        for sz in (-1, 1):
            b.cyl(0.0025, 0.001, (sx * 0.044, -0.0048, sz * 0.03), (0.4, 0.4, 0.42, 1), axis="y", segments=8)
    return b.np


def _psu(part):
    b = _B(part.id)
    b.box((0.15, 0.14, 0.086), (0, 0, 0), (0.16, 0.16, 0.18, 1))
    b.box((0.10, 0.001, 0.05), (0, -0.0705, 0), (0.92, 0.92, 0.9, 1))                 # สติกเกอร์ฉลาก
    b.box((0.10, 0.0012, 0.012), (0, -0.0707, 0.014), (0.9, 0.55, 0.1, 1))
    b.box((0.03, 0.002, 0.02), (0.045, 0.071, 0.0), (0.3, 0.3, 0.32, 1))              # ขั้วปลั๊ก AC
    return b.np


_BUILDERS = {
    Kind.MOTHERBOARD: _motherboard, Kind.CPU: _cpu, Kind.COOLER: _cooler,
    Kind.RAM: _ram, Kind.GPU: _gpu, Kind.STORAGE: _ssd, Kind.PSU: _psu,
}


def build_part(part):
    """คืน NodePath ของโมเดลชิ้นส่วน (สองหน้า เพราะใช้ทรงกล่องที่ไม่ได้เรียงด้านให้ตรงทิศ)"""
    np = _BUILDERS[part.kind](part)
    np.set_two_sided(True)
    return np
