class_name DesktopPlayer
extends CharacterBody3D

signal target_changed(label: String)
signal interaction_requested(target: Interactable)
var camera: Camera3D
var ray: RayCast3D
var enabled := true
var mouse_sensitivity := 0.0022

func _ready() -> void:
	camera = Camera3D.new(); camera.position.y = 1.65; camera.current = true; add_child(camera)
	ray = RayCast3D.new(); ray.target_position = Vector3(0, 0, -4.0); ray.collide_with_areas = true; camera.add_child(ray)
	Input.mouse_mode = Input.MOUSE_MODE_CAPTURED

func _unhandled_input(event: InputEvent) -> void:
	if not enabled: return
	if event is InputEventMouseMotion and Input.mouse_mode == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotation.x = clampf(camera.rotation.x - event.relative.y * mouse_sensitivity, -1.35, 1.35)
	if event.is_action_pressed("interact"):
		var target := ray.get_collider() as Interactable
		if target: interaction_requested.emit(target)
	if event.is_action_pressed("menu_toggle"):
		Input.mouse_mode = Input.MOUSE_MODE_VISIBLE if Input.mouse_mode == Input.MOUSE_MODE_CAPTURED else Input.MOUSE_MODE_CAPTURED

func _physics_process(_delta: float) -> void:
	if not enabled: return
	var input := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var direction := (transform.basis * Vector3(input.x, 0, input.y)).normalized()
	velocity.x = direction.x * float(SettingsManager.values.move_speed)
	velocity.z = direction.z * float(SettingsManager.values.move_speed)
	# Desktop classrooms are single-level. Pin eye-rig height to prevent spawn-edge
	# tunnelling while retaining horizontal CharacterBody wall collisions.
	velocity.y = 0.0
	move_and_slide()
	position.y = 0.2
	var collider := ray.get_collider() as Interactable
	target_changed.emit(str(collider.label) if collider else "")

