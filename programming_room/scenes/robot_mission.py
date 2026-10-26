
from panda3d.core import NodePath

try:
    from ..config import GRID_SIZE
except ImportError:
    from config import GRID_SIZE


class RobotMissionScene:

    def __init__(self, app):
        self.app = app
        self.level = app.mission.level

        self.root = NodePath("RobotMissionScene")
        self.root.reparentTo(app.render)

        self.battery_models = {}

        self.build_board()
        self.build_robot()

        self.update_robot(self.app.mission.state)

    def box(self, name, pos, half_size, color, parent=None):
        """
        Create a centered 3D box.
        All scales are interpreted as half-sizes.
        """
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

            sizes = [
                high[i] - low[i]
                for i in range(3)
            ]

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
                *[
                    -centers[i] * factors[i]
                    for i in range(3)
                ]
            )

        model.setTextureOff(1)
        model.setColor(*color)

        return holder

    def build_board(self):
        center = (GRID_SIZE - 1) / 2
        half_extent = GRID_SIZE / 2 + 0.16

        # Main board foundation
        self.box(
            "BoardFoundation",
            (center, center, -0.20),
            (half_extent, half_extent, 0.14),
            (0.47, 0.62, 0.85, 1),
        )

        # Thin border around the board
        edge = (GRID_SIZE - 1) / 2 + 0.57
        border_color = (0.63, 0.80, 0.98, 1)

        self.box(
            "LeftBorder",
            (center - edge, center, -0.035),
            (0.07, half_extent, 0.10),
            border_color,
        )

        self.box(
            "RightBorder",
            (center + edge, center, -0.035),
            (0.07, half_extent, 0.10),
            border_color,
        )

        self.box(
            "FrontBorder",
            (center, center - edge, -0.035),
            (half_extent, 0.07, 0.10),
            border_color,
        )

        self.box(
            "BackBorder",
            (center, center + edge, -0.035),
            (half_extent, 0.07, 0.10),
            border_color,
        )

        # Exactly 5 x 5 centered tiles
        for x in range(GRID_SIZE):
            for y in range(GRID_SIZE):
                cell = (x, y)

                if (x + y) % 2 == 0:
                    color = (0.85, 0.93, 1.0, 1)
                else:
                    color = (0.94, 0.97, 1.0, 1)

                if cell == self.level.start:
                    color = (0.48, 0.85, 0.62, 1)

                elif cell == self.level.target:
                    color = (1.0, 0.75, 0.42, 1)

                # Lower face aligns with board top
                self.box(
                    f"Tile_{x}_{y}",
                    (x, y, 0.005),
                    (0.46, 0.46, 0.065),
                    color,
                )

                if cell in self.level.obstacles:
                    self.build_obstacle(x, y)

                if cell in self.level.batteries:
                    self.build_battery(x, y)

        self.build_goal_flag()

    def build_obstacle(self, x, y):
        # Base occupies exactly one grid cell
        self.box(
            f"ObstacleBase_{x}_{y}",
            (x, y, 0.40),
            (0.34, 0.34, 0.33),
            (0.92, 0.40, 0.51, 1),
        )

        # Top cap
        self.box(
            f"ObstacleCap_{x}_{y}",
            (x, y, 0.76),
            (0.35, 0.35, 0.055),
            (1.0, 0.65, 0.71, 1),
        )

        # Yellow warning mark on front
        self.box(
            f"WarningMark_{x}_{y}",
            (x, y - 0.347, 0.43),
            (0.10, 0.015, 0.18),
            (1.0, 0.88, 0.40, 1),
        )

    def build_battery(self, x, y):
        # Movable parent node, positioned at cell center
        battery = self.root.attachNewNode(
            f"Battery_{x}_{y}"
        )
        battery.setPos(x, y, 0.30)

        self.box(
            "BatteryBody",
            (0, 0, 0.02),
            (0.23, 0.18, 0.21),
            (1.0, 0.87, 0.27, 1),
            parent=battery,
        )

        self.box(
            "BatteryTop",
            (0, 0, 0.27),
            (0.11, 0.11, 0.05),
            (0.84, 0.65, 0.14, 1),
            parent=battery,
        )

        # Battery plus symbol
        self.box(
            "BatteryPlusVertical",
            (0, -0.194, 0.02),
            (0.035, 0.012, 0.11),
            (1, 1, 1, 1),
            parent=battery,
        )

        self.box(
            "BatteryPlusHorizontal",
            (0, -0.197, 0.02),
            (0.10, 0.012, 0.035),
            (1, 1, 1, 1),
            parent=battery,
        )

        self.battery_models[(x, y)] = battery

    def build_goal_flag(self):
        x, y = self.level.target

        # Flag sits at the back-right corner of goal tile
        self.box(
            "GoalPole",
            (x + 0.30, y + 0.28, 0.66),
            (0.035, 0.035, 0.58),
            (0.95, 0.96, 1, 1),
        )

        self.box(
            "GoalFlag",
            (x + 0.08, y + 0.28, 1.02),
            (0.24, 0.035, 0.15),
            (1.0, 0.52, 0.33, 1),
        )

    def build_robot(self):
        # One parent: body, head and feet move together
        self.robot = self.root.attachNewNode("Robot")

        blue = (0.36, 0.69, 1.0, 1)
        white = (0.95, 0.97, 1.0, 1)
        dark = (0.18, 0.31, 0.50, 1)
        eye_color = (0.51, 0.96, 1.0, 1)

        # Feet stand just above the tile surface
        for dx in (-0.16, 0.16):
            self.box(
                "RobotFoot",
                (dx, 0.01, 0.11),
                (0.11, 0.16, 0.07),
                dark,
                parent=self.robot,
            )

        # Body
        self.box(
            "RobotBody",
            (0, 0, 0.43),
            (0.27, 0.24, 0.25),
            blue,
            parent=self.robot,
        )

        # Neck
        self.box(
            "RobotNeck",
            (0, 0, 0.73),
            (0.10, 0.10, 0.09),
            dark,
            parent=self.robot,
        )

        # Head
        self.box(
            "RobotHead",
            (0, 0, 0.96),
            (0.30, 0.25, 0.19),
            white,
            parent=self.robot,
        )

        # Face looks toward local +Y
        self.box(
            "RobotFace",
            (0, 0.255, 0.96),
            (0.24, 0.018, 0.13),
            dark,
            parent=self.robot,
        )

        # Eyes
        for dx in (-0.12, 0.12):
            self.box(
                "RobotEye",
                (dx, 0.277, 1.00),
                (0.048, 0.013, 0.047),
                eye_color,
                parent=self.robot,
            )

        # Arms
        for dx in (-0.36, 0.36):
            self.box(
                "RobotArm",
                (dx, 0, 0.44),
                (0.09, 0.11, 0.17),
                (0.44, 0.58, 0.88, 1),
                parent=self.robot,
            )

        # Antenna
        self.box(
            "AntennaStem",
            (0, 0, 1.23),
            (0.025, 0.025, 0.11),
            dark,
            parent=self.robot,
        )

        self.box(
            "AntennaTip",
            (0, 0, 1.36),
            (0.07, 0.07, 0.07),
            (1.0, 0.65, 0.77, 1),
            parent=self.robot,
        )

    def update_robot(self, state):
        x, y = state.position

        # Robot origin sits at the exact center of its tile
        self.robot.setPos(x, y, 0)

        # Local +Y is forward
        headings = {
            "N": 0,
            "E": -90,
            "S": 180,
            "W": 90,
        }

        self.robot.setH(headings[state.direction])

        # Hide batteries collected by the logic system
        for position, model in self.battery_models.items():
            if position in state.collected:
                model.hide()
            else:
                model.show()

    def reset(self, state):
        self.update_robot(state)

    def show(self):
        self.root.show()

    def hide(self):
        self.root.hide()
