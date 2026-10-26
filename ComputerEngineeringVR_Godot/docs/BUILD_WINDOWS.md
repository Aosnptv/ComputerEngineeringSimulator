# Windows build

Install Godot 4.7.2 stable and its matching Windows export templates. Add `godot.exe` as `godot` (or `godot4`) on PATH, or set `GODOT_EXE` to its full path. From this directory run `tools\build_windows.bat`.

The script validates content, performs a headless import, exports `builds/windows/ComputerEngineeringVR.exe` plus PCK, stages README/license material, and creates `builds/ComputerEngineeringVR-Windows-x64.zip`. Any validation/import/export/missing-output error returns nonzero. The 2026-10-27 artifact was extracted to a clean directory, launched outside the editor, and visibly exercised through Main Hub and PC Easy.

