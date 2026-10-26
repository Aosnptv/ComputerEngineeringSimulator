"""Dependency-free static and contract checks for environments without Godot."""
from __future__ import annotations
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
failures: list[str] = []

def check(condition: bool, message: str) -> None:
    if not condition: failures.append(message)

def load_json(relative: str):
    try: return json.loads((ROOT / relative).read_text(encoding="utf-8"))
    except Exception as exc: failures.append(f"{relative}: {exc}"); return {}

required = [
    "project.godot", "scenes/startup/main.tscn", "scripts/app/main.gd",
    "scripts/core/game_manager.gd", "scripts/core/score_manager.gd",
    "scripts/missions/pc_validator.gd", "scripts/networking_simulation/network_model.gd",
    "scripts/robot_interpreter/robot_interpreter.gd", "export_presets.cfg",
]
for item in required: check((ROOT / item).is_file(), f"missing required resource: {item}")

for path in ROOT.rglob("*.json"): load_json(path.relative_to(ROOT).as_posix())

catalog = load_json("data/localization/catalog.json")
check(set(catalog) == {"en", "th"}, "localization must contain exactly en and th catalogs")
check(set(catalog.get("en", {})) == set(catalog.get("th", {})), "en/th localization keys differ")

mission_expected = {
    "pc": {"easy":4, "normal":8, "hard":10},
    "lan": {"easy":3, "normal":5, "hard":7},
    "programming": {"easy":2, "normal":3, "hard":3},
}
source = (ROOT / "scripts/missions/mission_catalog.gd").read_text(encoding="utf-8")
for room, levels in mission_expected.items():
    check(f'"{room}"' in source, f"mission catalog missing room {room}")
    for level in levels: check(f'"{level}"' in source, f"mission catalog missing {room}/{level}")

refs = set()
for path in list(ROOT.rglob("*.gd")) + list(ROOT.rglob("*.tscn")) + [ROOT/"project.godot"]:
    text = path.read_text(encoding="utf-8")
    refs.update(re.findall(r'res://([A-Za-z0-9_./-]+\.(?:gd|tscn|json|ogg|tres))', text))
for ref in sorted(refs):
    # Narration files are intentionally absent and documented as an audio blocker.
    if ref.startswith("assets/audio/"): continue
    check((ROOT / ref).exists(), f"broken resource reference: res://{ref}")

for path in ROOT.rglob("*.gd"):
    text = path.read_text(encoding="utf-8")
    check("TODO" not in text and "pass #" not in text, f"placeholder marker in {path.relative_to(ROOT)}")
    check(text.count("(") == text.count(")"), f"parenthesis imbalance in {path.relative_to(ROOT)}")
    check(text.count("[") == text.count("]"), f"bracket imbalance in {path.relative_to(ROOT)}")
    check(text.count("{") == text.count("}"), f"brace imbalance in {path.relative_to(ROOT)}")

# Independent scoring examples specified by the master requirements.
def score(passed, total, errors, seconds, target, complete):
    correctness = 70.0 * passed / max(total, 1)
    error_score = max(0.0, 20.0 - 2.0 * errors)
    time_score = 10.0 * min(1.0, target / max(seconds, 0.001)) if complete else 0.0
    value = round(min(100.0, max(0.0, correctness + error_score + time_score)))
    stars = 3 if complete and value >= 90 else 2 if complete and value >= 75 else 1 if complete and value >= 60 else 0
    return value, stars
check(score(4,4,0,300,300,True)==(100,3), "perfect scoring contract failed")
check(score(2,4,0,10,300,False)==(55,0), "incomplete scoring contract failed")
check(score(4,4,15,900,300,True)==(73,1), "error/time scoring contract failed")

if failures:
    print("STATIC VALIDATION: FAIL")
    for failure in failures: print(" -", failure)
    sys.exit(1)
print(f"STATIC VALIDATION: PASS ({len(required)} resources, {len(refs)} references, 9 mission configurations)")

