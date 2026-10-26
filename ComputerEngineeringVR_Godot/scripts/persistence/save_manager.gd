extends Node

const SAVE_PATH := "user://progress_v1.json"
const BACKUP_PATH := "user://progress_v1.backup.json"
const SCHEMA := 1
var data := {"schema": SCHEMA, "profiles": {}}

func _ready() -> void:
	load_data()

func ensure_profile(name: String) -> void:
	var safe := name.strip_edges().substr(0, 24)
	if safe.is_empty(): safe = "Student"
	if not data.profiles.has(safe):
		data.profiles[safe] = {"tutorial_complete": false, "attempts": {}, "history": [], "settings": {}}
	GameManager.profile_name = safe
	save_data()

func record_result(result: Dictionary) -> void:
	ensure_profile(str(result.get("profile", "Student")))
	var profile: Dictionary = data.profiles[GameManager.profile_name]
	var key := "%s/%s" % [result.room, result.difficulty]
	var entry: Dictionary = profile.attempts.get(key, {"attempt_count": 0, "best": {}})
	entry.attempt_count = int(entry.attempt_count) + 1
	if entry.best.is_empty() or int(result.score) > int(entry.best.get("score", -1)):
		entry.best = result.duplicate(true)
	entry.latest = result.duplicate(true)
	profile.attempts[key] = entry
	profile.history.append(result.duplicate(true))
	if profile.history.size() > 100: profile.history.pop_front()
	save_data()

func save_data() -> bool:
	var payload := JSON.stringify(data, "  ")
	if FileAccess.file_exists(SAVE_PATH):
		var old := FileAccess.get_file_as_string(SAVE_PATH)
		var backup := FileAccess.open(BACKUP_PATH, FileAccess.WRITE)
		if backup: backup.store_string(old)
	var temp_path := SAVE_PATH + ".tmp"
	var file := FileAccess.open(temp_path, FileAccess.WRITE)
	if not file: return false
	file.store_string(payload)
	file.close()
	DirAccess.remove_absolute(SAVE_PATH)
	return DirAccess.rename_absolute(temp_path, SAVE_PATH) == OK

func load_data() -> void:
	for path in [SAVE_PATH, BACKUP_PATH]:
		if not FileAccess.file_exists(path): continue
		var parsed = JSON.parse_string(FileAccess.get_file_as_string(path))
		if parsed is Dictionary and int(parsed.get("schema", 0)) == SCHEMA and parsed.get("profiles", null) is Dictionary:
			data = parsed
			return
	data = {"schema": SCHEMA, "profiles": {}}

