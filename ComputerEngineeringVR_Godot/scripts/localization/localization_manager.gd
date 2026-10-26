extends Node

signal language_changed(language: String)
var language := "en"
var catalog: Dictionary = {}

func _ready() -> void:
	var parsed = JSON.parse_string(FileAccess.get_file_as_string("res://data/localization/catalog.json"))
	if parsed is Dictionary: catalog = parsed

func set_language(value: String) -> void:
	language = value if value in ["en", "th"] else "en"
	language_changed.emit(language)

func t(key: String, fallback := "") -> String:
	return str(catalog.get(language, {}).get(key, fallback if not fallback.is_empty() else key))
