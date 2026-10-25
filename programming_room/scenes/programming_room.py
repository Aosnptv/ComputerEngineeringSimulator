"""
Programming Room
Soft Cartoon 3D Classroom
"""

from panda3d.core import NodePath, TextNode


class ProgrammingRoom:

    def __init__(self, app):
        self.app = app
        self.root = NodePath("ProgrammingRoom")
        self.root.reparentTo(app.render)
        self.build_room()

    # ==================================================
    # NORMALIZED BOX
    # ==================================================

    def box(self, name, pos, half_size, color, parent=None):
        if parent is None:
            parent = self.root

        holder = parent.attachNewNode(name)
        holder.setPos(*pos)
        holder.setScale(*half_size)

        model = self.app.loader.loadModel("models/box")
        model.reparentTo(holder)

        bounds = model.getTightBounds()

        if bounds:
            low, high = bounds
            sizes = [high[i] - low[i] for i in range(3)]
            centers = [
                (low[i] + high[i]) / 2
                for i in range(3)
            ]
            factors = [
                2.0 / sizes[i] if sizes[i] else 1.0
                for i in range(3)
            ]

            model.setScale(*factors)
            model.setPos(
                *[-centers[i] * factors[i] for i in range(3)]
            )

        model.setTextureOff(1)
        model.setColor(*color)

        return holder

    # ==================================================
    # ROOM
    # ==================================================

    def build_room(self):
        self.build_structure()
        self.build_front_board()

        for number, x in enumerate((-3.8, 0.0, 3.8)):
            self.build_workstation(x, 0.8, number)

        # Stand in front of the board,
        # looking toward the student desks.
        self.build_robot(0, 3.65)

        self.build_programming_computer()
        self.build_exit_door()
        self.build_decorations()

    def build_structure(self):
        self.box(
            "Floor",
            (0, 0, -0.35),
            (6.8, 5.8, 0.25),
            (0.91, 0.94, 1.0, 1)
        )

        self.box(
            "BackWall",
            (0, 5.7, 2.7),
            (6.8, 0.12, 3.05),
            (0.86, 0.89, 0.98, 1)
        )

        self.box(
            "LeftWall",
            (-6.65, 0, 2.7),
            (0.12, 5.7, 3.05),
            (0.82, 0.87, 0.97, 1)
        )

        for x in (-5.5, 5.5):
            self.box(
                "FloorTrim",
                (x, 0, -0.07),
                (0.08, 5.3, 0.025),
                (0.75, 0.83, 0.96, 1)
            )

    # ==================================================
    # BLACKBOARD
    # ==================================================

    def build_front_board(self):
        self.box(
            "TeachingBoard",
            (0, 5.48, 3.35),
            (2.8, 0.09, 1.25),
            (0.36, 0.65, 0.69, 1)
        )

        wood = (0.95, 0.76, 0.51, 1)

        for z in (2.03, 4.67):
            self.box(
                "BoardHorizontalFrame",
                (0, 5.35, z),
                (2.95, 0.10, 0.075),
                wood
            )

        for x in (-2.88, 2.88):
            self.box(
                "BoardVerticalFrame",
                (x, 5.35, 3.35),
                (0.075, 0.10, 1.32),
                wood
            )

        for x, z, width in (
            (-0.5, 3.75, 1.2),
            (0.25, 3.35, 0.9),
            (-0.3, 2.95, 1.4)
        ):
            self.box(
                "BoardCodeLine",
                (x, 5.31, z),
                (width, 0.025, 0.06),
                (0.82, 0.97, 1.0, 1)
            )

    # ==================================================
    # COMPUTER DESKS
    # ==================================================

    def build_workstation(self, x, y, number):
        wood = (0.91, 0.70, 0.52, 1)
        legs = (0.72, 0.53, 0.43, 1)
        chair = (0.70, 0.76, 0.97, 1)
        dark = (0.36, 0.43, 0.58, 1)

        self.box(
            f"DeskTop_{number}",
            (x, y, 1.10),
            (1.20, 0.70, 0.12),
            wood
        )

        for dx in (-1.02, 1.02):
            for dy in (-0.52, 0.52):
                self.box(
                    f"DeskLeg_{number}",
                    (x + dx, y + dy, 0.44),
                    (0.09, 0.09, 0.54),
                    legs
                )

        self.box(
            f"MonitorBase_{number}",
            (x, y + 0.25, 1.25),
            (0.32, 0.25, 0.035),
            dark
        )

        self.box(
            f"MonitorNeck_{number}",
            (x, y + 0.25, 1.49),
            (0.055, 0.055, 0.22),
            dark
        )

        self.box(
            f"Monitor_{number}",
            (x, y + 0.25, 1.90),
            (0.59, 0.10, 0.42),
            (0.23, 0.32, 0.48, 1)
        )

        self.box(
            f"Screen_{number}",
            (x, y + 0.137, 1.90),
            (0.51, 0.015, 0.34),
            (0.49, 0.90, 0.98, 1)
        )

        self.box(
            f"Keyboard_{number}",
            (x, y - 0.31, 1.245),
            (0.47, 0.17, 0.025),
            (0.91, 0.94, 0.99, 1)
        )

        self.box(
            f"ChairSeat_{number}",
            (x, y - 1.55, 0.55),
            (0.50, 0.46, 0.10),
            chair
        )

        self.box(
            f"ChairBack_{number}",
            (x, y - 1.98, 1.05),
            (0.50, 0.08, 0.49),
            chair
        )

        self.box(
            f"ChairSupport_{number}",
            (x, y - 1.55, 0.18),
            (0.075, 0.075, 0.28),
            (0.49, 0.57, 0.73, 1)
        )

        self.box(
            f"ChairFootX_{number}",
            (x, y - 1.55, -0.045),
            (0.43, 0.07, 0.055),
            (0.49, 0.57, 0.73, 1)
        )

        self.box(
            f"ChairFootY_{number}",
            (x, y - 1.55, -0.045),
            (0.07, 0.43, 0.055),
            (0.49, 0.57, 0.73, 1)
        )

    # ==================================================
    # ROBOT TEACHER
    # ==================================================

    def build_robot(self, x, y):
        robot = self.root.attachNewNode("ClassroomRobot")
        robot.setPos(x, y, 0)

        # Face toward negative Y = computer desks
        robot.setHpr(0, 0, 0)

        blue = (0.36, 0.69, 0.98, 1)
        white = (0.94, 0.96, 1.0, 1)
        dark = (0.18, 0.31, 0.48, 1)

        for dx in (-0.27, 0.27):
            self.box(
                "Foot", (dx, 0, 0.16),
                (0.19, 0.27, 0.26), dark, robot
            )

        self.box(
            "Body", (0, 0, 0.87),
            (0.56, 0.43, 0.47), blue, robot
        )

        self.box(
            "Neck", (0, 0, 1.42),
            (0.16, 0.16, 0.17), dark, robot
        )

        self.box(
            "Head", (0, 0, 1.92),
            (0.62, 0.47, 0.39), white, robot
        )

        # Facial panel is placed toward the desks
        self.box(
            "Face", (0, -0.505, 1.92),
            (0.49, 0.025, 0.28), dark, robot
        )

        for dx in (-0.23, 0.23):
            self.box(
                "Eye", (dx, -0.54, 2.00),
                (0.09, 0.02, 0.09),
                (0.49, 0.98, 1.0, 1), robot
            )

        self.box(
            "Mouth", (0, -0.545, 1.80),
            (0.17, 0.02, 0.025),
            (0.56, 0.94, 1.0, 1), robot
        )

        for dx in (-0.68, 0.68):
            self.box(
                "Arm", (dx, 0, 0.91),
                (0.12, 0.19, 0.34), blue, robot
            )

        self.box(
            "Antenna", (0, 0, 2.43),
            (0.035, 0.035, 0.15), dark, robot
        )

        self.box(
            "AntennaTip", (0, 0, 2.61),
            (0.10, 0.10, 0.10),
            (1.0, 0.67, 0.79, 1), robot
        )

    # ==================================================
    # INTERACTIVE COMPUTER KIOSK
    # ==================================================

    def build_programming_computer(self):
        x, y = 2.8, -3.2

        self.box(
            "ProgrammingComputerBase",
            (x, y, 0.70),
            (0.48, 0.40, 0.70),
            (0.50, 0.72, 0.98, 1)
        )

        self.box(
            "ComputerHousing",
            (x, y - 0.06, 1.65),
            (0.66, 0.19, 0.57),
            (0.24, 0.43, 0.70, 1)
        )

        self.box(
            "ComputerScreen",
            (x, y - 0.275, 1.65),
            (0.57, 0.025, 0.48),
            (0.55, 0.95, 1.0, 1)
        )

        for z, width in (
            (1.85, 0.38),
            (1.63, 0.28),
            (1.43, 0.38)
        ):
            self.box(
                "ComputerCodeLine",
                (x, y - 0.315, z),
                (width, 0.01, 0.035),
                (0.20, 0.49, 0.76, 1)
            )

        self.box(
            "ComputerBeacon",
            (x, y, 2.38),
            (0.07, 0.07, 0.22),
            (0.24, 0.46, 0.77, 1)
        )

        self.box(
            "ComputerBeaconLight",
            (x, y, 2.72),
            (0.38, 0.27, 0.16),
            (0.15, 0.95, 0.93, 1)
        )

    # ==================================================
    # EXIT DOOR
    # ==================================================

    def build_exit_door(self):
        x, y = -6.48, -4.25

        self.box(
            "ExitDoor",
            (x, y, 1.36),
            (0.12, 0.75, 1.48),
            (0.57, 0.88, 0.75, 1)
        )

        frame = (0.26, 0.59, 0.57, 1)

        for side_y in (y - 0.82, y + 0.82):
            self.box(
                "ExitDoorSideFrame",
                (x - 0.05, side_y, 1.36),
                (0.16, 0.09, 1.55),
                frame
            )

        self.box(
            "ExitDoorTopFrame",
            (x - 0.05, y, 2.93),
            (0.16, 0.91, 0.09),
            frame
        )

        self.box(
            "ExitDoorHandle",
            (x + 0.15, y + 0.46, 1.25),
            (0.045, 0.055, 0.15),
            (1.0, 0.85, 0.35, 1)
        )

        self.box(
            "ExitSign",
            (x + 0.18, y, 3.22),
            (0.045, 0.57, 0.19),
            (0.20, 0.78, 0.47, 1)
        )

        exit_text = TextNode("ExitText")
        exit_text.setText("EXIT")
        exit_text.setAlign(TextNode.ACenter)
        exit_text.setTextColor(1, 1, 1, 1)

        label = self.root.attachNewNode(exit_text)
        label.setPos(x + 0.23, y, 3.14)
        label.setHpr(90, 0, 0)
        label.setScale(0.30)
        label.setTwoSided(True)

    # ==================================================
    # DECORATIONS
    # ==================================================

    def build_decorations(self):
        for x, color in (
            (-5.45, (1.0, 0.75, 0.83, 1)),
            (5.45, (0.72, 0.94, 0.78, 1))
        ):
            self.box(
                "WallDecoration",
                (x, 5.42, 3.45),
                (0.50, 0.06, 0.70),
                color
            )

    def show(self):
        self.root.show()

    def hide(self):
        self.root.hide()