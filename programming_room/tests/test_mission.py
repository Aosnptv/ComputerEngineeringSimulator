# tests/test_mission.py

import unittest

from config import (
    START,
    TARGET,
    BATTERIES,
    OBSTACLES,
)

from core.mission import RobotMission
from core.levels import LEVELS
from core.validator import (
    CommandValidator,
    MissingBlockPuzzle,
)


DEMO_COMMANDS = [
    "FORWARD",
    "FORWARD",
    "TURN_LEFT",
    "FORWARD",
    "TURN_RIGHT",
    "FORWARD",
    "FORWARD",
    "TURN_LEFT",
    "FORWARD",
    "FORWARD",
    "FORWARD",
]


class TestRobotMission(unittest.TestCase):

    def setUp(self):
        # V3 mission is preserved as Level 3 of V4.
        self.mission = RobotMission(2)

    def test_start_position(self):
        self.assertEqual(
            self.mission.state.position,
            START,
        )

    def test_forward(self):
        self.assertTrue(
            self.mission.execute("FORWARD")
        )

        self.assertEqual(
            self.mission.state.position,
            (1, 0),
        )

    def test_turn_left(self):
        self.mission.execute("TURN_LEFT")

        self.assertEqual(
            self.mission.state.direction,
            "N",
        )

    def test_turn_right(self):
        self.mission.execute("TURN_RIGHT")

        self.assertEqual(
            self.mission.state.direction,
            "S",
        )

    def test_boundary(self):
        self.mission.execute("TURN_RIGHT")

        result = self.mission.execute("FORWARD")

        self.assertFalse(result)
        self.assertEqual(
            self.mission.state.position,
            START,
        )

    def test_obstacle(self):
        self.mission.execute("FORWARD")
        self.mission.execute("TURN_LEFT")

        result = self.mission.execute("FORWARD")

        self.assertFalse(result)
        self.assertEqual(
            self.mission.state.position,
            (1, 0),
        )

    def test_invalid_command(self):
        result = self.mission.execute("FLY")

        self.assertFalse(result)

    def test_reset(self):
        self.mission.execute("FORWARD")
        self.mission.reset()

        self.assertEqual(
            self.mission.state.position,
            START,
        )

        self.assertEqual(
            self.mission.state.steps,
            0,
        )

    def test_validator(self):
        valid, _ = CommandValidator.validate(
            ["FORWARD", "TURN_LEFT"]
        )

        self.assertTrue(valid)

    def test_invalid_validator(self):
        valid, _ = CommandValidator.validate(
            ["FORWARD", "PYTHON_CODE"]
        )

        self.assertFalse(valid)

    def test_missing_block(self):
        self.assertTrue(
            MissingBlockPuzzle.check_answer(
                "TURN_LEFT"
            )
        )

    def test_demo_completes_mission(self):
        for command in DEMO_COMMANDS:
            self.assertTrue(
                self.mission.execute(command)
            )

        self.assertEqual(
            self.mission.state.position,
            TARGET,
        )

        self.assertEqual(
            self.mission.state.collected,
            BATTERIES,
        )

        self.assertTrue(
            self.mission.state.completed
        )

    def test_obstacles_are_valid(self):
        self.assertNotIn(START, OBSTACLES)
        self.assertNotIn(TARGET, OBSTACLES)

        for battery in BATTERIES:
            self.assertNotIn(battery, OBSTACLES)

    def test_all_five_demos_complete(self):
        for index, level in enumerate(LEVELS):
            mission = RobotMission(index)
            for command in level.demo:
                self.assertTrue(mission.execute(command), (index, command))
            self.assertTrue(mission.state.completed, index)
            self.assertEqual(mission.state.collected, level.batteries)

    def test_change_level_resets_position(self):
        self.mission.execute("FORWARD")
        self.mission.set_level(0)
        self.assertEqual(self.mission.state.position, LEVELS[0].start)
        self.assertEqual(self.mission.state.steps, 0)


if __name__ == "__main__":
    unittest.main()
