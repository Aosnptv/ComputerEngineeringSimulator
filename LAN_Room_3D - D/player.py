# player.py
from panda3d.core import CardMaker, Vec3, Vec4


def create_cube_3d(parent, pos, scale, color):
    cube = parent.attachNewNode("cube_3d")
    cm = CardMaker("face")
    faces = [
        (Vec3(0, 0, 0.5), Vec3(0, 0, 0)),
        (Vec3(0, 0, -0.5), Vec3(0, 180, 0)),
        (Vec3(0, -0.5, 0), Vec3(0, 90, 0)),
        (Vec3(0, 0.5, 0), Vec3(0, -90, 0)),
        (Vec3(-0.5, 0, 0), Vec3(-90, 0, 0)),
        (Vec3(0.5, 0, 0), Vec3(90, 0, 0)),
    ]
    cm.setFrame(-0.5, 0.5, -0.5, 0.5)
    for face_pos, face_hpr in faces:
        face_node = cube.attachNewNode(cm.generate())
        face_node.setPos(face_pos)
        face_node.setHpr(face_hpr)
        face_node.setColor(color)
    cube.setPos(pos)
    cube.setScale(scale)
    return cube


class PlayerController:
    def __init__(self, base_app, parent=None, input_scope=None, ui=None):
        self.app = base_app
        self.ui = ui
        self.input_scope = input_scope
        self.enabled = True
        self.move_speed = 12.0
        self.mouse_sens = 0.25

        self.cam_distance = 14.0
        self.cam_height = 8.0
        self.cam_pitch = -25.0
        self.cam_heading = 0.0

        self.is_dragging = False
        self.last_mouse_x = 0
        self.last_mouse_y = 0

        self.stations_pos = {
            1: Vec3(-13, 12, 0),
            2: Vec3(-6.5, 12, 0),
            3: Vec3(0.0, 12, 0),
            4: Vec3(6.5, 12, 0),
            5: Vec3(13, 12, 0),
            6: Vec3(10, 0, 0),
            7: Vec3(0, 0, 0),
            8: Vec3(-10, 0, 0),
            9: Vec3(0, -10, 0)
        }
        self.nearby_station = None

        self.bot = (parent or self.app.render).attachNewNode("PlayerBot")
        self.bot.setPos(0, -8, 0)

        create_cube_3d(self.bot, pos=Vec3(0, 0, 0.9), scale=Vec3(0.6, 0.4, 0.8), color=Vec4(0.1, 0.45, 0.75, 1))
        create_cube_3d(self.bot, pos=Vec3(0, 0, 1.6), scale=Vec3(0.45, 0.45, 0.45), color=Vec4(0.9, 0.78, 0.68, 1))
        visor = create_cube_3d(self.bot, pos=Vec3(0, -0.22, 1.65), scale=Vec3(0.38, 0.1, 0.12), color=Vec4(0.9, 0.75, 0.0, 1))
        visor.setLightOff()
        create_cube_3d(self.bot, pos=Vec3(-0.18, 0, 0.25), scale=Vec3(0.18, 0.25, 0.5), color=Vec4(0.2, 0.25, 0.3, 1))
        create_cube_3d(self.bot, pos=Vec3(0.18, 0, 0.25), scale=Vec3(0.18, 0.25, 0.5), color=Vec4(0.2, 0.25, 0.3, 1))

        self.key_map = {"up": False, "down": False, "left": False, "right": False}

        for key, name in [("w", "up"), ("s", "down"), ("a", "left"), ("d", "right"),
                          ("arrow_up", "up"), ("arrow_down", "down"), ("arrow_left", "left"), ("arrow_right", "right")]:
            self._bind(key, self.set_key, [name, True])
            self._bind(f"{key}-up", self.set_key, [name, False])

        self._bind("mouse1", self.start_drag)
        self._bind("mouse1-up", self.stop_drag)
        self._bind("mouse3", self.start_drag)
        self._bind("mouse3-up", self.stop_drag)

        self._bind("wheel_up", self.zoom, [-2.0])
        self._bind("wheel_down", self.zoom, [2.0])

        self.task = self.app.taskMgr.add(self.update_controller, "lan_player_controller")

    def _bind(self, event, method, args=None):
        if self.input_scope is not None:
            self.input_scope.bind(event, method, args)
        else:
            self.app.accept(event, method, args or [])

    def set_key(self, key, state):
        self.key_map[key] = state if self.enabled else False

    def start_drag(self):
        self.is_dragging = True
        if self.app.mouseWatcherNode.hasMouse():
            self.last_mouse_x = self.app.mouseWatcherNode.getMouseX()
            self.last_mouse_y = self.app.mouseWatcherNode.getMouseY()

    def stop_drag(self):
        self.is_dragging = False

    def zoom(self, amount):
        self.cam_distance = max(3.0, min(35.0, self.cam_distance + amount))

    def check_nearby_stations(self):
        ui = self.ui or getattr(self.app, "ui", None)
        if ui is None:
            return

        if (ui.bg_frame and not ui.bg_frame.isHidden()) or \
           (ui.result_frame and not ui.result_frame.isHidden()):
            return

        bot_pos = self.bot.getPos()
        closest_st = None
        min_dist = 3.5

        for st_num, st_pos in self.stations_pos.items():
            dist = (bot_pos - st_pos).length()
            if dist < min_dist:
                min_dist = dist
                closest_st = st_num

        if closest_st and closest_st != self.nearby_station:
            self.nearby_station = closest_st
            if ui.logic.can_access_station(closest_st):
                ui.open_station_ui(closest_st)
            else:
                ui.close_station_ui()
        elif not closest_st and self.nearby_station is not None:
            self.nearby_station = None
            ui.close_station_ui()

    def update_controller(self, task):
        if not self.enabled:
            return task.cont
        dt = self.app.clock.getDt()

        move_vec = Vec3(0, 0, 0)
        if self.key_map["up"]: move_vec.setY(1)
        if self.key_map["down"]: move_vec.setY(-1)
        if self.key_map["left"]: move_vec.setX(-1)
        if self.key_map["right"]: move_vec.setX(1)

        if move_vec.length_squared() > 0:
            move_vec.normalize()
            target_h = self.cam_heading + (0 if move_vec.getY() > 0 else 180 if move_vec.getY() < 0 else 0)
            if move_vec.getX() > 0:
                target_h -= 90 if move_vec.getY() == 0 else 45 * (1 if move_vec.getY() > 0 else -1)
            elif move_vec.getX() < 0:
                target_h += 90 if move_vec.getY() == 0 else 45 * (1 if move_vec.getY() > 0 else -1)

            self.bot.setH(target_h)
            self.bot.setY(self.bot, -self.move_speed * dt)

        if self.is_dragging and self.app.mouseWatcherNode.hasMouse():
            mx = self.app.mouseWatcherNode.getMouseX()
            my = self.app.mouseWatcherNode.getMouseY()

            dx = (mx - self.last_mouse_x) * 100 * self.mouse_sens
            dy = (my - self.last_mouse_y) * 100 * self.mouse_sens

            self.cam_heading -= dx
            self.cam_pitch = max(-80.0, min(10.0, self.cam_pitch + dy))

            self.last_mouse_x = mx
            self.last_mouse_y = my

        bot_pos = self.bot.getPos()
        self.app.camera.setPos(
            bot_pos.getX(),
            bot_pos.getY() - self.cam_distance,
            bot_pos.getZ() + self.cam_height
        )
        self.app.camera.setHpr(self.cam_heading, self.cam_pitch, 0)

        self.check_nearby_stations()

        return task.cont

    def set_enabled(self, enabled):
        self.enabled = enabled
        self.is_dragging = False
        if not enabled:
            for key in self.key_map:
                self.key_map[key] = False

    def reset(self):
        self.bot.setPos(0, -8, 0)
        self.cam_heading = 0.0
        self.cam_pitch = -25.0
        self.nearby_station = None

    def destroy(self):
        self.set_enabled(False)
        if self.task is not None:
            self.task.remove()
            self.task = None
        if not self.bot.isEmpty():
            self.bot.removeNode()
