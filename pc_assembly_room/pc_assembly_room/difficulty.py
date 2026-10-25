"""Room-local difficulty settings; scoring thresholds remain undefined."""
from .data import PARTS
LEVELS = ("easy", "medium")
EASY_PARTS = frozenset({"mobo_lga", "cpu_intel", "cooler_std", "ram_ddr4", "gpu_std", "ssd_std", "psu_std"})
def available_parts(level):
    if level not in LEVELS:
        raise ValueError("Unknown difficulty: " + level)
    return tuple(p for p in PARTS if level != "easy" or p.id in EASY_PARTS)
def initial_parts(level):
    return (("psu", "psu_std"), ("motherboard", "mobo_lga")) if level == "easy" else ()
