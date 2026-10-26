# Audio assets

`data/audio/voice_manifest.json` defines Thai narration paths and bilingual subtitles for welcome, tutorial, room introductions, correct/incorrect feedback, and completion. `AudioManager` prevents overlap by stopping the previous clip, honors voice volume/mute, and emits subtitles.

No offline Thai TTS engine or verified recordings were available. The referenced OGG files are intentionally absent; no silence is presented as narration. Record or synthesize the manifest text with a licensed Thai voice, normalize to consistent loudness, export mono OGG files at the listed paths, and listen-check every clip before changing AC-20 from incomplete.

