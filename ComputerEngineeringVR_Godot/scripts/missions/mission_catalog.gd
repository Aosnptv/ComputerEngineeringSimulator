class_name MissionCatalog
extends RefCounted

const MISSIONS := {
	"pc": {
		"easy": ["ram", "ssd", "gpu", "inspection"],
		"normal": ["cpu", "cooler", "ram", "ssd", "gpu", "cpu_power", "board_power", "inspection"],
		"hard": ["cpu", "cooler", "ram", "ssd", "gpu", "psu", "cpu_power", "board_power", "gpu_power", "boot"]
	},
	"lan": {
		"easy": ["pc1-switch", "switch-router", "link_check"],
		"normal": ["pc1-switch", "pc2-switch", "switch-router", "network_check", "ping"],
		"hard": ["pc1-switch", "pc2-switch", "pc3-switch", "switch-router", "addresses", "fault_fixed", "ping_all"]
	},
	"programming": {
		"easy": ["valid_program", "goal"],
		"normal": ["uses_repeat", "valid_program", "goal"],
		"hard": ["uses_conditional", "scenario_a", "scenario_b"]
	},
	"tutorial": {"easy": ["look", "move", "teleport", "turn", "left_hand", "right_hand", "grab", "release", "snap", "button", "menu", "return"]}
}

static func objectives(room: String, difficulty: String) -> Array[String]:
	var result: Array[String] = []
	for item in MISSIONS.get(room, {}).get(difficulty, []): result.append(str(item))
	return result

static func guidance(room: String, difficulty: String) -> String:
	var goals := objectives(room, difficulty)
	if difficulty == "easy": return "Follow the highlighted steps: " + ", ".join(goals)
	if difficulty == "normal": return "Complete the work area objectives. Ask for a hint when needed."
	return "Diagnose and complete the mission. Hints are available only on request."

