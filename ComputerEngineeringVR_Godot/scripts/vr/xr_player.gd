class_name XRPlayer
extends XROrigin3D

signal xr_status(message: String)
var camera: XRCamera3D
var left: XRController3D
var right: XRController3D

func _ready() -> void:
	camera = XRCamera3D.new(); add_child(camera)
	left = _make_hand("LeftHand", "left_hand")
	right = _make_hand("RightHand", "right_hand")
	var interface := XRServer.find_interface("OpenXR")
	if interface and interface.is_initialized():
		get_viewport().use_xr = true
		xr_status.emit("OpenXR session active")
	elif interface and interface.initialize():
		get_viewport().use_xr = true
		xr_status.emit("OpenXR initialized")
	else:
		xr_status.emit("OpenXR unavailable — Desktop Mode remains available")

func _make_hand(node_name: String, tracker: String) -> XRController3D:
	var hand := XRController3D.new(); hand.name = node_name; hand.tracker = tracker; add_child(hand)
	var mesh_instance := MeshInstance3D.new(); var mesh := CapsuleMesh.new(); mesh.radius = 0.035; mesh.height = 0.15
	var material := StandardMaterial3D.new(); material.albedo_color = Color(0.12, 0.65, 0.92); mesh.material = material
	mesh_instance.mesh = mesh; mesh_instance.rotation.x = PI / 2.0; hand.add_child(mesh_instance)
	var ray := RayCast3D.new(); ray.name = "InteractionRay"; ray.target_position = Vector3(0, 0, -8); ray.enabled = true; hand.add_child(ray)
	return hand

func recenter() -> void:
	XRServer.center_on_hmd(XRServer.RESET_BUT_KEEP_TILT, true)

