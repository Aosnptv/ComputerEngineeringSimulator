import unittest

from core.exploration import can_walk, near_kiosk, interaction_at


class ExplorationTests(unittest.TestCase):
    def test_start_is_walkable(self):
        self.assertTrue(can_walk(2.0, -4.5))

    def test_wall_blocks_movement(self):
        self.assertFalse(can_walk(7, 0))

    def test_desk_blocks_movement(self):
        self.assertFalse(can_walk(0, 0.8))

    def test_robot_blocks_movement(self):
        # Current low-poly robot is at the front of the classroom.
        self.assertFalse(can_walk(0, 3.5))

    def test_player_can_approach_kiosk(self):
        self.assertTrue(can_walk(3.8, -4.6))
        self.assertTrue(near_kiosk(3.8, -4.6))

    def test_far_from_kiosk_cannot_enter(self):
        self.assertFalse(near_kiosk(2.0, -4.5))

    def test_exit_detected_across_door_approach(self):
        self.assertEqual(interaction_at(-5.0, -4.9), "exit")
        self.assertEqual(interaction_at(-5.0, -3.0), "exit")
        self.assertIsNone(interaction_at(0.0, -5.0))


if __name__ == "__main__":
    unittest.main()
