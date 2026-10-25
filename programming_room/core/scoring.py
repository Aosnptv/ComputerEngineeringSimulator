"""Shared Programming Lab timing, mistakes, and star rules."""
from time import monotonic


def rate_stars(elapsed, mistakes, difficulty="Easy"):
    """A completed task always earns at least one star; no time limit."""
    target = {"Easy": 90, "Medium": 120, "Hard": 180}.get(difficulty, 90)
    if mistakes <= 1 and elapsed <= target:
        return 3
    if mistakes <= 3 and elapsed <= target * 2:
        return 2
    return 1


class Attempt:
    def __init__(self):
        self.reset()

    def reset(self):
        self.started = monotonic()
        self.mistakes = 0

    def error(self):
        self.mistakes += 1

    @property
    def elapsed(self):
        return monotonic() - self.started

    def stars(self, difficulty):
        return rate_stars(self.elapsed, self.mistakes, difficulty)
