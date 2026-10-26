extends Node

var world: Node3D
var ui: CanvasLayer
var panel: PanelContainer
var panel_scroll: ScrollContainer
var title_label: Label
var body_label: Label
var status_label: Label
var objective_label: Label
var reticle: Label
var player: DesktopPlayer
var xr_player: XRPlayer
var current_screen := "language"
var selected_component := ""
var selected_endpoint := ""
var pc := PCValidator.new()
var network := NetworkModel.new()
var robot := RobotInterpreter.new()
var program: Array = []
var interactive_nodes: Array[Interactable] = []
var palette := {"navy":Color("172a46"), "blue":Color("2f7fc1"), "cyan":Color("48c8d8"), "cream":Color("f2eadf"), "wood":Color("8c623d"), "green":Color("45b879"), "red":Color("dd5d5d")}

func _ready() -> void:
	build_world_root()
	build_ui()
	show_language()

func build_world_root() -> void:
	world = Node3D.new(); world.name = "World"; add_child(world)
	var environment := WorldEnvironment.new(); var env := Environment.new()
	env.background_mode = Environment.BG_COLOR; env.background_color = Color("17243a")
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR; env.ambient_light_color = Color("c9dcff"); env.ambient_light_energy = 0.55
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC; environment.environment = env; world.add_child(environment)
	player = preload("res://scenes/player/desktop_player.tscn").instantiate()
	player.position = Vector3(0,0,5); player.interaction_requested.connect(_on_interact); player.target_changed.connect(_on_target_changed); world.add_child(player)

func build_ui() -> void:
	ui = CanvasLayer.new(); ui.layer = 10; add_child(ui)
	var margin := MarginContainer.new(); margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	margin.add_theme_constant_override("margin_left", 28); margin.add_theme_constant_override("margin_top", 24); margin.add_theme_constant_override("margin_right", 28); margin.add_theme_constant_override("margin_bottom", 24); ui.add_child(margin)
	var root_box := VBoxContainer.new(); root_box.add_theme_constant_override("separation", 12); margin.add_child(root_box)
	var top := HBoxContainer.new(); root_box.add_child(top)
	title_label = Label.new(); title_label.text = "COMPUTER ENGINEERING VR"; title_label.add_theme_font_size_override("font_size", 28); title_label.add_theme_color_override("font_color", Color("76d7e8")); title_label.size_flags_horizontal = Control.SIZE_EXPAND_FILL; top.add_child(title_label)
	objective_label = Label.new(); objective_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT; objective_label.add_theme_font_size_override("font_size", 18); top.add_child(objective_label)
	panel_scroll = ScrollContainer.new(); panel_scroll.custom_minimum_size = Vector2(490, 500); panel_scroll.size_flags_horizontal = Control.SIZE_SHRINK_BEGIN; panel_scroll.size_flags_vertical = Control.SIZE_EXPAND_FILL; panel_scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED; root_box.add_child(panel_scroll)
	panel = PanelContainer.new(); panel.custom_minimum_size = Vector2(470, 0); panel.size_flags_horizontal = Control.SIZE_EXPAND_FILL; panel_scroll.add_child(panel)
	var style := StyleBoxFlat.new(); style.bg_color = Color(0.035,0.07,0.13,0.94); style.border_color = Color("2f7fc1"); style.set_border_width_all(2); style.corner_radius_top_left=12;style.corner_radius_top_right=12;style.corner_radius_bottom_left=12;style.corner_radius_bottom_right=12; style.set_content_margin_all(20)
	panel.add_theme_stylebox_override("panel", style)
	body_label = Label.new(); body_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; body_label.add_theme_font_size_override("font_size", 18)
	status_label = Label.new(); status_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; status_label.add_theme_font_size_override("font_size", 17); status_label.add_theme_color_override("font_color", Color("ffd166")); root_box.add_child(status_label)
	reticle = Label.new(); reticle.text = "+"; reticle.add_theme_font_size_override("font_size", 30); reticle.position = Vector2(634,345); ui.add_child(reticle)

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("capture_screenshot"):
		capture_qa_screenshot()

func capture_qa_screenshot() -> void:
	var directory := "user://qa_screenshots"
	DirAccess.make_dir_recursive_absolute(directory)
	var stamp := "%s_%d" % [Time.get_datetime_string_from_system().replace(":", "-").replace("T", "_"), Time.get_ticks_msec()]
	var context := "%s_%s" % [GameManager.current_room if not GameManager.current_room.is_empty() else current_screen, GameManager.difficulty]
	var path := "%s/%s_%s.png" % [directory, context, stamp]
	var error := get_viewport().get_texture().get_image().save_png(path)
	status_label.text = "Screenshot saved: " + path if error == OK else "Screenshot failed: %s" % error

func clear_panel() -> VBoxContainer:
	panel_scroll.scroll_vertical = 0
	for child in panel.get_children(): child.queue_free()
	var box := VBoxContainer.new(); box.add_theme_constant_override("separation", 10); panel.add_child(box); return box

func add_heading(box: VBoxContainer, text: String) -> void:
	var label := Label.new(); label.text = text; label.add_theme_font_size_override("font_size", 25); label.add_theme_color_override("font_color", Color("68d5e7")); box.add_child(label)

func add_text(box: VBoxContainer, text: String) -> Label:
	var label := Label.new(); label.text = text; label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART; label.add_theme_font_size_override("font_size", 17); box.add_child(label); return label

func add_button(box: VBoxContainer, text: String, callback: Callable, color := Color("2f7fc1")) -> Button:
	var button := Button.new(); button.text = text; button.custom_minimum_size.y = 42; button.add_theme_font_size_override("font_size", 17)
	var normal := StyleBoxFlat.new(); normal.bg_color = color; normal.corner_radius_top_left=7;normal.corner_radius_top_right=7;normal.corner_radius_bottom_left=7;normal.corner_radius_bottom_right=7; normal.set_content_margin_all(8); button.add_theme_stylebox_override("normal", normal)
	button.pressed.connect(callback); box.add_child(button); return button

func show_language() -> void:
	current_screen = "language"; player.enabled = false; Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var box := clear_panel(); add_heading(box, "Choose language / เลือกภาษา")
	add_text(box, "UI and subtitles support English and Thai. Instructional narration is designed for Thai audio.")
	add_button(box, "English", func(): I18n.set_language("en"); show_profile())
	add_button(box, "ไทย", func(): I18n.set_language("th"); show_profile())

func show_profile() -> void:
	current_screen = "profile"; var box := clear_panel(); add_heading(box, I18n.t("profile.title", "Player profile"))
	var edit := LineEdit.new(); edit.placeholder_text = I18n.t("profile.placeholder", "Student name"); edit.max_length = 24; box.add_child(edit)
	add_button(box, I18n.t("continue", "Continue"), func(): SaveManager.ensure_profile(edit.text); show_mode())

func show_mode() -> void:
	current_screen = "mode"; var box := clear_panel(); add_heading(box, I18n.t("mode.title", "Choose play mode"))
	add_button(box, I18n.t("mode.desktop", "Desktop — keyboard and mouse"), func(): GameManager.gameplay_mode="desktop"; enter_hub())
	add_button(box, I18n.t("mode.vr", "VR — OpenXR / SteamVR"), func(): start_xr())

func start_xr() -> void:
	GameManager.gameplay_mode = "vr"
	xr_player = preload("res://scenes/player/xr_player.tscn").instantiate(); xr_player.xr_status.connect(func(message): status_label.text=message); world.add_child(xr_player)
	player.enabled = false
	enter_hub()

func enter_hub() -> void:
	GameManager.state = "HUB"; current_screen = "hub"; objective_label.text = I18n.t("hub.objective", "Choose a learning laboratory")
	build_room("hub")
	if GameManager.gameplay_mode == "desktop": player.enabled = true; reset_desktop_view(); Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var box := clear_panel(); add_heading(box, I18n.t("hub.title", "Main Hub")); add_text(box, I18n.t("hub.help", "Walk to a station and press E, or use these accessible controls."))
	add_button(box, "PC Assembly", func(): show_difficulty("pc"), palette.blue)
	add_button(box, "LAN Networking", func(): show_difficulty("lan"), palette.green)
	add_button(box, "Programming & Robotics", func(): show_difficulty("programming"), Color("8b67c9"))
	add_button(box, I18n.t("tutorial", "Controls tutorial"), func(): show_difficulty("tutorial"), Color("ca8b3c"))
	add_button(box, I18n.t("progress", "Progress / results"), show_progress, Color("4d607d"))
	set_neutral_status(I18n.t("controls.desktop", "WASD move • Mouse look • E/click interact • Esc release mouse • H hint"))

func show_difficulty(room: String) -> void:
	GameManager.current_room = room; current_screen = "difficulty"; player.enabled = false; Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	var box := clear_panel(); add_heading(box, room_name(room)); add_text(box, I18n.t("difficulty.help", "All levels are unlocked. Choose your guidance level."))
	for level in (["easy"] if room == "tutorial" else ["easy","normal","hard"]):
		add_button(box, level.to_upper() + " — " + guidance_name(level), func(value=level): start_mission(room, value))
	add_button(box, I18n.t("back", "Back to Hub"), enter_hub, Color("4d607d"))

func start_mission(room: String, difficulty: String) -> void:
	GameManager.begin_mission(room, difficulty, MissionCatalog.objectives(room, difficulty), 20261027)
	current_screen = "mission"; selected_component=""; selected_endpoint=""; program.clear(); pc.reset(); network.reset(GameManager.scenario_seed)
	build_room(room); player.enabled = GameManager.gameplay_mode == "desktop"; reset_desktop_view(); Input.mouse_mode = Input.MOUSE_MODE_VISIBLE
	objective_label.text = "%s • %s • 0/%d" % [room_name(room), difficulty.to_upper(), GameManager.completed_objectives.size()]
	var box := clear_panel(); add_heading(box, "%s — %s" % [room_name(room), difficulty.to_upper()]); add_text(box, MissionCatalog.guidance(room, difficulty))
	if room == "pc": build_pc_controls(box, difficulty)
	elif room == "lan": build_lan_controls(box, difficulty)
	elif room == "programming": build_program_controls(box, difficulty)
	else: build_tutorial_controls(box)
	add_button(box, I18n.t("mission.restart", "Restart mission"), func(): start_mission(room, difficulty), Color("895a43"))
	add_button(box, I18n.t("mission.hub", "Return to Hub"), enter_hub, Color("4d607d"))
	set_neutral_status(I18n.t("mission.started", "Mission started. Interact with the 3D equipment or panel controls."))

func build_pc_controls(box: VBoxContainer, difficulty: String) -> void:
	add_text(box, "Select a component, then its matching installation zone.")
	for component in pc_components(difficulty): add_button(box, "Pick: " + component, func(id=component): select_pc_component(id), Color("385b7c"))
	for slot in pc_slots(difficulty): add_button(box, "Install in: " + slot, func(id=slot): place_pc(id), Color("376b62"))
	if difficulty != "easy":
		for link in ["board_power","cpu_power"] + (["gpu_power"] if difficulty == "hard" else []): add_button(box, "Connect: " + link, func(id=link): pc_power(id), Color("a66c32"))
	add_button(box, "FINAL INSPECTION" if difficulty != "hard" else "SIMULATED BOOT", func(): pc_final(difficulty), palette.green)

func build_lan_controls(box: VBoxContainer, difficulty: String) -> void:
	add_text(box, "Select two endpoints to attach a simulated Ethernet cable.")
	var endpoints := ["pc1","switch","router"] if difficulty == "easy" else (["pc1","pc2","switch","router"] if difficulty == "normal" else ["pc1","pc2","pc3","switch","router"])
	for endpoint in endpoints: add_button(box, "Cable endpoint: " + endpoint.to_upper(), func(id=endpoint): select_network_endpoint(id), Color("375f7c"))
	if difficulty == "hard": add_button(box, "DIAGNOSE & CORRECT SEEDED FAULT", network_repair, Color("a66c32"))
	add_button(box, "VERIFY LINKS / SIMULATED PING", func(): network_final(difficulty), palette.green)

func build_program_controls(box: VBoxContainer, difficulty: String) -> void:
	add_text(box, "Build a command sequence. The interpreter calculates every move and checks collisions.")
	add_button(box, "+ FORWARD", func(): program.append({"op":"forward"}); update_program_status(), Color("385b7c"))
	add_button(box, "+ TURN LEFT", func(): program.append({"op":"left"}); update_program_status(), Color("385b7c"))
	add_button(box, "+ TURN RIGHT", func(): program.append({"op":"right"}); update_program_status(), Color("385b7c"))
	if difficulty != "easy": add_button(box, "+ REPEAT 4 × FORWARD", func(): program.append({"op":"repeat","count":4,"body":[{"op":"forward"}]}); update_program_status(), Color("71589b"))
	if difficulty == "hard": add_button(box, "+ CONDITIONAL ADAPTIVE STEP", func(): program.append(adaptive_step()); update_program_status(), Color("9b586e"))
	add_button(box, "REMOVE LAST", func(): if not program.is_empty(): program.pop_back(); update_program_status(), Color("895a43"))
	add_button(box, "CLEAR", func(): program.clear(); update_program_status(), Color("895a43"))
	add_button(box, "RUN PROGRAM", func(): run_program(difficulty), palette.green)

func build_tutorial_controls(box: VBoxContainer) -> void:
	add_text(box, "Perform each real control, then confirm the interaction. This compact station remains replayable.")
	for step in MissionCatalog.objectives("tutorial", "easy"):
		add_button(box, "Practice: " + step.replace("_", " "), func(id=step): tutorial_step(id), Color("55718c"))

func _on_interact(target: Interactable) -> void:
	var id := target.interaction_id
	if current_screen == "hub" and id.begins_with("door:"): show_difficulty(id.trim_prefix("door:")); return
	if current_screen != "mission": return
	if GameManager.current_room == "pc":
		if id.begins_with("component:"): select_pc_component(id.trim_prefix("component:"))
		elif id.begins_with("slot:"): place_pc(id.trim_prefix("slot:"))
		elif id.begins_with("power:"): pc_power(id.trim_prefix("power:"))
		elif id == "action:validate": pc_final(GameManager.difficulty)
	elif GameManager.current_room == "lan":
		if id.begins_with("endpoint:"): select_network_endpoint(id.trim_prefix("endpoint:"))
		elif id == "action:repair": network_repair()
		elif id == "action:validate": network_final(GameManager.difficulty)
	elif GameManager.current_room == "programming" and id == "action:validate": run_program(GameManager.difficulty)
	elif GameManager.current_room == "tutorial": tutorial_step(id.trim_prefix("tutorial:"))

func select_pc_component(id: String) -> void:
	selected_component=id; status_label.text="Holding %s. Choose its installation zone." % id

func place_pc(slot: String) -> void:
	if selected_component.is_empty(): feedback(false, "Pick a component first.", "pc:no_selection"); return
	var result := pc.install(selected_component, slot); feedback(result.ok, result.message, "pc:%s:%s" % [selected_component,slot])
	if result.ok: GameManager.complete_objective(slot); selected_component=""; refresh_progress()

func pc_power(link: String) -> void:
	var result := pc.connect_power(link); feedback(result.ok, result.message, "pc:"+link)
	if result.ok: GameManager.complete_objective(link); refresh_progress()

func pc_final(difficulty: String) -> void:
	var required := MissionCatalog.objectives("pc", difficulty)
	var result := pc.boot() if difficulty == "hard" else pc.inspect(required)
	feedback(result.ok, result.message, "pc:final")
	if result.ok:
		GameManager.complete_objective("boot" if difficulty == "hard" else "inspection"); finish_if_complete()

func select_network_endpoint(id: String) -> void:
	if selected_endpoint.is_empty(): selected_endpoint=id; status_label.text="First endpoint: %s. Choose the other end." % id.to_upper(); return
	var first := selected_endpoint; selected_endpoint=""; var result := network.connect_devices(first,id); feedback(result.ok,result.message,"lan:%s:%s" % [first,id])
	if result.ok:
		var endpoints := {first:true,id:true}; var objective := "switch-router" if endpoints.has("switch") and endpoints.has("router") else (("pc1-switch" if endpoints.has("pc1") else ("pc2-switch" if endpoints.has("pc2") else "pc3-switch")))
		GameManager.complete_objective(objective); refresh_progress()

func network_repair() -> void:
	var result := network.repair_fault(); feedback(true,result.message,"lan:repair"); GameManager.complete_objective("addresses"); GameManager.complete_objective("fault_fixed"); refresh_progress()

func network_final(difficulty: String) -> void:
	var devices: Array[String] = ["pc1"] if difficulty=="easy" else (["pc1","pc2"] if difficulty=="normal" else ["pc1","pc2","pc3"])
	var result := network.validate(devices); feedback(result.ok,result.message,"lan:validate")
	if result.ok:
		GameManager.complete_objective("link_check" if difficulty=="easy" else ("ping" if difficulty=="normal" else "ping_all")); GameManager.complete_objective("network_check"); finish_if_complete()

func update_program_status() -> void:
	status_label.text="Program (%d blocks): %s" % [program.size(), JSON.stringify(program)]

func run_program(difficulty: String) -> void:
	if program.is_empty(): feedback(false,"Program is empty.","program:empty"); return
	var scenarios := RobotInterpreter.scenarios(difficulty); var all_ok := true
	for index in scenarios.size():
		var result := robot.run(program, scenarios[index]); all_ok = all_ok and bool(result.ok)
		if result.ok: GameManager.complete_objective("scenario_a" if index==0 else "scenario_b")
		if result.used_repeat: GameManager.complete_objective("uses_repeat")
		if result.used_conditional: GameManager.complete_objective("uses_conditional")
		if result.ok: GameManager.complete_objective("goal")
		if result.error == "": GameManager.complete_objective("valid_program")
		status_label.text="Scenario %d: %s • position %s • %d steps" % [index+1, "PASS" if result.ok else result.error, result.position, result.steps]
	feedback(all_ok, "All required robot scenarios passed." if all_ok else status_label.text, "program:run")
	if all_ok: finish_if_complete()

func adaptive_step() -> Dictionary:
	# If blocked, walk a one-cell-wide detour and resume the original heading.
	return {"op":"if_obstacle","then":[{"op":"left"},{"op":"forward"},{"op":"right"},{"op":"forward"},{"op":"forward"},{"op":"right"},{"op":"forward"},{"op":"left"}],"else":[{"op":"forward"}]}

func tutorial_step(id: String) -> void:
	GameManager.complete_objective(id); status_label.text="Tutorial step completed: " + id.replace("_", " "); refresh_progress(); finish_if_complete()

func feedback(ok: bool, message: String, action_id: String) -> void:
	status_label.text = ("✓ " if ok else "✕ ") + message
	status_label.add_theme_color_override("font_color", palette.green if ok else palette.red)
	if ok: GameManager.clear_error_dedup(action_id)
	else: GameManager.count_error(action_id)

func refresh_progress() -> void:
	var done := 0
	for value in GameManager.completed_objectives.values(): if value: done += 1
	objective_label.text = "%s • %s • %d/%d" % [room_name(GameManager.current_room), GameManager.difficulty.to_upper(), done, GameManager.completed_objectives.size()]

func finish_if_complete() -> void:
	for value in GameManager.completed_objectives.values():
		if not value: refresh_progress(); return
	var result := GameManager.finish_mission(); show_results(result)

func show_results(result: Dictionary) -> void:
	current_screen="results"; player.enabled=false; Input.mouse_mode=Input.MOUSE_MODE_VISIBLE
	objective_label.text = "%s • COMPLETE • %d/100 • %d★" % [room_name(str(result.room)), int(result.score), int(result.stars)]
	var box:=clear_panel(); add_heading(box,I18n.t("results.title","Mission complete")); add_text(box,"Score: %d/100\nStars: %s\nActive time: %.2f s\nCounted errors: %d" % [result.score,"★".repeat(result.stars)+"☆".repeat(3-result.stars),result.active_seconds,result.error_count])
	add_button(box,I18n.t("results.replay","Replay"),func(): start_mission(result.room,result.difficulty),palette.green)
	add_button(box,I18n.t("results.difficulty","Change difficulty"),func(): show_difficulty(result.room),palette.blue)
	add_button(box,I18n.t("mission.hub","Return to Hub"),enter_hub,Color("4d607d"))

func show_progress() -> void:
	player.enabled=false; Input.mouse_mode=Input.MOUSE_MODE_VISIBLE; var box:=clear_panel(); add_heading(box,I18n.t("progress","Progress / results"))
	var profile: Dictionary = SaveManager.data.profiles.get(GameManager.profile_name,{})
	var attempts: Dictionary = profile.get("attempts",{})
	if attempts.is_empty(): add_text(box,I18n.t("progress.empty","No mission attempts saved yet."))
	for key in attempts:
		var entry: Dictionary=attempts[key]; add_text(box,"%s — attempts %d, best %d, %d★" % [key,entry.attempt_count,entry.best.score,entry.best.stars])
	add_button(box,I18n.t("back","Back to Hub"),enter_hub,Color("4d607d"))

func build_room(kind: String) -> void:
	interactive_nodes.clear()
	for child in world.get_children():
		if child.is_in_group("room_geometry"):
			child.free()
	var room := Node3D.new(); room.name="EnvironmentGeometry"; world.add_child(room)
	room.add_to_group("room_geometry")
	add_box(room,"Floor",Vector3(0,-0.1,0),Vector3(9,0.2,9),Color("d6dde0"),true)
	add_box(room,"BackWall",Vector3(0,2,-4.45),Vector3(9,4,0.15),Color("d9e8ef"),true)
	add_box(room,"LeftWall",Vector3(-4.45,2,0),Vector3(0.15,4,9),Color("e8f1f3"),true)
	add_box(room,"RightWall",Vector3(4.45,2,0),Vector3(0.15,4,9),Color("e8f1f3"),true)
	for x in [-2.8,0.0,2.8]:
		var light:=OmniLight3D.new();light.position=Vector3(x,3.4,0);light.light_color=Color("e4f4ff");light.omni_range=5.5;light.light_energy=0.8;room.add_child(light)
	if kind=="hub": build_hub_geometry(room)
	elif kind=="pc": build_pc_geometry(room)
	elif kind=="lan": build_lan_geometry(room)
	elif kind=="programming": build_program_geometry(room)
	else: build_tutorial_geometry(room)

func build_hub_geometry(room: Node3D) -> void:
	add_box(room,"Reception",Vector3(0,0.55,-2.8),Vector3(3.2,1.1,0.7),palette.wood,false)
	make_interactable(room,"door:pc","PC Assembly",Vector3(-2.7,1.2,-4.25),Vector3(1.6,2.4,0.25),palette.blue)
	make_interactable(room,"door:lan","LAN Networking",Vector3(0,1.2,-4.25),Vector3(1.6,2.4,0.25),palette.green)
	make_interactable(room,"door:programming","Programming",Vector3(2.7,1.2,-4.25),Vector3(1.6,2.4,0.25),Color("8b67c9"))
	make_interactable(room,"door:tutorial","Tutorial",Vector3(-3.8,0.8,2.4),Vector3(0.5,1.6,1.2),Color("ca8b3c"))

func build_pc_geometry(room: Node3D) -> void:
	add_box(room,"Workbench",Vector3(0,0.65,-1.3),Vector3(5.8,0.25,2.0),palette.wood,false)
	add_box(room,"Case",Vector3(2.0,1.25,-1.3),Vector3(1.3,1.5,1.3),Color("253244"),false)
	var components:=pc_components(GameManager.difficulty); for index in components.size(): make_interactable(room,"component:"+components[index],components[index],Vector3(-2.4+index%3*0.75,1.0,-0.9+index/3*0.75),Vector3(0.48,0.16,0.48),Color.from_hsv(float(index)/maxf(1,components.size()),0.55,0.85))
	var slots:=pc_slots(GameManager.difficulty); for index in slots.size(): make_interactable(room,"slot:"+slots[index],slots[index]+" slot",Vector3(1.75+(index%2)*0.45,1.3,-1.55+(index/2)*0.35),Vector3(0.32,0.08,0.25),Color("4ba3b5"))
	make_interactable(room,"action:validate","Inspection / Boot",Vector3(0,1.3,-3.7),Vector3(1.6,0.8,0.25),palette.green)

func build_lan_geometry(room: Node3D) -> void:
	var devices:=["pc1","switch","router"] if GameManager.difficulty=="easy" else (["pc1","pc2","switch","router"] if GameManager.difficulty=="normal" else ["pc1","pc2","pc3","switch","router"])
	for index in devices.size():
		var pos:=Vector3(-3.0+index*1.5,0.9,-1.0+(index%2)*1.5); make_interactable(room,"endpoint:"+devices[index],devices[index].to_upper()+" Ethernet port",pos,Vector3(1.0,1.1,0.65),palette.blue if devices[index].begins_with("pc") else palette.green)
	make_interactable(room,"action:validate","Network tester / Ping",Vector3(0,1.3,-3.7),Vector3(1.8,0.8,0.25),palette.green)
	if GameManager.difficulty=="hard": make_interactable(room,"action:repair","Fault diagnostics",Vector3(2.8,1.2,-3.7),Vector3(1.4,0.7,0.25),Color("a66c32"))

func build_program_geometry(room: Node3D) -> void:
	add_box(room,"Arena",Vector3(0,0.05,-0.8),Vector3(5.5,0.1,5.5),Color("39536b"),false)
	for x in 6: for z in 6: add_box(room,"Grid",Vector3(-2.1+x*0.84,0.12,-2.9+z*0.84),Vector3(0.75,0.04,0.75),Color("5f8293") if (x+z)%2==0 else Color("496b7d"),false)
	add_box(room,"RobotBody",Vector3(-2.1,0.42,1.3),Vector3(0.55,0.55,0.55),Color("f1b94e"),false)
	add_box(room,"RobotHead",Vector3(-2.1,0.82,1.3),Vector3(0.42,0.28,0.42),Color("f4d178"),false)
	make_interactable(room,"action:validate","RUN robot program",Vector3(2.8,1.2,-3.7),Vector3(1.7,0.8,0.25),palette.green)

func build_tutorial_geometry(room: Node3D) -> void:
	for index in MissionCatalog.objectives("tutorial","easy").size():
		var id:=MissionCatalog.objectives("tutorial","easy")[index]; make_interactable(room,"tutorial:"+id,id.replace("_"," "),Vector3(-3.4+(index%4)*2.2,0.45,-2.7+(index/4)*2.1),Vector3(1.2,0.75,1.0),Color.from_hsv(float(index)/12.0,0.5,0.82))

func add_box(parent: Node3D, node_name: String, position: Vector3, size: Vector3, color: Color, collision: bool) -> Node3D:
	var holder:=StaticBody3D.new() if collision else Node3D.new();holder.name=node_name;holder.position=position;parent.add_child(holder)
	var mesh_instance:=MeshInstance3D.new();var mesh:=BoxMesh.new();mesh.size=size;var material:=StandardMaterial3D.new();material.albedo_color=color;material.roughness=0.7;mesh.material=material;mesh_instance.mesh=mesh;holder.add_child(mesh_instance)
	if collision:
		var shape_node:=CollisionShape3D.new();var shape:=BoxShape3D.new();shape.size=size;shape_node.shape=shape;holder.add_child(shape_node)
	return holder

func make_interactable(parent: Node3D,id:String,text:String,position:Vector3,size:Vector3,color:Color)->Interactable:
	var item:=Interactable.create(id,text,size,color);item.position=position;parent.add_child(item);interactive_nodes.append(item);return item

func pc_components(difficulty:String)->Array[String]:
	if difficulty=="easy": return ["ram_d4","ssd","gpu"]
	if difficulty=="normal": return ["cpu_amber","cooler_a","ram_d4","ssd","gpu"]
	return ["cpu_amber","cpu_blue","cooler_a","cooler_b","ram_d4","ram_d5","ssd","gpu","psu_450","psu_650"]

func pc_slots(difficulty:String)->Array[String]:
	if difficulty=="easy": return ["ram","ssd","gpu"]
	if difficulty=="normal": return ["cpu","cooler","ram","ssd","gpu"]
	return ["cpu","cooler","ram","ssd","gpu","psu"]

func room_name(room:String)->String:
	return {"pc":"PC Assembly Laboratory","lan":"LAN Networking Laboratory","programming":"Programming & Robotics Laboratory","tutorial":"Control Tutorial"}.get(room,room)

func guidance_name(level:String)->String:
	return {"easy":"guided step by step","normal":"partial guidance","hard":"independent diagnosis"}[level]

func set_neutral_status(text: String) -> void:
	status_label.text = text
	status_label.add_theme_color_override("font_color", Color("ffd166"))

func reset_desktop_view() -> void:
	player.position = Vector3(0,0.2,5)
	player.velocity = Vector3.ZERO
	player.rotation = Vector3.ZERO
	player.look_at(Vector3(0,0,0), Vector3.UP)
	player.camera.rotation = Vector3.ZERO

func _on_target_changed(label:String)->void:
	reticle.text="+" if label.is_empty() else "[E] "+label
