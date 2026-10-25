import unittest

from core.code_runner import parse_program, validate_single_code
from core.scoring import Attempt, rate_stars


class ProgrammingModesTests(unittest.TestCase):
    def test_python_and_c_robot_commands(self):
        self.assertEqual(parse_program("robot.move_forward()\nrobot.turn_right()", "Python"), ("FORWARD", "TURN_RIGHT"))
        self.assertEqual(parse_program("move_forward();\nturn_right();", "C"), ("FORWARD", "TURN_RIGHT"))

    def test_no_arbitrary_code_is_executed(self):
        with self.assertRaises(ValueError):
            parse_program("import os", "Python")
        self.assertFalse(validate_single_code("system(\"dir\");", "FORWARD", "C"))

    def test_scoring_uses_both_inputs(self):
        self.assertEqual(rate_stars(25, 0), 3)
        self.assertEqual(rate_stars(120, 2), 2)
        self.assertEqual(rate_stars(600, 8), 1)

    def test_attempt_reset(self):
        attempt = Attempt()
        attempt.error()
        self.assertEqual(attempt.mistakes, 1)
        attempt.reset()
        self.assertEqual(attempt.mistakes, 0)


if __name__ == "__main__":
    unittest.main()
