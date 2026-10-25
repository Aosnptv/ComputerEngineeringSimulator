import unittest

from ui.text_layout import fitted_scale


class TextLayoutTests(unittest.TestCase):
    def test_short_text_keeps_its_size(self):
        self.assertEqual(fitted_scale("RUN", 0.05, 1.0), 0.05)

    def test_long_text_shrinks(self):
        self.assertLess(fitted_scale("A VERY LONG INSTRUCTION LABEL", 0.07, 0.4), 0.07)

    def test_line_width_controls_size(self):
        self.assertEqual(fitted_scale("RUN\nRESET", 0.05, 1.0), 0.05)


if __name__ == "__main__":
    unittest.main()
