# core/mission.py

from dataclasses import dataclass, field
from typing import Set, Tuple

from config import (
    GRID_SIZE,
)
from core.levels import LEVELS
from core.difficulty import level_for_difficulty

DIRECTIONS = ("N", "E", "S", "W")

MOVEMENT = {
    "N": (0, 1),
    "E": (1, 0),
    "S": (0, -1),
    "W": (-1, 0),
}


@dataclass
class MissionState:
    position: Tuple[int, int] = (0, 0)
    direction: str = "E"
    collected: Set[Tuple[int, int]] = field(
        default_factory=set
    )
    steps: int = 0
    completed: bool = False
    error: str = ""


class RobotMission:

    def __init__(self, level_index=0, difficulty="Classic"):
        self.level_index = level_index
        self.difficulty = difficulty
        self.level = level_for_difficulty(level_index, difficulty)
        self.reset()

    def set_level(self, level_index, difficulty=None):
        if not 0 <= level_index < len(LEVELS):
            raise ValueError("Unknown level")
        self.level_index = level_index
        if difficulty is not None:
            self.difficulty = difficulty
        self.level = level_for_difficulty(level_index, self.difficulty)
        self.reset()

    def reset(self):
        self.state = MissionState(
            position=self.level.start,
            direction=self.level.direction,
        )
        return self.state

    def turn_left(self):
        index = DIRECTIONS.index(self.state.direction)
        self.state.direction = DIRECTIONS[(index - 1) % 4]

    def turn_right(self):
        index = DIRECTIONS.index(self.state.direction)
        self.state.direction = DIRECTIONS[(index + 1) % 4]

    def forward(self):
        x, y = self.state.position
        dx, dy = MOVEMENT[self.state.direction]

        new_position = (x + dx, y + dy)
        nx, ny = new_position

        if not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE):
            self.state.error = "Robot moved outside the grid"
            return False

        if new_position in self.level.obstacles:
            self.state.error = "Robot hit an obstacle"
            return False

        self.state.position = new_position
        self.state.steps += 1

        if new_position in self.level.batteries:
            self.state.collected.add(new_position)

        return True

    def obstacle_ahead(self):
        """True when the next cell is blocked by an obstacle or the board edge."""
        x, y = self.state.position
        dx, dy = MOVEMENT[self.state.direction]
        nx, ny = x + dx, y + dy
        return not (0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE) or (nx, ny) in self.level.obstacles

    def execute(self, command):
        if self.state.completed:
            return False

        self.state.error = ""

        if command == "FORWARD":
            success = self.forward()

        elif command == "TURN_LEFT":
            self.turn_left()
            success = True

        elif command == "TURN_RIGHT":
            self.turn_right()
            success = True

        else:
            self.state.error = "Invalid command"
            return False

        if not success:
            return False

        if (
            self.state.position == self.level.target
            and self.state.collected == self.level.batteries
        ):
            self.state.completed = True

        return True

    def get_score(self):
        battery_points = len(self.state.collected) * 100

        if self.state.completed:
            return battery_points + 500

        return battery_points

    def get_status(self):
        if self.state.error:
            return self.state.error

        if self.state.completed:
            return "MISSION COMPLETE!"

        if self.state.position == self.level.target:
            return "Collect all batteries first!"

        return "Mission in progress"
