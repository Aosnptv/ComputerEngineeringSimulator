"""Real Easy/Medium/Hard robot boards, preserving each mission's goal."""

from collections import deque
from dataclasses import replace
from functools import lru_cache

from config import GRID_SIZE
from core.levels import LEVELS

HEADINGS = ("N", "E", "S", "W")
MOVES = ((0, 1), (1, 0), (0, -1), (-1, 0))


def shortest_program_length(level):
    """Shortest number of MOVE/TURN actions needed to collect and finish."""
    batteries = tuple(sorted(level.batteries))
    full_mask = (1 << len(batteries)) - 1
    start = (*level.start, HEADINGS.index(level.direction), 0)
    queue = deque([(start, 0)])
    seen = {start}
    while queue:
        (x, y, heading, mask), count = queue.popleft()
        if (x, y) == level.target and mask == full_mask:
            return count
        for delta in (-1, 1):
            state = (x, y, (heading + delta) % 4, mask)
            if state not in seen:
                seen.add(state)
                queue.append((state, count + 1))
        dx, dy = MOVES[heading]
        nx, ny = x + dx, y + dy
        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and (nx, ny) not in level.obstacles:
            new_mask = mask
            if (nx, ny) in batteries:
                new_mask |= 1 << batteries.index((nx, ny))
            state = (nx, ny, heading, new_mask)
            if state not in seen:
                seen.add(state)
                queue.append((state, count + 1))
    return None


def add_challenging_obstacle(level):
    base_length = shortest_program_length(level)
    if base_length is None:
        return level
    choices = []
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            point = (x, y)
            if point in level.obstacles or point in level.batteries or point in (level.start, level.target):
                continue
            candidate = replace(level, obstacles=level.obstacles | frozenset({point}))
            length = shortest_program_length(candidate)
            if length is not None and length <= 32:
                choices.append((length, point, candidate))
    if not choices:
        return level
    # Prefer a blocker that forces a longer route; deterministic tie-breaking.
    return max(choices, key=lambda item: (item[0], -item[1][0], -item[1][1]))[2]


@lru_cache(maxsize=None)
def level_for_difficulty(index, difficulty="Easy"):
    level = LEVELS[index]
    if difficulty == "Classic":
        return level  # Backward-compatible rule set for legacy core tests.
    if difficulty == "Easy":
        return replace(level, obstacles=frozenset())
    if difficulty == "Medium":
        return add_challenging_obstacle(level) if not level.obstacles else level
    if difficulty == "Hard":
        medium = level_for_difficulty(index, "Medium")
        return add_challenging_obstacle(medium)
    raise ValueError("Unknown difficulty")
