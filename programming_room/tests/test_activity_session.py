import unittest

from core.activity_session import ActivitySession


class ActivitySessionTests(unittest.TestCase):
    def test_wrong_answer_is_zero_and_cannot_retry(self):
        session = ActivitySession(3)
        self.assertTrue(session.submit(False))
        self.assertEqual(session.score, 0)
        self.assertFalse(session.submit(True))
        self.assertEqual(session.correct_count, 0)

    def test_auto_advance_logic_and_summary_after_three(self):
        session = ActivitySession(3)
        self.assertTrue(session.submit(True))
        self.assertTrue(session.advance())
        self.assertTrue(session.submit(False))
        self.assertTrue(session.advance())
        self.assertTrue(session.submit(True))
        self.assertFalse(session.advance())
        self.assertTrue(session.finished)
        self.assertEqual(session.results, [True, False, True])
        self.assertEqual(session.correct_count, 2)
        self.assertEqual(session.score, 200)

    def test_new_activity_is_empty(self):
        first = ActivitySession()
        first.submit(True)
        second = ActivitySession()
        self.assertEqual(second.score, 0)
        self.assertEqual(second.results, [])


if __name__ == "__main__":
    unittest.main()
