class_name NetworkModel
extends RefCounted

const DEFAULT_CONFIG := {
	"router":{"ip":"192.168.10.1","mask":"255.255.255.0","gateway":""},
	"pc1":{"ip":"192.168.10.11","mask":"255.255.255.0","gateway":"192.168.10.1"},
	"pc2":{"ip":"192.168.10.12","mask":"255.255.255.0","gateway":"192.168.10.1"},
	"pc3":{"ip":"192.168.10.13","mask":"255.255.255.0","gateway":"192.168.10.1"}
}
var links: Array[Array] = []
var configs := DEFAULT_CONFIG.duplicate(true)
var seed := 20261027
var fault := "duplicate_ip"

func reset(scenario_seed: int) -> void:
	links.clear(); configs = DEFAULT_CONFIG.duplicate(true); seed = scenario_seed
	var faults := ["duplicate_ip", "wrong_mask", "wrong_gateway"]
	fault = faults[abs(seed) % faults.size()]
	if fault == "duplicate_ip": configs.pc3.ip = configs.pc2.ip
	elif fault == "wrong_mask": configs.pc2.mask = "255.255.0.0"
	else: configs.pc1.gateway = "192.168.10.254"

func connect_devices(a: String, b: String) -> Dictionary:
	if a == b: return {"ok":false,"message":"A cable needs two different endpoints."}
	var pair := [a, b]; pair.sort()
	if pair in links: return {"ok":false,"message":"These endpoints are already linked."}
	if not ((a.begins_with("pc") and b == "switch") or (b.begins_with("pc") and a == "switch") or (a == "switch" and b == "router") or (b == "switch" and a == "router")):
		return {"ok":false,"message":"Connect computers and router through the switch."}
	links.append(pair)
	return {"ok":true,"message":"Link is up: %s ↔ %s" % [a.to_upper(), b.to_upper()]}

func has_link(a: String, b: String) -> bool:
	var pair := [a, b]; pair.sort(); return pair in links

func repair_fault() -> Dictionary:
	configs = DEFAULT_CONFIG.duplicate(true)
	return {"ok":true,"message":"%s corrected." % fault.replace("_", " ")}

func validate(devices: Array[String]) -> Dictionary:
	if not has_link("switch", "router"): return {"ok":false,"message":"Switch-to-router link is down."}
	var ips := {}
	for device in devices:
		if not has_link(device, "switch"): return {"ok":false,"message":"%s is disconnected." % device.to_upper()}
		var cfg: Dictionary = configs[device]
		if cfg.mask != "255.255.255.0": return {"ok":false,"message":"%s has an incorrect /24 subnet mask." % device.to_upper()}
		if cfg.gateway != configs.router.ip: return {"ok":false,"message":"%s has an incorrect gateway." % device.to_upper()}
		if ips.has(cfg.ip): return {"ok":false,"message":"Duplicate IP address detected."}
		ips[cfg.ip] = true
	return {"ok":true,"message":"Ping simulation: replies received from all required devices."}

