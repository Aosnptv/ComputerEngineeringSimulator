"""
Programming Room
Main Hub - 3D Room Selection

Controls:
    WASD          Walk
    Right Mouse   Look around
    E             Enter selected room
    Q             Quit (only in Main Hub)
"""

import math

from panda3d.core import (
    NodePath,
    TextNode,
    ClockObject,
)

from direct.showbase.DirectObject import DirectObject
from direct.task import Task
from direct.gui.DirectGui import DirectLabel


ROOMS = [
    {
        "id": "programming",
        "name": "PROGRAMMING LAB",
        "x": -6.9,
        "color": (0.43, 0.79, 1.0, 1),
    },
    {
        "id": "networking",
        "name": "NETWORKING LAB",
        "x": -2.3,
        "color": (0.69, 0.64, 0.98, 1),
    },
    {
        "id": "hardware",
        "name": "HARDWARE LAB",
        "x": 2.3,
        "color": (0.55, 0.88, 0.68, 1),
    },
    {
        "id": "learning",
        "name": "LEARNING ROOM",
        "x": 6.9,
        "color": (1.0, 0.78, 0.52, 1),
    },
]


class MainHub:

    def __init__(self, app):

        self.app = app

        self.root = NodePath("MainHub")
        self.root.reparentTo(app.render)

        self.build_hub()
        self.hide()

    # ==========================================
    # BOX HELPER
    # ==========================================

    def box(self, name, pos, size, color):

        return self.app.room.box(
            name,
            pos,
            size,
            color,
            parent=self.root
        )

    # ==========================================
    # TEXT HELPER
    # ==========================================

    def text(self, value, x, y, z, scale, color):

        node = TextNode("HubText")

        node.setText(value)
        node.setAlign(TextNode.ACenter)
        node.setTextColor(*color)

        path = self.root.attachNewNode(node)

        path.setPos(x, y, z)
        path.setHpr(0, 0, 0)
        path.setTwoSided(True)
        path.setScale(scale)

        return path

    # ==========================================
    # BUILD HUB
    # ==========================================

    def build_hub(self):

        # Floor
        self.box(
            "HubFloor",
            (0, 0, -0.3),
            (10.0, 12.0, 0.3),
            (0.91, 0.95, 1.0, 1)
        )

        # Back wall
        self.box(
            "HubBackWall",
            (0, 11.5, 3.5),
            (10.0, 0.18, 3.8),
            (0.80, 0.88, 1.0, 1)
        )

        # Left wall
        self.box(
            "HubLeftWall",
            (-9.85, 0, 3.5),
            (0.15, 11.5, 3.8),
            (0.84, 0.89, 1.0, 1)
        )

        # Right wall
        self.box(
            "HubRightWall",
            (9.85, 0, 3.5),
            (0.15, 11.5, 3.8),
            (0.84, 0.89, 1.0, 1)
        )

        # Ceiling
        self.box(
            "HubCeiling",
            (0, 0, 7.20),
            (10.0, 11.5, 0.18),
            (0.90, 0.94, 1.0, 1)
        )

        # Floor pathway
        self.box(
            "HubWalkway",
            (0, 0, 0.018),
            (8.5, 9.5, 0.018),
            (0.83, 0.89, 1.0, 1)
        )

        # Welcome sign
        self.box(
            "WelcomePanel",
            (0, 11.17, 6.15),
            (4.5, 0.12, 0.52),
            (0.48, 0.69, 0.96, 1)
        )

        self.text(
            "WELCOME TO VR LEARNING CAMPUS",
            0,
            10.98,
            6.05,
            0.37,
            (1, 1, 1, 1)
        )

        # Doors
        for room in ROOMS:
            self.build_door(room)

        # Decorative ceiling lights
        for x in (-6, -2, 2, 6):
            self.box(
                "CeilingLight",
                (x, 0, 6.92),
                (0.85, 1.0, 0.08),
                (1.0, 0.97, 0.77, 1)
            )

        # Pastel wall panels
        for x in (-7.9, 7.9):
            self.box(
                "HubDecoration",
                (x, -5.2, 3.35),
                (0.48, 0.06, 0.85),
                (0.98, 0.78, 0.86, 1)
            )

    # ==========================================
    # BUILD DOOR
    # ==========================================

    def build_door(self, room):

        x = room["x"]
        y = 11.12

        # Door panel
        self.box(
            f"Door_{room['id']}",
            (x, y, 1.85),
            (1.45, 0.12, 1.85),
            room["color"]
        )

        # Door frame
        frame = (0.25, 0.43, 0.68, 1)

        for dx in (-1.58, 1.58):
            self.box(
                "DoorSideFrame",
                (x + dx, 10.99, 1.85),
                (0.12, 0.17, 1.95),
                frame
            )

        self.box(
            "DoorTopFrame",
            (x, 10.99, 3.86),
            (1.70, 0.17, 0.12),
            frame
        )

        # Colorful title sign
        self.box(
            "DoorTitlePanel",
            (x, 10.91, 4.48),
            (1.77, 0.10, 0.39),
            room["color"]
        )

        self.text(
            room["name"],
            x,
            10.76,
            4.35,
            0.24,
            (0.12, 0.23, 0.40, 1)
        )

        # Door handle
        self.box(
            "DoorHandle",
            (x + 1.04, 10.89, 1.78),
            (0.09, 0.06, 0.22),
            (1.0, 0.90, 0.52, 1)
        )

        # Interaction floor marker
        self.box(
            "DoorFloorMarker",
            (x, 8.75, 0.045),
            (1.15, 0.42, 0.035),
            room["color"]
        )

    # ==========================================
    # FIND NEAREST DOOR
    # ==========================================

    def nearby_room(self, x, y):

        for room in ROOMS:

            distance = math.hypot(
                x - room["x"],
                y - 8.75
            )

            if distance <= 2.05:
                return room

        return None

    def show(self):
        self.root.show()

    def hide(self):
        self.root.hide()


class HubController(DirectObject):

    MOVE_SPEED = 5.0
    TURN_SPEED = 95.0
    MOUSE_SENSITIVITY = 0.17
    CAMERA_HEIGHT = 1.72

    def __init__(self, app, hub):

        DirectObject.__init__(self)

        self.app = app
        self.hub = hub

        self.active = False
        self.mouse_look = False
        self.last_pointer = None

        # Initial position: facing the Programming Lab door
        self.position = [-6.9, -7.5]
        self.heading = 0.0
        self.pitch = -5.0

        self.keys = {
            key: False
            for key in (
                "w", "a", "s", "d",
                "arrow_left", "arrow_right"
            )
        }

        self.guide = DirectLabel(
            parent=app.aspect2d,
            text="MAIN HUB | WASD WALK | E ENTER ROOM",
            pos=(0, 0, 0.64),
            scale=0.045,
            frameColor=(0.86, 0.96, 1.0, 0.93),
            text_fg=(0.10, 0.25, 0.43, 1),
        )

        self.guide.hide()

        for key in self.keys:
            self.accept(
                key,
                self.set_key,
                [key, True]
            )

            self.accept(
                key + "-up",
                self.set_key,
                [key, False]
            )

        self.accept("mouse3", self.start_mouse_look)
        self.accept("mouse3-up", self.stop_mouse_look)
        self.accept("e", self.try_enter)
        self.accept("q", self.try_quit)

        app.taskMgr.add(
            self.update,
            "main_hub_walk"
        )

    # ==========================================
    # ENABLE / DISABLE
    # ==========================================

    def enable(self):
        self.active = True

        # Prevent the same E key event from reopening
        # Programming Room immediately after exiting.
        self.enter_ready_at = (
            ClockObject.getGlobalClock().getFrameTime() + 0.35
        )

        self.mouse_look = False
        self.last_pointer = None
        self.guide.show()
        self.move_camera()
        self.update_prompt()

    def disable(self):
        self.active = False
        self.mouse_look = False
        self.last_pointer = None
        self.guide.hide()

        for key in self.keys:
            self.keys[key] = False

    def set_key(self, key, down):
        self.keys[key] = (
            down if self.active else False
        )

    def start_mouse_look(self):
        if self.active:
            self.mouse_look = True
            self.last_pointer = None

    def stop_mouse_look(self):
        self.mouse_look = False
        self.last_pointer = None

    # ==========================================
    # CAMERA
    # ==========================================

    def move_camera(self):
        self.app.camera.setPos(
            self.position[0],
            self.position[1],
            self.CAMERA_HEIGHT
        )

        self.app.camera.setHpr(
            self.heading,
            self.pitch,
            0
        )

    # ==========================================
    # DOOR PROMPT
    # ==========================================

    def update_prompt(self):
        if not self.active:
            return

        room = self.hub.nearby_room(
            self.position[0],
            self.position[1]
        )

        if room:
            message = (
                f"{room['name']} | PRESS E TO ENTER"
            )
        else:
            message = (
                "MAIN HUB | WASD WALK | "
                "RIGHT MOUSE LOOK | FIND A DOOR"
            )

        self.guide["text"] = message
        self.app.status_label["text"] = message

    # ==========================================
    # ENTER ROOM
    # ==========================================

    def try_enter(self):
        if not self.active:
            return

        # Wait briefly after arriving at Main Hub.
        # This prevents re-entering from the exit key press.
        if (
            ClockObject.getGlobalClock().getFrameTime()
            < self.enter_ready_at
        ):
            return

        room = self.hub.nearby_room(
            self.position[0],
            self.position[1]
        )

        if room is None:
            return

        if room["id"] == "programming":
            self.app.enter_programming_room()
        else:
            self.app.show_locked_room(room["name"])

    def try_quit(self):
        if self.active:
            self.app.userExit()

    # ==========================================
    # UPDATE
    # ==========================================

    def update(self, task):
        if not self.active:
            return Task.cont

        dt = min(
            ClockObject.getGlobalClock().getDt(),
            0.06
        )

        self.heading += self.TURN_SPEED * dt * (
            int(self.keys["arrow_left"])
            - int(self.keys["arrow_right"])
        )

        if self.mouse_look and self.app.win is not None:
            pointer = self.app.win.getPointer(0)

            current = (
                pointer.getX(),
                pointer.getY()
            )

            if self.last_pointer is not None:
                dx = current[0] - self.last_pointer[0]
                dy = current[1] - self.last_pointer[1]

                self.heading -= (
                    dx * self.MOUSE_SENSITIVITY
                )

                self.pitch = max(
                    -55,
                    min(
                        55,
                        self.pitch
                        - dy * self.MOUSE_SENSITIVITY
                    )
                )

            self.last_pointer = current

        angle = math.radians(self.heading)

        forward = (
            math.sin(angle),
            math.cos(angle)
        )

        right = (
            math.cos(angle),
            -math.sin(angle)
        )

        fi = int(self.keys["w"]) - int(self.keys["s"])
        si = int(self.keys["d"]) - int(self.keys["a"])

        if fi or si:
            length = math.hypot(fi, si)

            dx = (
                forward[0] * fi
                + right[0] * si
            ) / length

            dy = (
                forward[1] * fi
                + right[1] * si
            ) / length

            nx = (
                self.position[0]
                + dx * self.MOVE_SPEED * dt
            )

            ny = (
                self.position[1]
                + dy * self.MOVE_SPEED * dt
            )

            # Keep player inside the hub
            if -9.3 <= nx <= 9.3:
                self.position[0] = nx

            if -10.8 <= ny <= 9.1:
                self.position[1] = ny

        self.move_camera()
        self.update_prompt()

        return Task.cont