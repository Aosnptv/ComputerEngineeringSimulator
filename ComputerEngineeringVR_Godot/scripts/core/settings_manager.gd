extends Node

var values := {"graphics": "medium", "move_speed": 3.0, "snap_turn": 45, "seated": false, "height_offset": 0.0, "voice_volume": 0.8, "voice_muted": false, "subtitles": true}

func apply_graphics(preset: String) -> void:
	values.graphics = preset if preset in ["low", "medium", "high"] else "medium"
	var viewport := get_viewport()
	viewport.msaa_3d = Viewport.MSAA_DISABLED if values.graphics == "low" else (Viewport.MSAA_2X if values.graphics == "medium" else Viewport.MSAA_4X)
	viewport.scaling_3d_scale = 0.8 if values.graphics == "low" else (1.0 if values.graphics == "medium" else 1.15)

