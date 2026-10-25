"""Five playable levels; all coordinates use the same 5x5 grid."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Level:
    title: str
    start: tuple
    direction: str
    target: tuple
    batteries: frozenset
    obstacles: frozenset
    demo: tuple
    three_star_limit: int


F = "FORWARD"
L = "TURN_LEFT"
R = "TURN_RIGHT"

LEVELS = (
    Level("First Steps", (0, 0), "E", (2, 0), frozenset(),
          frozenset(), (F, F), 2),
    Level("Turning Robot", (0, 0), "E", (2, 2), frozenset(),
          frozenset({(1, 1)}), (F, F, L, F, F), 5),
    Level("Battery Hunt", (0, 0), "E", (4, 4), frozenset({(2, 1)}),
          frozenset({(1, 1), (3, 2), (1, 3)}),
          (F, F, L, F, R, F, F, L, F, F, F), 11),
    Level("Avoid Obstacles", (0, 0), "E", (4, 2), frozenset({(0, 2)}),
          frozenset({(1, 0), (2, 0), (3, 1), (2, 3)}),
          (L, F, F, R, F, F, F, F), 8),
    Level("Final Mission", (0, 0), "E", (4, 4),
          frozenset({(0, 2), (3, 4)}),
          frozenset({(1, 1), (2, 2), (3, 2), (1, 3)}),
          (L, F, F, F, F, R, F, F, F, F), 10),
)
