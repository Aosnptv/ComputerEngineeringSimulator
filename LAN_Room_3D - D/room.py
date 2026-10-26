# room.py
import random
from panda3d.core import (
    CardMaker, TextNode, Vec3, Vec4,
    AmbientLight, DirectionalLight, Material
)


def create_solid_cube_3d(parent, pos, scale, color, name="solid_cube"):
    cube = parent.attachNewNode(name)
    cm = CardMaker(name + "_face")
    cm.setFrame(-0.5, 0.5, -0.5, 0.5)

    faces = [
        (Vec3(0, 0, 0.5), Vec3(0, 0, 0)),
        (Vec3(0, 0, -0.5), Vec3(0, 180, 0)),
        (Vec3(0, -0.5, 0), Vec3(90, 0, 0)),
        (Vec3(0, 0.5, 0), Vec3(-90, 0, 0)),
        (Vec3(-0.5, 0, 0), Vec3(0, 90, 0)),
        (Vec3(0.5, 0, 0), Vec3(0, -90, 0)),
    ]

    for face_pos, face_hpr in faces:
        face = cube.attachNewNode(cm.generate())
        face.setPos(face_pos)
        face.setHpr(face_hpr)
        face.setColor(color)
        face.setTwoSided(True)

    cube.setPos(pos)
    cube.setScale(scale)

    mat = Material()
    mat.setSpecular(Vec4(0, 0, 0, 0))
    mat.setShininess(0.0)
    cube.setMaterial(mat, 1)
    cube.setLightOff()
    return cube


def create_station_signboard_3d(parent, pos, number_str, title_str, sub_desc="", font=None, hide_hints=False):
    sign_group = parent.attachNewNode(f"signboard_{number_str}")
    sign_group.setPos(pos)

    create_solid_cube_3d(sign_group, Vec3(0, 0, 0), Vec3(3.4, 0.08, 0.85), Vec4(0.12, 0.16, 0.22, 1), "sign_bg")
    create_solid_cube_3d(sign_group, Vec3(-1.2, -0.06, 0), Vec3(0.7, 0.02, 0.7), Vec4(0.18, 0.42, 0.65, 1), "num_box")

    tn_num = TextNode("num")
    tn_num.setText(number_str)
    tn_num.setAlign(TextNode.ACenter)
    tn_num.setTextColor(1, 1, 1, 1)
    t_num = sign_group.attachNewNode(tn_num)
    t_num.setPos(-1.2, -0.08, -0.22)
    t_num.setScale(0.55)

    if not hide_hints:
        tn_title = TextNode("title")
        if font: tn_title.setFont(font)
        tn_title.setText(title_str)
        tn_title.setTextColor(0.3, 0.8, 0.95, 1)
        t_title = sign_group.attachNewNode(tn_title)
        t_title.setPos(-0.7, -0.08, 0.08)
        t_title.setScale(0.28)

        if sub_desc:
            tn_sub = TextNode("sub")
            if font: tn_sub.setFont(font)
            tn_sub.setText(sub_desc)
            tn_sub.setTextColor(0.75, 0.78, 0.82, 1)
            t_sub = sign_group.attachNewNode(tn_sub)
            t_sub.setPos(-0.7, -0.08, -0.25)
            t_sub.setScale(0.18)
    else:
        # โหมดยาก: มีเฉพาะตัวเลขสถานี ไม่มีคำใบ้/ชื่อภารกิจ
        tn_title = TextNode("title_hard")
        if font: tn_title.setFont(font)
        tn_title.setText(f"สถานีที่ {number_str}")
        tn_title.setTextColor(0.85, 0.3, 0.3, 1)
        t_title = sign_group.attachNewNode(tn_title)
        t_title.setPos(-0.7, -0.08, -0.05)
        t_title.setScale(0.24)

    return sign_group


def create_station_desk(parent, pos, desk_color, station_num):
    desk_group = parent.attachNewNode(f"desk_st_{station_num}")
    desk_group.setPos(pos)

    create_solid_cube_3d(desk_group, Vec3(0, 0, 1.0), Vec3(3.4, 1.6, 0.15), Vec4(0.75, 0.78, 0.82, 1), "desk_top")
    create_solid_cube_3d(desk_group, Vec3(0, -0.82, 0.95), Vec3(3.4, 0.05, 0.18), desk_color, "desk_edge")

    leg_color = Vec4(0.22, 0.24, 0.28, 1)
    for i, leg in enumerate([Vec3(-1.5, -0.6, 0.45), Vec3(1.5, -0.6, 0.45), Vec3(-1.5, 0.6, 0.45), Vec3(1.5, 0.6, 0.45)]):
        create_solid_cube_3d(desk_group, leg, Vec3(0.12, 0.12, 0.9), leg_color, f"leg_{i}")
    create_solid_cube_3d(desk_group, Vec3(1.1, 0, 0.45), Vec3(0.85, 1.4, 0.8), Vec4(0.55, 0.58, 0.62, 1), "cabinet")

    if station_num in ["2", "3", "4", "5", "6"]:
        create_solid_cube_3d(desk_group, Vec3(0, 0.76, 2.0), Vec3(3.2, 0.08, 1.8), Vec4(0.14, 0.20, 0.28, 1), "pegboard_back")

    if station_num == "1":
        create_solid_cube_3d(desk_group, Vec3(0, 0.3, 1.62), Vec3(1.4, 0.1, 0.9), Vec4(0.12, 0.3, 0.55, 1), "main_screen")
        create_solid_cube_3d(desk_group, Vec3(0, 0.3, 1.1), Vec3(0.2, 0.2, 0.2), Vec4(0.2, 0.2, 0.2, 1), "screen_stand")
    elif station_num == "2":
        create_solid_cube_3d(desk_group, Vec3(-1.0, -0.2, 1.22), Vec3(0.7, 0.7, 0.25), Vec4(0.1, 0.4, 0.7, 1), "utp_roll")
        create_solid_cube_3d(desk_group, Vec3(-0.3, -0.2, 1.17), Vec3(0.4, 0.4, 0.15), Vec4(0.75, 0.78, 0.82, 1), "rj45_box")
        create_solid_cube_3d(desk_group, Vec3(0.4, 0.68, 2.1), Vec3(0.15, 0.1, 0.6), Vec4(0.75, 0.35, 0.1, 1), "crimper_tool")
        create_solid_cube_3d(desk_group, Vec3(1.0, 0.68, 2.0), Vec3(0.35, 0.1, 0.55), Vec4(0.15, 0.55, 0.3, 1), "tester_unit")
    elif station_num == "3":
        create_solid_cube_3d(desk_group, Vec3(-0.6, 0.0, 1.14), Vec3(1.2, 0.12, 0.08), Vec4(0.1, 0.4, 0.7, 1), "stripped_cable")
        create_solid_cube_3d(desk_group, Vec3(0.5, 0.0, 1.14), Vec3(0.25, 0.4, 0.08), Vec4(0.75, 0.65, 0.15, 1), "stripper_tool")
    elif station_num == "4":
        colors = [
            Vec4(0.85, 0.60, 0.35, 1), Vec4(0.85, 0.40, 0.15, 1),
            Vec4(0.50, 0.80, 0.50, 1), Vec4(0.15, 0.35, 0.75, 1),
            Vec4(0.45, 0.60, 0.85, 1), Vec4(0.15, 0.65, 0.25, 1),
            Vec4(0.70, 0.55, 0.45, 1), Vec4(0.40, 0.25, 0.15, 1)
        ]
        for i, col in enumerate(colors):
            create_solid_cube_3d(desk_group, Vec3(-0.7 + (i * 0.2), 0.0, 1.12), Vec3(0.08, 0.7, 0.05), col, f"wire_pin_{i}")
    elif station_num == "5":
        create_solid_cube_3d(desk_group, Vec3(-0.4, -0.1, 1.14), Vec3(0.9, 0.1, 0.08), Vec4(0.1, 0.4, 0.7, 1), "cable_in_plug")
        create_solid_cube_3d(desk_group, Vec3(0.1, -0.1, 1.16), Vec3(0.2, 0.15, 0.12), Vec4(0.75, 0.78, 0.82, 1), "rj45_head")
        create_solid_cube_3d(desk_group, Vec3(0.8, -0.1, 1.20), Vec3(0.2, 0.6, 0.25), Vec4(0.7, 0.2, 0.2, 1), "crimper_heavy")
    elif station_num == "6":
        create_solid_cube_3d(desk_group, Vec3(0, 0.68, 2.0), Vec3(0.9, 0.12, 1.3), Vec4(0.65, 0.68, 0.72, 1), "big_tester")
        for i in range(8):
            create_solid_cube_3d(desk_group, Vec3(-0.2, 0.61, 2.4 - (i * 0.12)), Vec3(0.1, 0.02, 0.08), Vec4(0.1, 0.7, 0.3, 1), f"led_{i}")
    elif station_num == "7":
        create_solid_cube_3d(desk_group, Vec3(-0.9, 0.2, 1.52), Vec3(1.0, 0.1, 0.7), Vec4(0.12, 0.22, 0.35, 1), "pc_screen")
        create_solid_cube_3d(desk_group, Vec3(0.0, 0.1, 1.22), Vec3(0.9, 0.5, 0.25), Vec4(0.1, 0.35, 0.65, 1), "net_switch")
        create_solid_cube_3d(desk_group, Vec3(0.95, 0.1, 1.22), Vec3(0.7, 0.45, 0.2), Vec4(0.2, 0.22, 0.25, 1), "net_router")
    elif station_num == "8":
        for idx, offset in enumerate([-0.95, 0, 0.95]):
            create_solid_cube_3d(desk_group, Vec3(offset, 0.4, 1.62), Vec3(0.85, 0.05, 0.65), Vec4(0.1, 0.2, 0.32, 1), f"status_screen_{idx}")
    elif station_num == "9":
        for i in range(3):
            create_solid_cube_3d(desk_group, Vec3(-0.4 + (i * 0.4), 0, 1.32), Vec3(0.25, 0.1, 0.25), Vec4(0.8, 0.65, 0.1, 1), f"star_{i}")

    return desk_group


def build_room(base_app, difficulty="easy", parent=None):
    room_node = (parent or base_app.render).attachNewNode("VirtualLabRoom3D")
    font = base_app.thai_font

    if hasattr(base_app, "camLens"):
        base_app.camLens.setNear(0.5)
        base_app.camLens.setFar(150.0)

    is_hard = (difficulty == "hard")

    if difficulty == "easy":
        floor_color = Vec4(0.25, 0.35, 0.45, 1)
        wall_color = Vec4(0.40, 0.50, 0.60, 1)
        desk_edge_color = Vec4(0.18, 0.48, 0.75, 1)
    elif difficulty == "medium":
        floor_color = Vec4(0.42, 0.38, 0.32, 1)
        wall_color = Vec4(0.55, 0.50, 0.45, 1)
        desk_edge_color = Vec4(0.75, 0.5, 0.1, 1)
    else:
        floor_color = Vec4(0.15, 0.15, 0.17, 1)
        wall_color = Vec4(0.22, 0.20, 0.22, 1)
        desk_edge_color = Vec4(0.7, 0.2, 0.2, 1)

    alight = AmbientLight("amb_light")
    alight.setColor(Vec4(0.25, 0.25, 0.25, 1) if is_hard else Vec4(0.65, 0.68, 0.72, 1))
    dlight = DirectionalLight("dir_light")
    dlight.setColor(Vec4(0.25, 0.25, 0.25, 1) if is_hard else Vec4(0.5, 0.5, 0.5, 1))
    dlnp = room_node.attachNewNode(dlight)
    dlnp.setHpr(-35, -50, 0)
    room_node.setLight(room_node.attachNewNode(alight))
    room_node.setLight(dlnp)

    create_solid_cube_3d(room_node, pos=Vec3(0, 0, -0.2), scale=Vec3(40, 34, 0.4), color=floor_color, name="floor")
    create_solid_cube_3d(room_node, pos=Vec3(0, 16.5, 4.5), scale=Vec3(40, 0.4, 9.0), color=wall_color, name="wall_back")
    create_solid_cube_3d(room_node, pos=Vec3(-19.8, 0, 4.5), scale=Vec3(0.4, 33, 9.0), color=wall_color, name="wall_left")
    create_solid_cube_3d(room_node, pos=Vec3(19.8, 0, 4.5), scale=Vec3(0.4, 33, 9.0), color=wall_color, name="wall_right")

    # ตำแหน่งโต๊ะปกติสำหรับโหมด Easy และ Medium
    default_positions = [
        (-13, 12), (-6.5, 12), (0.0, 12), (6.5, 12), (13, 12),
        (10, 0), (0, 0), (-10, 0), (0, -10)
    ]

    # ตำแหน่งกระจัดกระจายทั่วห้องสำหรับโหมด Hard
    hard_positions = [
        (13, -10), (-13, 0), (6.5, 12), (-6.5, -8), (0.0, 12),
        (-13, 12), (10, 5), (0, -2), (13, 8)
    ]

    used_positions = hard_positions if is_hard else default_positions

    # อัปเดตพิกัดโต๊ะไปยัง PlayerController ให้เช็คระยะตรวจจับถูกตำแหน่ง
    if hasattr(base_app, 'player') and base_app.player:
        for idx in range(1, 10):
            x, y = used_positions[idx - 1]
            base_app.player.stations_pos[idx] = Vec3(x, y, 0)

    stations_info = [
        ("1", "เริ่มภารกิจ", "ลงชื่อเข้าเรียน"),
        ("2", "เลือกอุปกรณ์", "สาย UTP/หัว RJ45/คีม/Tester"),
        ("3", "เตรียมสาย UTP", "ปอกเปลือกและคลายเกลียว"),
        ("4", "เรียงสีสาย LAN", "จัดสายตามมาตรฐาน T568B/T568A"),
        ("5", "ตัดและเข้าหัว", "ตัด / เสียบหัว / ย้ำหัว"),
        ("6", "ทดสอบสาย", "เช็คสัญญาณ LED 1-8"),
        ("7", "ต่อเครือข่าย", "PC -> Switch -> Router"),
        ("8", "ตั้งค่า Network", "IP Config & Ping Test"),
        ("9", "สรุปคะแนน", "คำนวณดาวและประเมินผล")
    ]

    for idx, (num, title, desc) in enumerate(stations_info):
        x, y = used_positions[idx]
        create_station_desk(room_node, pos=Vec3(x, y, 0), desk_color=desk_edge_color, station_num=num)
        create_station_signboard_3d(
            room_node, pos=Vec3(x, y + 0.75, 2.9), number_str=num,
            title_str=title, sub_desc=desc, font=font, hide_hints=is_hard
        )

    # เฉพาะระดับง่ายเท่านั้นที่มีเส้นนำทาง
    if difficulty == "easy":
        path_points = [
            (-13, 8), (-6.5, 8), (0, 8), (6.5, 8), (13, 8),
            (13, 0), (10, 0), (0, 0), (-10, 0), (-10, -6), (0, -6)
        ]
        for i in range(len(path_points) - 1):
            x1, y1 = path_points[i]
            x2, y2 = path_points[i + 1]
            cx, cy = (x1 + x2) / 2, (y1 + y2) / 2
            sx = max(abs(x2 - x1) + 0.4, 0.4)
            sy = max(abs(y2 - y1) + 0.4, 0.4)
            create_solid_cube_3d(
                room_node, pos=Vec3(cx, cy, 0.03), scale=Vec3(sx, sy, 0.05), color=Vec4(0.0, 0.85, 1.0, 1), name=f"path_{i}"
            )

    return room_node
