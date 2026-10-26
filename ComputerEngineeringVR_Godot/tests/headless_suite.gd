extends SceneTree

var failures: Array[String] = []

func _initialize() -> void:
	test_scoring()
	test_pc_paths()
	test_lan_paths()
	test_robot_paths()
	if failures.is_empty():
		print("GODOT HEADLESS GAMEPLAY: PASS (9/9 mission logic paths)")
		quit(0)
	else:
		printerr("GODOT HEADLESS GAMEPLAY: FAIL")
		for failure in failures: printerr(" - " + failure)
		quit(1)

func expect(value: bool, message: String) -> void:
	if not value: failures.append(message)

func test_scoring() -> void:
	var result := ScoreManager.calculate("pc","easy",{"a":true,"b":true},0,300.0,true)
	expect(result.score == 100 and result.stars == 3, "perfect scoring")
	var incomplete := ScoreManager.calculate("pc","easy",{"a":true,"b":false},0,10.0,false)
	expect(incomplete.stars == 0, "incomplete mission stars")

func install_set(pc: PCValidator, components: Array[String], slots: Array[String]) -> bool:
	for index in components.size():
		if not pc.install(components[index],slots[index]).ok: return false
	return true

func test_pc_paths() -> void:
	var pc := PCValidator.new()
	expect(install_set(pc,["ram_d4","ssd","gpu"],["ram","ssd","gpu"]),"PC Easy install")
	expect(pc.inspect(["ram","ssd","gpu"]).ok,"PC Easy inspection")
	pc.reset(); expect(install_set(pc,["cpu_amber","cooler_a","ram_d4","ssd","gpu"],["cpu","cooler","ram","ssd","gpu"]),"PC Normal install")
	pc.connect_power("cpu_power");pc.connect_power("board_power")
	expect(pc.inspect(["cpu","cooler","ram","ssd","gpu","cpu_power","board_power"]).ok,"PC Normal inspection")
	pc.reset(); expect(not pc.install("cpu_blue","cpu").ok,"PC Hard rejects incompatible CPU")
	expect(install_set(pc,["cpu_amber","cooler_a","ram_d4","ssd","gpu","psu_650"],["cpu","cooler","ram","ssd","gpu","psu"]),"PC Hard install")
	for link in ["cpu_power","board_power","gpu_power"]: pc.connect_power(link)
	expect(pc.boot().ok,"PC Hard boot")

func wire(network: NetworkModel, devices: Array[String]) -> bool:
	for device in devices:
		if not network.connect_devices(device,"switch").ok: return false
	return network.connect_devices("switch","router").ok

func test_lan_paths() -> void:
	var network:=NetworkModel.new(); network.reset(20261027); network.repair_fault()
	expect(wire(network,["pc1"]) and network.validate(["pc1"]).ok,"LAN Easy")
	network.reset(20261027); network.repair_fault(); expect(wire(network,["pc1","pc2"]) and network.validate(["pc1","pc2"]).ok,"LAN Normal")
	network.reset(20261027); expect(not network.validate(["pc1","pc2","pc3"]).ok,"LAN Hard detects fault/disconnect")
	network.repair_fault(); expect(wire(network,["pc1","pc2","pc3"]) and network.validate(["pc1","pc2","pc3"]).ok,"LAN Hard repaired")

func test_robot_paths() -> void:
	var robot:=RobotInterpreter.new()
	var easy := [{"op":"forward"},{"op":"forward"},{"op":"forward"}]
	expect(robot.run(easy,RobotInterpreter.scenarios("easy")[0]).ok,"Programming Easy")
	var normal := [{"op":"repeat","count":4,"body":[{"op":"forward"}]}]
	var normal_result:=robot.run(normal,RobotInterpreter.scenarios("normal")[0]); expect(normal_result.ok and normal_result.used_repeat,"Programming Normal")
	var adaptive := {"op":"if_obstacle","then":[{"op":"left"},{"op":"forward"},{"op":"right"},{"op":"forward"},{"op":"forward"},{"op":"right"},{"op":"forward"},{"op":"left"}],"else":[{"op":"forward"}]}
	for scenario in RobotInterpreter.scenarios("hard"):
		var hard_result:=robot.run([adaptive,adaptive,adaptive,adaptive],scenario); expect(hard_result.ok and hard_result.used_conditional,"Programming Hard scenario")
