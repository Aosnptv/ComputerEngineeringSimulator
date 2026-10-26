# Architecture

`GameManager` owns deterministic lifecycle state and one active mission. `SaveManager`, `I18n`, and `SettingsManager` are autoloads. `MissionCatalog` supplies objectives; `PCValidator`, `NetworkModel`, and `RobotInterpreter` are engine-independent domain services. `ScoreManager` implements the common 70/20/10 policy. `main.gd` composes procedural classroom scenes and connects both 3D and panel interactions to the same services.

DesktopPlayer uses a CharacterBody3D, tracked camera ray, collision, and shared interaction IDs. XRPlayer owns one persistent XROrigin3D, XRCamera3D, two tracked controllers, and controller rays; head orientation is never driven by mouse look. Room rebuilds clear old geometry and interaction registrations before adding the next room. Mission state is reset exactly once on start/restart.

State transitions are STARTUP → HUB → BRIEFING/ACTIVE → PAUSED/COMPLETED → HUB or RESETTING. Scoring completion is gated by every mandatory objective, never by score or a final-button click alone.

