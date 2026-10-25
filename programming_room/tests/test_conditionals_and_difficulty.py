import unittest

from core.difficulty import level_for_difficulty, shortest_program_length
from core.mission import RobotMission
from core.program_flow import ProgramRunner
from core.validator import CommandValidator


class ConditionAndDifficultyTests(unittest.TestCase):
    def test_if_false_runs_else_branch(self):
        robot = RobotMission(0, "Easy")
        program = ProgramRunner(["IF_OBSTACLE", "TURN_LEFT", "ELSE", "FORWARD", "END_IF", "FORWARD"])
        while (instruction := program.next_instruction(robot)) is not None:
            self.assertTrue(robot.execute(instruction))
        self.assertTrue(robot.state.completed)

    def test_if_true_runs_then_branch(self):
        robot = RobotMission(0, "Hard")
        self.assertTrue(robot.obstacle_ahead())
        program = ProgramRunner(["IF_OBSTACLE", "TURN_LEFT", "ELSE", "FORWARD", "END_IF"])
        instruction = program.next_instruction(robot)
        self.assertEqual(instruction, "TURN_LEFT")
        self.assertTrue(robot.execute(instruction))
        self.assertIsNone(program.next_instruction(robot))
        self.assertEqual(robot.state.direction, "N")

    def test_hard_requires_structure(self):
        okay, reason = CommandValidator.validate(["FORWARD"], require_conditional=True)
        self.assertFalse(okay)
        self.assertIn("Hard mode", reason)

    def test_broken_if_rejected(self):
        for commands in (["IF_OBSTACLE", "FORWARD"], ["ELSE", "FORWARD"], ["IF_OBSTACLE", "ELSE", "ELSE", "END_IF", "FORWARD"]):
            with self.subTest(commands=commands):
                with self.assertRaises(ValueError):
                    ProgramRunner(commands)

    def test_all_difficulties_are_solvable_and_hard_is_more_complex(self):
        for index in range(5):
            with self.subTest(level=index):
                easy = level_for_difficulty(index, "Easy")
                medium = level_for_difficulty(index, "Medium")
                hard = level_for_difficulty(index, "Hard")
                self.assertLessEqual(len(easy.obstacles), len(medium.obstacles))
                self.assertLess(len(medium.obstacles), len(hard.obstacles))
                for level in (easy, medium, hard):
                    self.assertIsNotNone(shortest_program_length(level))
                self.assertGreater(shortest_program_length(hard), shortest_program_length(easy))


if __name__ == "__main__":
    unittest.main()
