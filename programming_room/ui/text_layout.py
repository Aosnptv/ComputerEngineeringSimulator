"""Sizing helpers for Panda3D DirectGUI text within pastel panels."""


def fitted_scale(text, preferred, max_width, min_scale=0.025):
    """Estimate a safe scale for text inside a width in aspect2d units.

    Panda3D font glyphs vary; reserve 25 percent of the width as padding.
    Multiline text is sized from its longest line.
    """
    longest = max((len(part) for part in str(text).splitlines()), default=0)
    if longest == 0:
        return preferred
    approximate_width_per_char = 0.72
    limit = max_width * 0.75 / (longest * approximate_width_per_char)
    return max(min_scale, min(preferred, limit))
