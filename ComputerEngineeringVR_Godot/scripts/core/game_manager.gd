extends Node

signal state_changed(state: String)
signal mission_started(room: String, difficulty: String)
signal mission_completed(result: Dictionary)

const VALID_STATES := ["STARTUP", "HUB", "BRIEFING", "ACTIVE", "PAUSED", "COMPLETED", "RESETTING"]
var state := "STARTUP"
var profile_name := "Student"
var gameplay_mode := "desktop"
var current_room := ""
var difficulty := "easy"
var mission_started_at := 0
var paused_at := 0
var paused_msec := 0
var errors: Dictionary = {}
var completed_objectives: Dictionary = {}
var scenario_seed := 20261027

func transition(next: String) -> bool:
	if next not in VALID_STATES:
		return false
	var allowed := {
		"STARTUP": ["HUB"], "HUB": ["BRIEFING"],
		"BRIEFING": ["ACTIVE", "HUB"], "ACTIVE": ["PAUSED", "COMPLETED", "RESETTING", "HUB"],
		"PAUSED": ["ACTIVE", "RESETTING", "HUB"], "COMPLETED": ["RESETTING", "HUB", "BRIEFING"],
		"RESETTING": ["ACTIVE", "HUB"]
	}
	if next not in allowed.get(state, []):
		return false
	state = next
	state_changed.emit(state)
	return true

func begin_mission(room: String, level: String, objectives: Array[String], seed := 20261027) -> void:
	current_room = room
	difficulty = level
	scenario_seed = seed
	errors.clear()
	completed_objectives.clear()
	for objective in objectives:
		completed_objectives[objective] = false
	mission_started_at = Time.get_ticks_msec()
	paused_msec = 0
	state = "ACTIVE"
	mission_started.emit(room, level)
	state_changed.emit(state)

func count_error(stable_action_id: String) -> void:
	# A continuous/repeated invalid action is counted once until a correct action clears it.
	errors[stable_action_id] = true

func clear_error_dedup(stable_action_id: String) -> void:
	errors.erase(stable_action_id)

func complete_objective(id: String) -> void:
	if completed_objectives.has(id):
		completed_objectives[id] = true

func active_seconds() -> float:
	if mission_started_at == 0:
		return 0.0
	return maxf(0.001, float(Time.get_ticks_msec() - mission_started_at - paused_msec) / 1000.0)

func finish_mission() -> Dictionary:
	var complete := not completed_objectives.is_empty()
	for passed in completed_objectives.values():
		complete = complete and bool(passed)
	var result := ScoreManager.calculate(current_room, difficulty, completed_objectives, errors.size(), active_seconds(), complete)
	result.merge({"profile": profile_name, "mode": gameplay_mode, "scenario_seed": scenario_seed, "game_version": "0.1.0", "timestamp": Time.get_datetime_string_from_system(true)})
	state = "COMPLETED"
	SaveManager.record_result(result)
	mission_completed.emit(result)
	state_changed.emit(state)
	return result

