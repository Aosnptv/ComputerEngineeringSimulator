"""
Programming Room
Interactive First-Person Classroom Controller

Controls:
    W A S D      Walk
    Right Mouse  Look around
    Arrow Keys   Turn camera
    E            Interact
    Left Click   Click interaction button
"""

import math

from panda3d.core import ClockObject
from direct.task import Task

from direct.gui.DirectGui import (
    DirectLabel,
    DirectButton,
)

try:
    from ..core.exploration import PLAYER_START, can_walk, interaction_at
except ImportError:
    from core.exploration import PLAYER_START, can_walk, interaction_at


class ClassroomController:

    MOVE_SPEED = 4.0
    TURN_SPEED = 95.0

    MOUSE_SENSITIVITY = 0.17

    HEIGHT = 1.72

    def __init__(self, app, room):

        self.app = app
        self.room = room

        # ======================================
        # PLAYER STATE
        # ======================================

        self.active = False

        self.mouse_look = False
        self.last_pointer = None

        self.position = list(PLAYER_START)

        self.heading = 0.0
        self.pitch = -6.0

        self.keys = {
            key: False
            for key in (
                "w",
                "a",
                "s",
                "d",
                "arrow_left",
                "arrow_right",
            )
        }

        # ======================================
        # INSTRUCTION LABEL
        # ======================================

        self.guide = DirectLabel(
            parent=app.aspect2d,

            text="WASD WALK | FIND A COMPUTER",

            pos=(0, 0, 0.64),

            scale=0.043,

            frameColor=(
                0.86, 0.97, 1.0, 0.92
            ),

            text_fg=(
                0.08, 0.28, 0.46, 1
            ),
        )

        self.guide.hide()

        # ======================================
        # INTERACTION BUTTON
        # ======================================

        self.interact_button = DirectButton(
            parent=app.aspect2d,

            text="PRESS E  |  START PROGRAMMING",

            pos=(0, 0, -0.48),

            scale=0.075,

            frameSize=(
                -3.20,
                3.20,
                -0.50,
                0.50
            ),

            frameColor=(
                0.45, 0.88, 0.65, 1
            ),

            text_fg=(
                0.08, 0.27, 0.32, 1
            ),

            relief=1,

            command=self.try_interact,
        )

        self.interact_button.hide()

        # Always-available way back to the hub, even when door proximity
        # detection or first-person navigation is awkward.
        self.exit_button = DirectButton(
            parent=app.aspect2d,
            text="BACK TO MAIN HUB",
            pos=(1.02, 0, 0.76),
            scale=0.045,
            frameSize=(-3.3, 3.3, -0.55, 0.55),
            frameColor=(0.18, 0.58, 0.42, 0.94),
            text_fg=(1, 1, 1, 1),
            relief=1,
            command=self.exit_to_hub,
        )
        self.exit_button.hide()

        self.console_button = DirectButton(
            parent=app.aspect2d,
            text="OPEN PROGRAMMING CONSOLE",
            pos=(-1.00, 0, 0.76),
            scale=0.045,
            frameSize=(-3.6, 3.6, -0.55, 0.55),
            frameColor=(0.31, 0.55, 0.88, 0.94),
            text_fg=(1, 1, 1, 1),
            relief=1,
            command=app.open_computer_from_menu,
        )
        self.console_button.hide()

        # ======================================
        # KEYBOARD EVENTS
        # ======================================

        for key in self.keys:

            app.accept(
                key,
                self.set_key,
                [key, True]
            )

            app.accept(
                key + "-up",
                self.set_key,
                [key, False]
            )

        # ======================================
        # MOUSE EVENTS
        # ======================================

        app.accept(
            "mouse3",
            self.start_mouse_look
        )

        app.accept(
            "mouse3-up",
            self.stop_mouse_look
        )

        # ======================================
        # INTERACTION KEY
        # ======================================

        app.accept(
            "e",
            self.try_interact
        )

        # ======================================
        # PLAYER UPDATE TASK
        # ======================================

        app.taskMgr.add(
            self.update,
            "classroom_walk"
        )

    # ======================================================
    # ENABLE CLASSROOM
    # ======================================================

    def enable(self):

        self.active = True

        self.guide.show()
        self.exit_button.show()
        self.console_button.show()

        self.stop_mouse_look()

        self.move_camera()

        self.update_prompt()

    # ======================================================
    # DISABLE CLASSROOM
    # ======================================================

    def disable(self):

        self.active = False

        self.guide.hide()
        self.exit_button.hide()
        self.console_button.hide()
        self.interact_button.hide()

        self.stop_mouse_look()

        for key in self.keys:
            self.keys[key] = False

    # ======================================================
    # MOVEMENT INPUT
    # ======================================================

    def set_key(self, key, down):

        self.keys[key] = (
            down if self.active else False
        )

    # ======================================================
    # START MOUSE LOOK
    # ======================================================

    def start_mouse_look(self):

        if not self.active:
            return

        self.mouse_look = True
        self.last_pointer = None

    # ======================================================
    # STOP MOUSE LOOK
    # ======================================================

    def stop_mouse_look(self):

        self.mouse_look = False
        self.last_pointer = None

    # ======================================================
    # CAMERA POSITION
    # ======================================================

    def move_camera(self):

        self.app.camera.setPos(
            self.position[0],
            self.position[1],
            self.HEIGHT
        )

        self.app.camera.setHpr(
            self.heading,
            self.pitch,
            0
        )

    # ======================================================
    # UPDATE INTERACTION BUTTON
    # ======================================================

    def update_prompt(self):

        if not self.active:

            self.interact_button.hide()

            return

        x, y = self.position

        target = interaction_at(x, y)

        # --------------------------------------
        # COMPUTER
        # --------------------------------------

        if target == "computer":

            message = (
                "PROGRAMMING COMPUTER READY"
            )

            self.interact_button["text"] = (
                "PRESS E  |  START PROGRAMMING"
            )

            self.interact_button["frameColor"] = (
                0.45, 0.88, 0.65, 1
            )

            self.interact_button["text_fg"] = (
                0.08, 0.27, 0.32, 1
            )

            self.interact_button.show()

            self.app.status_label["text"] = (
                "Press E or click START to open Programming Lab"
            )

        # --------------------------------------
        # EXIT DOOR
        # --------------------------------------

        elif target == "exit":

            message = (
                "EXIT DOOR READY"
            )

            self.interact_button["text"] = (
                "PRESS E  |  EXIT CLASSROOM"
            )

            self.interact_button["frameColor"] = (
                1.0, 0.82, 0.57, 1
            )

            self.interact_button["text_fg"] = (
                0.28, 0.20, 0.12, 1
            )

            self.interact_button.show()

            self.app.status_label["text"] = (
                "Press E or click EXIT to finish the game"
            )

        # --------------------------------------
        # NOT NEAR AN INTERACTIVE OBJECT
        # --------------------------------------

        else:

            message = (
                "WASD WALK | RIGHT MOUSE LOOK | "
                "FIND A COMPUTER OR EXIT"
            )

            self.interact_button.hide()

            self.app.status_label["text"] = (
                "Walk to a computer to start programming"
            )

        self.guide["text"] = message

    # ======================================================
    # PRESS E OR CLICK BUTTON
    # ======================================================

    def try_interact(self):

        if not self.active:
            return

        x, y = self.position

        target = interaction_at(x, y)

        if target == "computer":

            self.app.open_computer()

        elif target == "exit":
            self.exit_to_hub()

        else:

            self.app.status_label["text"] = (
                "Move closer to a computer or EXIT door."
            )

    def exit_to_hub(self):
        if self.active:
            self.app.show_main_hub()

    # ======================================================
    # UPDATE PLAYER
    # ======================================================

    def update(self, task):

        if not self.active:
            return Task.cont

        dt = min(
            ClockObject.getGlobalClock().getDt(),
            0.06
        )

        # ======================================
        # KEYBOARD TURNING
        # ======================================

        self.heading += self.TURN_SPEED * dt * (
            int(self.keys["arrow_left"])
            - int(self.keys["arrow_right"])
        )

        # ======================================
        # RIGHT-MOUSE CAMERA LOOK
        # ======================================

        if (
            self.mouse_look
            and self.app.win is not None
        ):

            pointer = self.app.win.getPointer(0)

            current = (
                pointer.getX(),
                pointer.getY()
            )

            if self.last_pointer is not None:

                dx = (
                    current[0]
                    - self.last_pointer[0]
                )

                dy = (
                    current[1]
                    - self.last_pointer[1]
                )

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

        # ======================================
        # WASD MOVEMENT
        # ======================================

        angle = math.radians(
            self.heading
        )

        forward = (
            math.sin(angle),
            math.cos(angle)
        )

        right = (
            math.cos(angle),
            -math.sin(angle)
        )

        forward_input = (
            int(self.keys["w"])
            - int(self.keys["s"])
        )

        side_input = (
            int(self.keys["d"])
            - int(self.keys["a"])
        )

        if forward_input or side_input:

            length = math.hypot(
                forward_input,
                side_input
            )

            dx = (
                forward[0] * forward_input
                + right[0] * side_input
            ) / length

            dy = (
                forward[1] * forward_input
                + right[1] * side_input
            ) / length

            next_x = (
                self.position[0]
                + dx * self.MOVE_SPEED * dt
            )

            next_y = (
                self.position[1]
                + dy * self.MOVE_SPEED * dt
            )

            # Check horizontal movement
            if can_walk(
                next_x,
                self.position[1]
            ):
                self.position[0] = next_x

            # Check forward/backward movement
            if can_walk(
                self.position[0],
                next_y
            ):
                self.position[1] = next_y

        # ======================================
        # UPDATE CAMERA AND UI
        # ======================================

        self.move_camera()

        self.update_prompt()

        return Task.cont
