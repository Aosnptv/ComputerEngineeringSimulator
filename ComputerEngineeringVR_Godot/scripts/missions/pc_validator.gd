class_name PCValidator
extends RefCounted

const COMPONENTS := {
	"cpu_amber": {"type":"cpu", "socket":"EDU-A"}, "cpu_blue": {"type":"cpu", "socket":"EDU-B"},
	"cooler_a": {"type":"cooler", "socket":"EDU-A"}, "cooler_b": {"type":"cooler", "socket":"EDU-B"},
	"ram_d4": {"type":"ram", "ram_type":"DDR4"}, "ram_d5": {"type":"ram", "ram_type":"DDR5"},
	"ssd": {"type":"ssd"}, "gpu": {"type":"gpu", "watts":180},
	"psu_450": {"type":"psu", "watts":450}, "psu_650": {"type":"psu", "watts":650}
}
const BOARD := {"socket":"EDU-A", "ram_type":"DDR4", "base_watts":220}
var installed := {}
var power_links := {}

func reset() -> void:
	installed.clear(); power_links.clear()

func install(component_id: String, slot: String) -> Dictionary:
	if not COMPONENTS.has(component_id): return {"ok":false,"message":"Unknown component"}
	var component: Dictionary = COMPONENTS[component_id]
	if str(component.type) != slot and not (component.type == "psu" and slot == "psu"):
		return {"ok":false,"message":"This component belongs in a different slot."}
	if slot in ["cpu", "cooler"] and component.socket != BOARD.socket:
		return {"ok":false,"message":"Socket mismatch: choose an EDU-A part."}
	if slot == "ram" and component.ram_type != BOARD.ram_type:
		return {"ok":false,"message":"Memory type mismatch: this board requires DDR4."}
	installed[slot] = component_id
	return {"ok":true,"message":"%s installed correctly." % slot.to_upper()}

func connect_power(link: String) -> Dictionary:
	if link not in ["board_power", "cpu_power", "gpu_power"]:
		return {"ok":false,"message":"Unknown power connection."}
	power_links[link] = true
	return {"ok":true,"message":"Power connection secured."}

func inspect(required: Array[String]) -> Dictionary:
	var missing: Array[String] = []
	for item in required:
		if item.ends_with("_power"):
			if not power_links.has(item): missing.append(item)
		elif item not in ["inspection", "boot"] and not installed.has(item): missing.append(item)
	if not missing.is_empty(): return {"ok":false,"message":"Missing: " + ", ".join(missing)}
	return {"ok":true,"message":"Inspection passed."}

func boot() -> Dictionary:
	var check := inspect(["cpu","cooler","ram","ssd","gpu","psu","cpu_power","board_power","gpu_power"])
	if not check.ok: return check
	var psu: Dictionary = COMPONENTS[installed.psu]
	var required_watts := int(BOARD.base_watts) + int(COMPONENTS[installed.gpu].watts)
	if int(psu.watts) < required_watts: return {"ok":false,"message":"PSU capacity is below %d W." % required_watts}
	return {"ok":true,"message":"POST complete. Educational PC boot successful."}

