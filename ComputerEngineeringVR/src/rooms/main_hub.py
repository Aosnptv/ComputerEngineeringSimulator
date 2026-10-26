
import math

from direct.gui.DirectGui import DirectButton, DirectFrame, DirectLabel
from direct.task import Task
from panda3d.core import AmbientLight, AntialiasAttrib, ClockObject, DirectionalLight, Point3, TextNode, TransparencyAttrib

from content import STATIONS, TEXT, station_text

class MainHub:
    def __init__(self, app, font=None, parent=None):
        self.app = app
        self.font = font
        self.parent = parent or app.render
        self.root = self.parent.attachNewNode("main_hub")
        self.ui = []
        self.keys = {}
        self.active = False
        self.yaw = 0.0
        self.pitch = -7.0
        self.mouse_look = False
        self.last_mouse = None
        self.language = "en"
        self.nearby = None
        self.interaction_ready_at = 0.0

    def box(self, name, pos, scale, color, parent=None):
        model = self.app.loader.loadModel("models/box")
        model.reparentTo(parent or self.root)
        model.setName(name)
        # The built-in box runs from 0 to 1 on each axis, not -1 to 1.
        model.setPos(*(pos[i] - scale[i] for i in range(3)))
        model.setScale(*(2 * value for value in scale))
        model.setTextureOff(1)
        model.setColor(*color)
        return model

    def sphere(self, name, pos, scale, color, parent=None):
        model = self.app.loader.loadModel("models/misc/sphere")
        model.reparentTo(parent or self.root)
        model.setName(name)
        model.setPos(*pos)
        model.setScale(*scale)
        model.setTextureOff(1)
        model.setColor(*color)
        return model

    def build_lighting(self):
        self.root.setAntialias(AntialiasAttrib.MAuto)
        # Panda3D render states retain references to light NodePaths.  Creating
        # new lights on every Hub visit therefore grows native driver handles
        # on the Intel/WGL renderer even after the scene root is removed.
        # These immutable lights belong to the application renderer and are
        # intentionally shared by every short-lived MainHub instance.
        lights = getattr(self.app, "_main_hub_shared_lights", None)
        if lights is None:
            owner = self.app.render.attachNewNode("shared:main_hub_lights")
            ambient = AmbientLight("soft_ambient")
            ambient.setColor((0.42, 0.51, 0.64, 1))
            ambient_node = owner.attachNewNode(ambient)

            sun = DirectionalLight("lab_key_light")
            sun.setColor((0.48, 0.56, 0.67, 1))
            sun_node = owner.attachNewNode(sun)
            sun_node.setHpr(-35, -55, 0)
            lights = (ambient_node, sun_node)
            self.app._main_hub_shared_lights = lights

        for light in lights:
            self.root.setLight(light)

    def build_environment(self):
        self.box("Floor", (0, 0, -0.2),
                 (10, 10, 0.2), (0.13, 0.2, 0.31, 1))
        self.box("Walkway", (0, 0, 0.006),
                 (2.75, 9.5, 0.006), (0.18, 0.28, 0.4, 1))
        self.box("Ceiling", (0, 0, 6),
                 (10, 10, 0.2), (0.065, 0.105, 0.18, 1))

        for x in (-10, 10):
            self.box("Side Wall", (x, 0, 3),
                     (0.2, 10, 3), (0.12, 0.2, 0.32, 1))
            self.box("Wall Skirt", (x + (0.22 if x < 0 else -0.22), 0, 0.32),
                     (0.035, 9.7, 0.32), (0.05, 0.11, 0.2, 1))
            rail = self.box("Wall Light Rail",
                            (x + (0.25 if x < 0 else -0.25), 0, 4.55),
                            (0.025, 9.5, 0.045), (0.08, 0.72, 0.9, 1))
            rail.setLightOff()

        self.box("Front Wall", (0, -10, 3),
                 (10, 0.2, 3), (0.1, 0.18, 0.29, 1))

        # Frosted rear glazing frames the exterior without a bright flat wall.
        glass = self.box("Rear Glass", (0, 10, 3),
                         (10, 0.05, 3), (0.18, 0.56, 0.7, 0.24))
        glass.setTransparency(TransparencyAttrib.MAlpha)
        for x in (-9, -4.5, 0, 4.5, 9):
            self.box("Window Mullion", (x, 9.9, 3),
                     (0.07, 0.1, 3), (0.055, 0.14, 0.24, 1))
        for z in (0.15, 5.65):
            self.box("Window Beam", (0, 9.85, z),
                     (9.9, 0.11, 0.09), (0.055, 0.14, 0.24, 1))

        self.box("Campus Building", (0, 23, 5),
                 (7, 1.5, 5), (0.15, 0.24, 0.37, 1))
        for x in (-5, -2.5, 0, 2.5, 5):
            for z in (2, 4, 6, 8):
                window = self.box("Campus Window", (x, 21.4, z),
                                  (0.58, 0.04, 0.48),
                                  (0.12, 0.52, 0.72, 1))
                window.setLightOff()
        self.box("Campus Tower", (0, 23, 11),
                 (1.05, 1, 2), (0.18, 0.29, 0.43, 1))

        for x in (-4.5, 0, 4.5):
            self.box("Floor Inlay", (x, 0, 0.018),
                     (0.018, 9.4, 0.008), (0.11, 0.39, 0.5, 1))
        for y in (-7, -3.5, 0, 3.5, 7):
            self.box("Floor Inlay", (0, y, 0.018),
                     (9.4, 0.018, 0.008), (0.11, 0.39, 0.5, 1))
        for x in (-6, 0, 6):
            for y in (-5, 1, 7):
                light = self.box("Ceiling Panel", (x, y, 5.76),
                                 (1.45, 0.48, 0.015),
                                 (0.5, 0.88, 0.98, 1))
                light.setLightOff()

        # Central information console with a few readable screen details.
        self.box("Console Plinth", (0, 3.5, 0.48),
                 (1.75, 0.7, 0.48), (0.055, 0.12, 0.22, 1))
        self.box("Console Front Panel", (0, 2.785, 0.55),
                 (1.48, 0.02, 0.29), (0.11, 0.22, 0.34, 1))
        for x in (-0.74, 0, 0.74):
            indicator = self.box("Console Status", (x, 2.757, 0.55),
                                 (0.28, 0.012, 0.025),
                                 (0.08, 0.74, 0.85, 1))
            indicator.setLightOff()
        self.box("Console Top", (0, 3.5, 1.03),
                 (2.05, 0.9, 0.09), (0.2, 0.34, 0.48, 1))
        trim = self.box("Console Edge", (0, 2.57, 1.04),
                        (1.98, 0.025, 0.035), (0.07, 0.83, 0.95, 1))
        trim.setLightOff()
        self.box("Display Stand", (0, 3.72, 1.42),
                 (0.13, 0.13, 0.32), (0.08, 0.15, 0.25, 1))
        self.box("Display Frame", (0, 3.73, 2.04),
                 (1.04, 0.1, 0.56), (0.035, 0.09, 0.16, 1))
        screen = self.box("Display Screen", (0, 3.61, 2.04),
                          (0.93, 0.012, 0.46), (0.05, 0.22, 0.33, 1))
        screen.setLightOff()
        for z, width in ((2.39, 0.66), (1.70, 0.66)):
            bar = self.box("Display Accent", (0, 3.59, z),
                           (width, 0.008, 0.016),
                           (0.1, 0.82, 0.92, 1))
            bar.setLightOff()
        for value, z, size in (
            ("คลิกจอคอม" if self.language == "th" else "CLICK SCREEN", 2.15, 0.19),
            ("เลือกห้อง 1 - 3" if self.language == "th" else "CHOOSE ROOM 1 - 3", 1.91, 0.16),
        ):
            message = TextNode("computer_room_hint")
            message.setText(value)
            message.setAlign(TextNode.ACenter)
            message.setTextColor(0.56, 0.95, 1, 1)
            if self.font is not None:
                message.setFont(self.font)
            text_node = self.root.attachNewNode(message)
            text_node.setPos(0, 3.578, z)
            text_node.setScale(size)
            text_node.setLightOff()

    def build_stations(self):
        for index, station in enumerate(STATIONS, start=1):
            x, y = station["pos"]
            color = station["color"]
            stand = self.root.attachNewNode("station_" + station["id"])
            self.box("Station Base", (x, y, 0.13),
                     (1.03, 0.92, 0.13), (0.04, 0.09, 0.17, 1), stand)
            base_light = self.box("Station Base Light", (x, y, 0.28),
                                  (0.9, 0.79, 0.018), color, stand)
            base_light.setLightOff()
            self.box("Station Body", (x, y, 1.28),
                     (0.7, 0.66, 0.95), (0.1, 0.18, 0.29, 1), stand)
            self.box("Station Crown", (x, y, 2.28),
                     (0.78, 0.75, 0.08), (0.04, 0.1, 0.18, 1), stand)
            side = 1 if x < 0 else -1
            front_x = x + side * 0.72
            face_x = x + side * 0.76
            self.box("Station Display", (front_x, y, 1.44),
                     (0.025, 0.52, 0.65), (0.025, 0.09, 0.16, 1), stand)
            accent = self.box("Station Accent", (face_x, y, 1.86),
                              (0.012, 0.38, 0.045), color, stand)
            accent.setLightOff()
            for bar in range(index % 3 + 2):
                signal = self.box("Station Signal",
                                   (face_x, y - 0.28 + bar * 0.18, 1.31),
                                   (0.012, 0.065, 0.06), color, stand)
                signal.setLightOff()

    def build_robot(self):
        parent = self.root.attachNewNode("robot_guide")
        parent.setPos(-2.75, 0.9, 0)
        parent.setScale(0.8)
        self.robot = parent

        self.sphere("Robot Shadow", (-2.75, 0.9, 0.028),
                    (0.75, 0.55, 0.025), (0.035, 0.07, 0.13, 1))

        self.sphere("Robot Body", (0, 0, 0.85),
                    (0.65, 0.45, 0.75), (0.55, 0.77, 0.88, 1), parent)
        self.box("Robot Chest", (0, -0.445, 0.96),
                 (0.23, 0.028, 0.17), (0.035, 0.13, 0.24, 1), parent)
        chest_light = self.box("Robot Chest Light", (0, -0.477, 0.96),
                               (0.14, 0.012, 0.034),
                               (0.08, 0.86, 0.96, 1), parent)
        chest_light.setLightOff()

        self.sphere("Robot Head", (0, -0.08, 1.85),
                    (0.78, 0.55, 0.57), (0.7, 0.86, 0.95, 1), parent)

        self.box("Face Screen", (0, -0.60, 1.88),
                 (0.56, 0.06, 0.32), (0.03, 0.13, 0.24, 1), parent)

        for x in [-0.25, 0.25]:
            eye = self.sphere("Eye", (x, -0.68, 1.95),
                              (0.09, 0.04, 0.13), (0.1, 0.90, 1, 1), parent)
            eye.setLightOff()

        for x in [-0.82, 0.82]:
            self.sphere("Arm", (x, 0, 0.95),
                        (0.25, 0.23, 0.4), (0.48, 0.72, 0.84, 1), parent)

        for x in [-0.36, 0.36]:
            self.box("Foot", (x, -0.12, 0.20),
                     (0.28, 0.38, 0.18), (0.11, 0.4, 0.67, 1), parent)

        self.box("Antenna Stem", (0, 0, 2.39),
                 (0.04, 0.04, 0.18), (0.3, 0.6, 0.86, 1), parent)
        antenna = self.sphere("Antenna", (0, 0, 2.54),
                              (0.12, 0.12, 0.12), (0.1, 0.9, 1, 1), parent)
        antenna.setLightOff()

    def create_ui(self):
        def rectangle(parent, pos, bounds, color):
            return DirectFrame(parent=parent, pos=pos,
                               frameSize=bounds, frameColor=color)

        def caption(parent, value, pos, size, color):
            return DirectLabel(parent=parent, text=value, text_font=self.font,
                               pos=pos, scale=size, text_fg=color,
                               frameColor=(0, 0, 0, 0))

        cyan = (0.07, 0.79, 1, 1)
        pale = (0.91, 0.97, 1, 1)
        muted = (0.48, 0.78, 0.9, 1)
        navy = (0.014, 0.045, 0.105, 0.96)

        reset_button = DirectButton(
            parent=self.app.a2dTopLeft,
            text="NEW SESSION" if self.language == "en" else "เริ่มรอบใหม่",
            text_font=self.font,
            text_fg=(0.91, 0.97, 1, 1),
            scale=0.042,
            pos=(0.25, 0, -0.12),
            frameSize=(-2.6, 2.6, -0.55, 0.65),
            frameColor=(0.06, 0.43, 0.60, 0.94),
            command=self.app.reset_session,
        )
        self.ui.append(reset_button)

        # Floating sign, with a luminous edge and a separate CPE mark.
        title = rectangle(self.app.a2dTopCenter, (0, 0, -0.13),
                          (-0.94, 0.94, -0.105, 0.105),
                          (0.03, 0.38, 0.58, 0.92))
        self.ui.append(title)
        rectangle(title, (0, 0, 0), (-0.925, 0.925, -0.095, 0.095), navy)
        rectangle(title, (0, 0, 0.099), (-0.83, -0.68, -0.005, 0.005), cyan)
        rectangle(title, (0, 0, 0.099), (0.64, 0.79, -0.005, 0.005), cyan)
        rectangle(title, (0, 0, -0.099), (-0.87, -0.46, -0.004, 0.004), cyan)
        rectangle(title, (0, 0, -0.099), (0.45, 0.87, -0.004, 0.004), cyan)
        rectangle(title, (-0.83, 0, 0.0), (-0.032, 0.032, -0.032, 0.032), cyan)
        rectangle(title, (-0.83, 0, 0.0), (-0.026, 0.026, -0.026, 0.026), navy)
        rectangle(title, (-0.83, 0, 0.0), (-0.012, 0.012, -0.012, 0.012), cyan)
        caption(title, "CPE", (-0.59, 0, -0.029), 0.078,
                (0.39, 0.93, 1, 1))
        rectangle(title, (-0.38, 0, 0), (-0.002, 0.002, -0.063, 0.063),
                  (0.1, 0.57, 0.76, 1))
        caption(title, TEXT[self.language]["title"],
                (0.25, 0, -0.006), 0.052 if self.language == "th" else 0.048,
                pale)
        caption(title, "COMPUTER ENGINEERING CLASSROOM",
                (0.25, 0, -0.065), 0.023, muted)

        # Six neon cards in the right navigation panel.
        panel = rectangle(self.app.a2dRightCenter, (-0.42, 0, 0),
                          (-0.41, 0.41, -0.44, 0.82),
                          (0.04, 0.4, 0.62, 0.96))
        self.ui.append(panel)
        rectangle(panel, (0, 0, 0), (-0.403, 0.403, -0.433, 0.812), navy)
        rectangle(panel, (0, 0, 0.72), (-0.38, 0.38, -0.002, 0.002), cyan)
        cap = rectangle(panel, (-0.31, 0, 0.65),
                        (-0.024, 0.024, -0.024, 0.024),
                        (0.36, 0.75, 1, 1))
        cap.setR(45)
        rectangle(panel, (-0.31, 0, 0.614),
                  (-0.028, 0.028, -0.006, 0.006),
                  (0.36, 0.75, 1, 1))
        caption(panel, TEXT[self.language]["stations"],
                (0.045, 0, 0.655), 0.055, pale)
        caption(panel, "6 TOPICS  /  SELECT TO LEARN" if self.language == "en"
                else "6 หัวข้อ  /  เลือกเพื่อเรียนรู้",
                (0.045, 0, 0.575), 0.027, muted)

        self.station_card_borders = []
        self.station_card_fills = []
        icon_text = ("CPU", "</>", "NET", "DB", "SEC", "AI")
        for i, station in enumerate(STATIONS):
            z = 0.405 - i * 0.145
            accent = station["color"]
            border = rectangle(panel, (0, 0, z),
                               (-0.383, 0.383, -0.056, 0.056),
                               (accent[0] * 0.55, accent[1] * 0.55,
                                accent[2] * 0.55, 1))
            fill = rectangle(panel, (0, 0, z),
                             (-0.378, 0.378, -0.051, 0.051),
                             (0.065, 0.14, 0.255, 1))
            self.station_card_borders.append(border)
            self.station_card_fills.append(fill)
            rectangle(panel, (-0.368, 0, z),
                      (-0.009, 0.009, -0.049, 0.049), accent)
            caption(panel, f"{i + 1:02}", (-0.316, 0, z - 0.012),
                    0.034, accent)
            caption(panel, icon_text[i], (-0.205, 0, z - 0.012),
                    0.032, accent)
            caption(panel, station_text(station, self.language)[0],
                    (0.065, 0, z - 0.011),
                    0.039 if self.language == "en" else 0.036, pale)
            caption(panel, ">", (0.336, 0, z - 0.015), 0.046, accent)
            DirectButton(parent=panel, text="", scale=0.05,
                         pos=(0, 0, z), frameSize=(-7.6, 7.6, -1.1, 1.1),
                         frameColor=(0, 0, 0, 0), relief=0,
                         command=self.open_station, extraArgs=[station])

        # Compact guide panel keeps controls visible without covering the room.
        guide_panel = rectangle(self.app.a2dBottomCenter, (-0.27, 0, 0.17),
                                (-0.78, 0.78, -0.15, 0.15),
                                (0.035, 0.36, 0.55, 0.94))
        self.ui.append(guide_panel)
        rectangle(guide_panel, (0, 0, 0),
                  (-0.768, 0.768, -0.14, 0.14), navy)
        rectangle(guide_panel, (-0.745, 0, 0),
                  (-0.008, 0.008, -0.13, 0.13), cyan)
        caption(guide_panel,
                "GUIDE BOT" if self.language == "en" else "หุ่นยนต์ไกด์",
                (-0.56, 0, 0.086), 0.031, cyan)
        self.guide_label = DirectLabel(
            parent=guide_panel, text=TEXT[self.language]["welcome"],
            text_font=self.font, text_wordwrap=37,
            scale=0.041 if self.language == "en" else 0.038,
            pos=(0, 0, 0.015), text_fg=pale,
            frameColor=(0, 0, 0, 0))
        self.prompt_label = caption(guide_panel,
                                    TEXT[self.language]["help"],
                                    (0, 0, -0.105), 0.031, muted)

    def highlight_station(self, station):
        for index, candidate in enumerate(STATIONS):
            accent = candidate["color"]
            selected = candidate["id"] == station["id"]
            self.station_card_borders[index]["frameColor"] = (
                accent if selected else
                (accent[0] * 0.55, accent[1] * 0.55,
                 accent[2] * 0.55, 1))
            self.station_card_fills[index]["frameColor"] = (
                (accent[0] * 0.15 + 0.07,
                 accent[1] * 0.15 + 0.14,
                 accent[2] * 0.15 + 0.25, 1)
                if selected else (0.065, 0.14, 0.255, 1))

    def open_station(self, station):
        name, description = station_text(station, self.language)
        self.guide_label["text"] = f"{name}: {description}"
        self.highlight_station(station)

    def open_minigames(self):
        self.app.show_minigame_menu(self.language)

    def computer_screen_hit(self, mouse):
        """Return whether a camera ray through the cursor meets the monitor face."""
        near = Point3()
        far = Point3()
        if not self.app.camLens.extrude(mouse, near, far):
            return False
        start = self.app.render.getRelativePoint(self.app.cam, near)
        end = self.app.render.getRelativePoint(self.app.cam, far)
        dy = end.y - start.y
        if dy <= 0 or self.app.camera.getY() >= 3.59:
            return False
        amount = (3.59 - start.y) / dy
        if not 0 <= amount <= 1:
            return False
        x = start.x + amount * (end.x - start.x)
        z = start.z + amount * (end.z - start.z)
        return -1.04 <= x <= 1.04 and 1.48 <= z <= 2.60

    def click_computer(self):
        if (not self.active or self.mouse_look or
                hasattr(self.app, "minigame_menu") or
                ClockObject.getGlobalClock().getFrameTime() < self.interaction_ready_at):
            return
        watcher = self.app.mouseWatcherNode
        if watcher is not None and watcher.hasMouse() and self.computer_screen_hit(watcher.getMouse()):
            self.open_minigames()

    def interact(self):
        if (not self.active or hasattr(self.app, "minigame_menu") or
                self.nearby is None or
                ClockObject.getGlobalClock().getFrameTime() < self.interaction_ready_at):
            return
        if self.nearby == "robot":
            self.guide_label["text"] = TEXT[self.language]["robot_message"]
        elif self.nearby == "computer":
            self.open_minigames()
        else:
            self.open_station(self.nearby)

    def update_nearby(self):
        camera = self.app.camera.getPos()
        closest = None
        closest_distance = 2.3
        for station in STATIONS:
            x, y = station["pos"]
            distance = math.hypot(camera.x - x, camera.y - y)
            if distance < closest_distance:
                closest, closest_distance = station, distance
        if math.hypot(camera.x + 2.75, camera.y - 0.9) < closest_distance:
            closest = "robot"
        if math.hypot(camera.x, camera.y - 3.5) < 2.8:
            closest = "computer"
        if closest is self.nearby:
            return
        self.nearby = closest
        if closest == "robot":
            self.prompt_label["text"] = TEXT[self.language]["robot"]
        elif closest == "computer":
            self.prompt_label["text"] = TEXT[self.language]["computer_near"]
        elif closest is not None:
            self.prompt_label["text"] = TEXT[self.language]["near"].format(
                name=station_text(closest, self.language)[0]
            )
        else:
            self.prompt_label["text"] = TEXT[self.language]["help"]

    def key_event(self, name, value):
        self.keys[name] = value

    def set_mouse_look(self, enabled):
        self.mouse_look = enabled
        self.last_mouse = None

    def apply_mouse_delta(self, dx, dy):
        # Panda3D's positive heading points left, so moving right lowers H.
        self.yaw -= dx * 110
        self.pitch = max(-60, min(60, self.pitch + dy * 85))

    def update(self, task):
        if not self.active:
            return Task.cont
        if hasattr(self.app, "minigame_menu"):
            self.last_mouse = None
            return Task.cont

        dt = min(self.app.clock.getDt(), 0.05)
        speed = 5 * dt

        if self.keys.get("arrow_left"):
            self.yaw += 85 * dt
        if self.keys.get("arrow_right"):
            self.yaw -= 85 * dt

        watcher = self.app.mouseWatcherNode
        if self.mouse_look and watcher is not None and watcher.hasMouse():
            pointer = watcher.getMouse()
            current = (pointer.x, pointer.y)
            if self.last_mouse is not None:
                self.apply_mouse_delta(current[0] - self.last_mouse[0],
                                       current[1] - self.last_mouse[1])
            self.last_mouse = current
        else:
            self.last_mouse = None

        self.app.camera.setHpr(self.yaw, self.pitch, 0)

        angle = math.radians(self.yaw)
        forward = (-math.sin(angle), math.cos(angle))
        right = (math.cos(angle), math.sin(angle))

        dx, dy = 0, 0

        if self.keys.get("w"):
            dx += forward[0] * speed
            dy += forward[1] * speed
        if self.keys.get("s"):
            dx -= forward[0] * speed
            dy -= forward[1] * speed
        if self.keys.get("d"):
            dx += right[0] * speed
            dy += right[1] * speed
        if self.keys.get("a"):
            dx -= right[0] * speed
            dy -= right[1] * speed

        pos = self.app.camera.getPos()
        self.app.camera.setPos(
            max(-8.5, min(8.5, pos.x + dx)),
            max(-8.5, min(8.5, pos.y + dy)),
            2.2
        )

        self.robot.setZ(0.035 * math.sin(task.time * 2.5))
        self.update_nearby()

        return Task.cont

    def pause(self):
        self.active = False
        self.set_mouse_look(False)
        self.keys.clear()

    def resume(self):
        self.active = True
        self.last_mouse = None
        self.interaction_ready_at = ClockObject.getGlobalClock().getFrameTime() + 0.35

    def enter(self, language="en"):
        if self.active:
            return

        self.active = True
        self.interaction_ready_at = ClockObject.getGlobalClock().getFrameTime() + 0.35
        self.language = language if language in TEXT else "en"
        self.yaw = 0.0
        self.pitch = -7.0
        self.set_mouse_look(False)
        self.keys.clear()
        self.root.show()

        self.build_lighting()
        self.build_environment()
        self.build_stations()
        self.build_robot()
        self.create_ui()

        self.app.camera.setPos(0, -8, 2.2)
        self.app.camera.setHpr(0, -7, 0)
        self.update_nearby()

        for key in ["w", "a", "s", "d", "arrow_left", "arrow_right"]:
            self.app.accept(
                key, self.key_event, [key, True]
            )
            self.app.accept(
                key + "-up", self.key_event, [key, False]
            )
        self.app.accept("e", self.interact)
        self.app.accept("mouse1-up", self.click_computer)
        self.app.accept("mouse3", self.set_mouse_look, [True])
        self.app.accept("mouse3-up", self.set_mouse_look, [False])

        self.app.taskMgr.add(self.update, "main_hub_update")

    def exit(self):
        if not self.active:
            return
        self.active = False
        self.app.taskMgr.remove("main_hub_update")
        for widget in self.ui:
            widget.destroy()
        self.ui.clear()
        self.root.removeNode()
        self.root = self.parent.attachNewNode("main_hub")
        for key in ["w", "a", "s", "d", "arrow_left", "arrow_right"]:
            self.app.ignore(key)
            self.app.ignore(key + "-up")
        self.app.ignore("e")
        self.app.ignore("mouse1-up")
        self.app.ignore("mouse3")
        self.app.ignore("mouse3-up")
        self.set_mouse_look(False)
        self.keys.clear()

    def destroy(self):
        self.exit()
        if not self.root.isEmpty():
            self.root.removeNode()
