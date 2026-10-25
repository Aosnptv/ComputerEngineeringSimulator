"""ฉาก 3D ของห้อง — สร้างจากทรงกล่อง (ไม่ต้องใช้ไฟล์โมเดล) เบาและไม่มี Asset ภายนอก

ค่าตำแหน่ง/ขนาดทั้งหมดเป็นค่าตั้งต้น ปรับได้ที่ SLOT_LAYOUT / TRAY_* ด้านล่าง
ห้องนี้ไม่แตะกล้อง (กล้องเป็นของระบบกลาง)
"""
from panda3d.core import (
    AmbientLight, BitMask32, CollisionBox, CollisionHandlerQueue, CollisionNode,
    CollisionRay, CollisionTraverser, DirectionalLight, Geom, GeomNode,
    GeomTriangles, GeomVertexData, GeomVertexFormat, GeomVertexWriter,
    Point3, TransparencyAttrib,
)

PICK_MASK = BitMask32.bit(1)
NO_MASK = BitMask32.all_off()

# slot_id -> (ตำแหน่ง x,y,z , ขนาด x,y,z)   กล้องมองจากด้าน -Y
SLOT_LAYOUT = {
    "psu":         ((-1.6, -0.20, 0.7), (3.0, 0.40, 1.0)),
    "motherboard": ((-0.5, -0.20, 3.2), (3.4, 0.15, 3.4)),
    "storage":     (( 2.0, -0.25, 1.0), (1.2, 0.30, 1.4)),
    "cpu":         ((-0.3, -0.40, 3.9), (0.8, 0.15, 0.8)),
    "cooler":      ((-0.3, -0.63, 3.9), (1.0, 0.30, 1.0)),
    "ram":         (( 0.7, -0.40, 3.6), (0.25, 0.15, 1.8)),
    "gpu":         ((-0.5, -0.50, 2.3), (2.6, 0.40, 0.6)),
}

PART_COLORS = {
    "mobo_lga": (0.15, 0.55, 0.30, 1), "mobo_am5": (0.55, 0.20, 0.20, 1),
    "cpu_intel": (0.30, 0.50, 0.90, 1), "cpu_amd": (0.90, 0.45, 0.15, 1),
    "cooler_std": (0.70, 0.70, 0.75, 1),
    "ram_ddr4": (0.85, 0.80, 0.20, 1), "ram_ddr5": (0.70, 0.35, 0.85, 1),
    "gpu_std": (0.20, 0.20, 0.25, 1), "ssd_std": (0.25, 0.65, 0.65, 1),
    "psu_std": (0.35, 0.35, 0.35, 1),
}
DEFAULT_COLOR = (0.6, 0.6, 0.6, 1)

TRAY_COLS_X = (4.8, 6.9)
TRAY_TOP_Z = 5.8
TRAY_ROW_STEP = 1.5
TRAY_SCALE = 0.35
CHECK_BUTTON_POS = (5.85, -0.2, -1.8)


def _faces(hx, hy, hz):
    return [
        ((1, 0, 0), [(hx, -hy, -hz), (hx, hy, -hz), (hx, hy, hz), (hx, -hy, hz)]),
        ((-1, 0, 0), [(-hx, hy, -hz), (-hx, -hy, -hz), (-hx, -hy, hz), (-hx, hy, hz)]),
        ((0, 1, 0), [(hx, hy, -hz), (-hx, hy, -hz), (-hx, hy, hz), (hx, hy, hz)]),
        ((0, -1, 0), [(-hx, -hy, -hz), (hx, -hy, -hz), (hx, -hy, hz), (-hx, -hy, hz)]),
        ((0, 0, 1), [(-hx, -hy, hz), (hx, -hy, hz), (hx, hy, hz), (-hx, hy, hz)]),
        ((0, 0, -1), [(-hx, hy, -hz), (hx, hy, -hz), (hx, -hy, -hz), (-hx, -hy, -hz)]),
    ]


def make_box(name, size, color):
    hx, hy, hz = (s / 2 for s in size)
    vdata = GeomVertexData(name, GeomVertexFormat.get_v3n3c4(), Geom.UH_static)
    vw = GeomVertexWriter(vdata, "vertex")
    nw = GeomVertexWriter(vdata, "normal")
    cw = GeomVertexWriter(vdata, "color")
    tris = GeomTriangles(Geom.UH_static)
    base = 0
    for normal, corners in _faces(hx, hy, hz):
        for c in corners:
            vw.add_data3(*c)
            nw.add_data3(*normal)
            cw.add_data4(*color)
        tris.add_vertices(base, base + 1, base + 2)
        tris.add_vertices(base, base + 2, base + 3)
        base += 4
    geom = Geom(vdata)
    geom.add_primitive(tris)
    node = GeomNode(name)
    node.add_geom(geom)
    return node


class RoomScene:
    def __init__(self, parent, render, parts, slots, translator, font=None):
        self._render = render
        self._t = translator
        self._font = font
        self._labels = []          # (TextNode, key, kwargs)
        self._slot_ghost = {}      # slot_id -> NodePath
        self._slot_pick = {}       # slot_id -> CollisionNode
        self._slot_label = {}      # slot_id -> NodePath
        self._part_np = {}         # part_id -> NodePath
        self._part_label = {}      # part_id -> NodePath
        self._part_tray = {}       # part_id -> (pos, label_pos)
        self._installed_at = {}    # part_id -> slot_id
        self._slot_size = {s.kind: SLOT_LAYOUT[s.id][1] for s in slots}

        self.root = parent.attach_new_node("pc_assembly_room")
        self._build_lights()
        self._build_case()
        for s in slots:
            self._build_slot(s)
        for i, p in enumerate(parts):
            self._build_part(i, p)
        self._build_check_button()
        self._build_picker()

    # ---------- สร้างฉาก ----------
    def _build_lights(self):
        amb = AmbientLight("room_amb")
        amb.set_color((0.55, 0.55, 0.6, 1))
        amb_np = self.root.attach_new_node(amb)
        sun = DirectionalLight("room_sun")
        sun.set_color((0.8, 0.8, 0.75, 1))
        sun_np = self.root.attach_new_node(sun)
        sun_np.set_hpr(20, -35, 0)
        self.root.set_light(amb_np)
        self.root.set_light(sun_np)

    def _build_case(self):
        case = self.root.attach_new_node(make_box("case", (6.2, 0.3, 6.6), (0.22, 0.24, 0.3, 1)))
        case.set_pos(0, 0.2, 3.0)

    def _add_pick_box(self, np, size, tag):
        cn = CollisionNode("pick")
        cn.add_solid(CollisionBox(Point3(0, 0, 0), size[0] / 2, size[1] / 2, size[2] / 2))
        cn.set_from_collide_mask(NO_MASK)
        cn.set_into_collide_mask(PICK_MASK)
        cnp = np.attach_new_node(cn)
        cnp.set_tag("pick", tag)
        return cn

    def _make_label(self, key, pos, scale, **kwargs):
        from panda3d.core import TextNode
        tn = TextNode(key)
        tn.set_align(TextNode.A_center)
        tn.set_text_color(1, 1, 1, 1)
        tn.set_wordwrap(7)
        if self._font is not None:
            tn.set_font(self._font)
        tn.set_text(self._t(key, **kwargs))
        np = self.root.attach_new_node(tn)
        np.set_pos(*pos)
        np.set_scale(scale)
        np.set_light_off()
        np.set_billboard_point_eye()
        self._labels.append((tn, key, kwargs))
        return np

    def _build_slot(self, slot):
        pos, size = SLOT_LAYOUT[slot.id]
        ghost = self.root.attach_new_node(make_box(f"ghost_{slot.id}", size, (0.85, 0.92, 1, 1)))
        ghost.set_pos(*pos)
        ghost.set_two_sided(True)
        ghost.set_transparency(TransparencyAttrib.M_alpha)
        ghost.set_color_scale(1, 1, 1, 0.3)
        ghost.set_depth_write(False)
        self._slot_ghost[slot.id] = ghost
        self._slot_pick[slot.id] = self._add_pick_box(ghost, size, f"slot:{slot.id}")
        lp = (pos[0], pos[1] - 0.8, pos[2])
        self._slot_label[slot.id] = self._make_label(f"slot.{slot.id}", lp, 0.22)

    def _build_part(self, index, part):
        size = self._slot_size[part.kind]
        color = PART_COLORS.get(part.id, DEFAULT_COLOR)
        np = self.root.attach_new_node(make_box(f"part_{part.id}", size, color))
        np.set_two_sided(True)
        self._add_pick_box(np, size, f"part:{part.id}")
        x = TRAY_COLS_X[index % 2]
        z = TRAY_TOP_Z - (index // 2) * TRAY_ROW_STEP
        self._part_np[part.id] = np
        self._part_label[part.id] = self._make_label(
            f"part.{part.id}", (x, -0.6, z - 0.75), 0.2)
        self._part_tray[part.id] = ((x, 0.0, z), None)
        self._to_tray(part.id)

    def _build_check_button(self):
        np = self.root.attach_new_node(make_box("check_btn", (1.8, 0.2, 0.6), (0.2, 0.6, 0.3, 1)))
        np.set_pos(*CHECK_BUTTON_POS)
        self._add_pick_box(np, (1.8, 0.2, 0.6), "button:check")
        lp = (CHECK_BUTTON_POS[0], CHECK_BUTTON_POS[1] - 0.2, CHECK_BUTTON_POS[2] - 0.08)
        self._make_label("ui.check", lp, 0.28)

    def _build_picker(self):
        self._trav = CollisionTraverser("room_picker")
        self._queue = CollisionHandlerQueue()
        self._ray = CollisionRay()
        cn = CollisionNode("room_ray")
        cn.add_solid(self._ray)
        cn.set_from_collide_mask(PICK_MASK)
        cn.set_into_collide_mask(NO_MASK)
        self._ray_np = self.root.attach_new_node(cn)
        self._trav.add_collider(self._ray_np, self._queue)

    # ---------- ใช้งานจากห้อง ----------
    def pick(self, origin, direction):
        """คืนค่า 'part:<id>' | 'slot:<id>' | 'button:check' หรือ None"""
        self._ray.set_origin(self.root.get_relative_point(self._render, origin))
        self._ray.set_direction(self.root.get_relative_vector(self._render, direction))
        self._trav.traverse(self.root)
        self._queue.sort_entries()
        for i in range(self._queue.get_num_entries()):
            into = self._queue.get_entry(i).get_into_node_path()
            if into.has_net_tag("pick"):
                return into.get_net_tag("pick")
        return None

    def show_installed(self, part_id, slot_id):
        pos, _ = SLOT_LAYOUT[slot_id]
        np = self._part_np[part_id]
        np.set_scale(1)
        np.set_pos(*pos)
        self._part_label[part_id].hide()
        self._slot_ghost[slot_id].hide()
        self._slot_label[slot_id].hide()
        self._slot_pick[slot_id].set_into_collide_mask(NO_MASK)
        self._installed_at[part_id] = slot_id

    def show_in_tray(self, part_id):
        slot_id = self._installed_at.pop(part_id, None)
        if slot_id is not None:
            self._slot_ghost[slot_id].show()
            self._slot_label[slot_id].show()
            self._slot_pick[slot_id].set_into_collide_mask(PICK_MASK)
        self._to_tray(part_id)

    def _to_tray(self, part_id):
        np = self._part_np[part_id]
        np.set_scale(TRAY_SCALE)
        np.set_pos(*self._part_tray[part_id][0])
        self._part_label[part_id].show()

    def set_selected(self, part_id):
        for pid, np in self._part_np.items():
            np.set_color_scale(1.7, 1.7, 0.7, 1) if pid == part_id else np.set_color_scale(1, 1, 1, 1)

    def reset_visuals(self):
        for pid in list(self._part_np):
            self.show_in_tray(pid)
        self.set_selected(None)

    def set_translator(self, translator):
        self._t = translator
        self.refresh_labels()

    def refresh_labels(self):
        for tn, key, kwargs in self._labels:
            tn.set_text(self._t(key, **kwargs))

    def destroy(self):
        self._trav.clear_colliders()
        self.root.remove_node()
