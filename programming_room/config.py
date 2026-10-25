# config.py

WINDOW_TITLE = "Programming Room - Robot Mission"

GRID_SIZE = 5

START = (0, 0)
START_DIRECTION = "E"

TARGET = (4, 4)

BATTERIES = {
    (2, 1),
}

OBSTACLES = {
    (1, 1),
    (3, 2),
    (1, 3),
}

COMMANDS = (
    "FORWARD",
    "TURN_LEFT",
    "TURN_RIGHT",
    "IF_OBSTACLE",
    "ELSE",
    "END_IF",
)

MAX_COMMANDS = 40
ANIMATION_DELAY = 0.4

COLORS = {
    "floor": (0.89, 0.92, 1.0, 1),
    "wall": (0.78, 0.84, 0.98, 1),
    "desk": (0.85, 0.64, 0.48, 1),
    "grid": (0.86, 0.91, 0.98, 1),
    "start": (0.47, 0.84, 0.62, 1),
    "target": (1.0, 0.73, 0.44, 1),
    "obstacle": (0.91, 0.42, 0.49, 1),
    "battery": (1.0, 0.91, 0.32, 1),
    "robot": (0.35, 0.67, 1.0, 1),
}
