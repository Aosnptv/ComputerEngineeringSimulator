"""PROVISIONAL standalone-demo policy, not the team's shared scoring standard.
No timeout: these limits affect stars only, never whether a player may finish.
Replace/inject this policy once the team approves the shared service.
"""
from math import isfinite
# level -> (3-star seconds, maximum mistakes, 2-star seconds, maximum mistakes)
TRIAL_THRESHOLDS = {
    'easy': (300, 1, 600, 4),
    'medium': (420, 1, 840, 4),
}

def trial_stars(level, elapsed_seconds, mistakes):
    if level not in TRIAL_THRESHOLDS:
        raise ValueError('Unknown difficulty')
    if not isfinite(elapsed_seconds) or elapsed_seconds < 0 or mistakes < 0:
        raise ValueError('Invalid result')
    t3, e3, t2, e2 = TRIAL_THRESHOLDS[level]
    if elapsed_seconds <= t3 and mistakes <= e3:
        return 3
    if elapsed_seconds <= t2 and mistakes <= e2:
        return 2
    return 1

def clock_text(seconds):
    seconds = int(seconds)
    return f'{seconds // 60:02d}:{seconds % 60:02d}'
