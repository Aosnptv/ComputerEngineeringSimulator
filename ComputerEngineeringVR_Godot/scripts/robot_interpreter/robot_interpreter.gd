class_name RobotInterpreter
extends RefCounted

const DIRECTIONS := [Vector2i(0,-1), Vector2i(1,0), Vector2i(0,1), Vector2i(-1,0)]
const MAX_STEPS := 256

func run(program: Array, scenario: Dictionary) -> Dictionary:
	var state := {"position": scenario.start, "direction": int(scenario.get("direction", 1)), "steps": 0, "collided": false, "trace": [], "used_repeat": false, "used_conditional": false, "error": ""}
	_execute(program, scenario, state)
	return {"ok": state.error.is_empty() and not state.collided and state.position == scenario.goal, "position": state.position, "direction": state.direction, "steps": state.steps, "trace": state.trace, "used_repeat": state.used_repeat, "used_conditional": state.used_conditional, "error": state.error}

func _execute(program: Array, scenario: Dictionary, state: Dictionary) -> void:
	for command in program:
		if state.error != "": return
		state.steps += 1
		if state.steps > MAX_STEPS: state.error = "Execution limit exceeded."; return
		var op := str(command.get("op", ""))
		match op:
			"forward":
				var next: Vector2i = state.position + DIRECTIONS[state.direction]
				if next.x < 0 or next.y < 0 or next.x >= int(scenario.size) or next.y >= int(scenario.size) or next in scenario.obstacles:
					state.collided = true; state.error = "Robot hit an obstacle or boundary."; return
				state.position = next
			"left": state.direction = (state.direction + 3) % 4
			"right": state.direction = (state.direction + 1) % 4
			"repeat":
				state.used_repeat = true
				var count := clampi(int(command.get("count", 0)), 0, 20)
				for _i in count: _execute(command.get("body", []), scenario, state)
			"if_obstacle":
				state.used_conditional = true
				var ahead: Vector2i = state.position + DIRECTIONS[state.direction]
				var blocked: bool = ahead.x < 0 or ahead.y < 0 or ahead.x >= int(scenario.size) or ahead.y >= int(scenario.size) or ahead in scenario.obstacles
				_execute(command.get("then", []) if blocked else command.get("else", []), scenario, state)
			_: state.error = "Unknown command: " + op; return
		state.trace.append({"op":op, "position":state.position, "direction":state.direction})

static func scenarios(difficulty: String) -> Array[Dictionary]:
	if difficulty == "easy": return [{"size":4,"start":Vector2i(0,3),"goal":Vector2i(3,3),"direction":1,"obstacles":[]}]
	if difficulty == "normal": return [{"size":5,"start":Vector2i(0,4),"goal":Vector2i(4,4),"direction":1,"obstacles":[Vector2i(2,2)]}]
	return [
		{"size":6,"start":Vector2i(0,5),"goal":Vector2i(5,5),"direction":1,"obstacles":[Vector2i(2,5)]},
		{"size":6,"start":Vector2i(0,5),"goal":Vector2i(5,5),"direction":1,"obstacles":[Vector2i(4,5)]}
	]
