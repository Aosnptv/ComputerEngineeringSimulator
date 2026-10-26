# Computer Engineering VR Simulator — Godot 4 rebuild

This independent Godot 4 project preserves the legacy Panda3D projects beside it. It provides one bilingual application with a Main Hub, control tutorial, PC Assembly, LAN Networking, and Programming & Robotics laboratories. Each lab exposes Easy, Normal, and Hard missions through shared Desktop/OpenXR gameplay state.

## Run

Install Godot 4.7.2 stable, open this directory, and run `project.godot`. Desktop controls are WASD, `Esc` to capture/release mouse look, `E`/left click to interact, and `H` for hints. For PCVR, start SteamVR as the active OpenXR runtime before choosing VR mode.

Static checks without Godot:

```powershell
python tests/validate_project.py
python -m unittest discover -s tests -v
```

Windows release (requires Godot 4.3 and matching export templates on `PATH`):

```powershell
tools\build_windows.bat
```

See [ACCEPTANCE_REPORT.md](docs/ACCEPTANCE_REPORT.md) for verified status and honest hardware/runtime limitations.

