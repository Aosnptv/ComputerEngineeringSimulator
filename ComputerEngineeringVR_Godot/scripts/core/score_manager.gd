class_name ScoreManager
extends RefCounted

const TARGETS := {
	"pc": {"easy": 300.0, "normal": 480.0, "hard": 720.0},
	"lan": {"easy": 240.0, "normal": 420.0, "hard": 600.0},
	"programming": {"easy": 240.0, "normal": 420.0, "hard": 600.0},
	"tutorial": {"easy": 300.0}
}

static func calculate(room: String, difficulty: String, objectives: Dictionary, errors: int, seconds: float, complete: bool) -> Dictionary:
	var total := maxi(1, objectives.size())
	var passed := 0
	for value in objectives.values():
		if bool(value): passed += 1
	var correctness := 70.0 * float(passed) / float(total)
	var error_score := maxf(0.0, 20.0 - 2.0 * errors)
	var target := float(TARGETS.get(room, {}).get(difficulty, 300.0))
	var time_score := 10.0 * minf(1.0, target / maxf(seconds, 0.001)) if complete else 0.0
	var score := clampf(correctness + error_score + time_score, 0.0, 100.0)
	var rounded := int(round(score))
	var stars := 0
	if complete:
		stars = 3 if rounded >= 90 else (2 if rounded >= 75 else (1 if rounded >= 60 else 0))
	return {"room": room, "difficulty": difficulty, "completed": complete, "score": rounded, "stars": stars, "active_seconds": snappedf(seconds, 0.01), "error_count": errors, "objective_results": objectives.duplicate(true)}

