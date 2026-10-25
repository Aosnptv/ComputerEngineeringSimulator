"""
Programming Room
Classroom Exploration & Interaction

- WASD movement boundaries
- Three interactive desk computers
- Standalone programming kiosk
- Exit door interaction
"""

import math


# ==========================================================
# PLAYER START
# ==========================================================

PLAYER_START = (2.0, -4.8)


# ==========================================================
# PROGRAMMING COMPUTERS
# ==========================================================

# Standalone blue programming terminal
COMPUTER_POINT = (2.8, -3.2)
COMPUTER_RADIUS = 1.85

# Three classroom workstations
DESK_X_POSITIONS = (-3.8, 0.0, 3.8)

# Interaction zone in front of each desk
DESK_INTERACT_MIN_Y = -3.65
DESK_INTERACT_MAX_Y = -1.75
DESK_INTERACT_HALF_WIDTH = 1.65


# ==========================================================
# EXIT DOOR
# ==========================================================

EXIT_POINT = (-5.45, -4.25)
EXIT_RADIUS = 1.75


# ==========================================================
# OLD V5 COMPATIBILITY
# ==========================================================

ENTRY_POINT = COMPUTER_POINT
ENTRY_RADIUS = COMPUTER_RADIUS


# ==========================================================
# DISTANCE
# ==========================================================

def distance(x1, y1, x2, y2):

    return math.hypot(
        x1 - x2,
        y1 - y2
    )


# ==========================================================
# NEAR PROGRAMMING COMPUTER
# ==========================================================

def near_computer(x, y):

    # --------------------------------------
    # Standalone programming computer
    # --------------------------------------

    kiosk_distance = distance(
        x,
        y,
        COMPUTER_POINT[0],
        COMPUTER_POINT[1]
    )

    # Enter from the front/right; initial spawn should not trigger this kiosk.
    if kiosk_distance <= COMPUTER_RADIUS and x >= 2.55:
        return True

    # --------------------------------------
    # All three desk computers
    # --------------------------------------

    for desk_x in DESK_X_POSITIONS:

        close_to_desk = (
            abs(x - desk_x)
            <= DESK_INTERACT_HALF_WIDTH
        )

        correct_y = (
            DESK_INTERACT_MIN_Y
            <= y
            <= DESK_INTERACT_MAX_Y
        )

        if close_to_desk and correct_y:
            return True

    return False


# ==========================================================
# NEAR EXIT
# ==========================================================

def near_exit(x, y):

    exit_distance = distance(
        x,
        y,
        EXIT_POINT[0],
        EXIT_POINT[1]
    )

    # The visible door is mounted on the left wall. Accept the entire
    # approach area so players needn't stand on one exact floor point.
    return exit_distance <= EXIT_RADIUS or (x <= -4.75 and -5.10 <= y <= -2.80)


# ==========================================================
# COMPATIBILITY
# ==========================================================

def near_kiosk(x, y):

    return near_computer(x, y)


# ==========================================================
# FIND INTERACTIVE OBJECT
# ==========================================================

def interaction_at(x, y):

    # Door has priority
    if near_exit(x, y):
        return "exit"

    # Any programming computer
    if near_computer(x, y):
        return "computer"

    return None


# ==========================================================
# WALKING BOUNDARIES
# ==========================================================

def can_walk(x, y):

    # --------------------------------------
    # Room boundaries
    # --------------------------------------

    if not (-6.05 <= x <= 6.05):
        return False

    if not (-5.20 <= y <= 5.00):
        return False

    # --------------------------------------
    # Desks and chairs
    # --------------------------------------

    for cx in DESK_X_POSITIONS:

        if (
            abs(x - cx) < 1.35
            and -1.80 < y < 1.70
        ):
            return False

    # --------------------------------------
    # Programming kiosk collision
    # --------------------------------------

    kx, ky = COMPUTER_POINT

    if (
        abs(x - kx) < 0.62
        and abs(y - ky) < 0.57
    ):
        return False

    # --------------------------------------
    # Robot collision
    # --------------------------------------

    if (
        abs(x) < 0.85
        and 3.05 < y < 4.25
    ):
        return False

    return True
