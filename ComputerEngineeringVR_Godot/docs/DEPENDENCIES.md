# Dependencies

Target engine: Godot Engine 4.7.2 stable (`ed1daf0bf`), standard build, GDScript, Compatibility renderer. Runtime XR API: Godot's built-in OpenXR interface with SteamVR as the intended Windows runtime. Godot XR Tools is not vendored: this implementation uses native nodes and avoids adding an unverified addon dependency. Windows export requires the exact Godot 4.7.2 stable export templates.

Development-only static validation supports Python 3.10+ with no packages. The shipped game has no Python or Blender dependency. The environment audited on 2026-10-27 had Python 3.14 and a standalone Godot 4.7.2 binary outside PATH; Blender was unavailable.

