# Computer Engineering Simulator

An integrated Panda3D learning game for Windows. One application and one
`ShowBase` host the Main Hub and the original PC Assembly, LAN Networking, and
Programming experiences.

## Run on Windows

Double-click `run.bat`. The launcher resolves all paths from its own location,
checks for 64-bit Python 3.12 and Panda3D 1.10.16, and then starts
`ComputerEngineeringVR/src/main.py`. It never installs packages automatically.

The verified development environment is external to this repository:

```text
%LOCALAPPDATA%\venvs\ComputerEngineeringSimulator-py312
```

To request optional VR readiness checks, double-click `run_vr.bat`. Desktop is
always the safe default. The current adapter reports runtime/backend/headset
availability and falls back to desktop; it does not claim a verified headset
session when the required Python OpenXR backend or HMD is absent.

## Controls

- `W A S D`: move in 3D rooms
- Mouse / right-drag where shown: look around
- Left click or `E`: interact
- `R`: reset the active activity where supported
- `Tab`: PC Assembly navigation overlay
- `Esc`: pause menu (Resume, Restart Room, Main Hub, Main Menu, Settings, Quit)

## Integrated experiences

- **PC Assembly:** original component placement, validation, easy/medium
  difficulty, elapsed time, mistakes, and 1–3 stars.
- **LAN Networking:** the original nine-station workflow including equipment,
  UTP preparation, T568A/T568B wire order, RJ45 crimping, cable test, topology,
  IP/ping checks, difficulty, elapsed time, and 1–3 stars.
- **Programming:** the original classroom, block editor, constrained Python/C
  fill-ins, conditional puzzles, and robot missions. User text is parsed against
  an allow-list and is never passed to `exec` or `eval`.

Progress is session-only. The integrated game does not write score/progress
files.

## Tests

With the verified interpreter:

```powershell
$env:PYTHONDONTWRITEBYTECODE = "1"
& "$env:LOCALAPPDATA\venvs\ComputerEngineeringSimulator-py312\Scripts\python.exe" -m unittest discover -s tests -v
```

GUI behavior must still be checked in the real WGL window; an offscreen smoke
test cannot prove usability, mouse capture, visual layout, or headset behavior.

## Repository notes

- `ComputerEngineeringVR/.venv` is a tracked legacy environment and may contain
  machine-specific paths. It is not used by the launcher. Removing it from Git
  history/index requires separate approval.
- No license file is currently present, so no open-source license is implied.
- Optional SteamVR/OpenXR Python dependencies are intentionally not installed
  without explicit approval.

