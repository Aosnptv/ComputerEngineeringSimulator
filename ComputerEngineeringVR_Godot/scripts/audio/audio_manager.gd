class_name AudioManager
extends Node

signal subtitle_requested(text: String)
var player: AudioStreamPlayer
var manifest: Dictionary = {}

func _ready() -> void:
	player = AudioStreamPlayer.new(); add_child(player)
	var parsed = JSON.parse_string(FileAccess.get_file_as_string("res://data/audio/voice_manifest.json"))
	if parsed is Dictionary: manifest = parsed

func play_event(event_id: String) -> void:
	if not manifest.has(event_id): return
	var item: Dictionary = manifest[event_id]
	if SettingsManager.values.subtitles: subtitle_requested.emit(str(item.get(I18n.language + "_subtitle", item.get("en_subtitle", ""))))
	if SettingsManager.values.voice_muted: return
	var path := str(item.get("audio", ""))
	if path.is_empty() or not ResourceLoader.exists(path): return
	player.stop(); player.stream = load(path); player.volume_db = linear_to_db(float(SettingsManager.values.voice_volume)); player.play()

