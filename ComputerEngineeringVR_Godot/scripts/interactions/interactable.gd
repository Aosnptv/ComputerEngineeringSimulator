class_name Interactable
extends StaticBody3D

signal activated(id: String)
@export var interaction_id := ""
@export var label := "Interact"
@export var mission_tags: Array[String] = []
var base_material: StandardMaterial3D
var highlighted := false

func activate() -> void:
	activated.emit(interaction_id)

func set_highlight(value: bool) -> void:
	highlighted = value
	if base_material:
		base_material.emission_enabled = value
		base_material.emission = Color(0.1, 0.65, 1.0) if value else Color.BLACK
		base_material.emission_energy_multiplier = 0.7 if value else 0.0

static func create(id: String, text: String, size: Vector3, color: Color) -> Interactable:
	var body := Interactable.new()
	body.interaction_id = id; body.label = text
	var mesh_instance := MeshInstance3D.new()
	var mesh := BoxMesh.new(); mesh.size = size
	var material := StandardMaterial3D.new(); material.albedo_color = color; material.roughness = 0.65
	mesh.material = material; mesh_instance.mesh = mesh; body.base_material = material
	body.add_child(mesh_instance)
	var collision := CollisionShape3D.new(); var shape := BoxShape3D.new(); shape.size = size; collision.shape = shape; body.add_child(collision)
	body.set_meta("label", text)
	return body

