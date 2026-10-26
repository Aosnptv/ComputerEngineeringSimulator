# Validation — 2026-10-27

- `python tests/validate_project.py`: PASS — 9 required resources, 12 resource references, 9 mission configurations.
- `python -m unittest discover -s tests -v`: PASS — 4 tests.
- Godot 4.7.2 `--headless --path . --editor --quit`: PASS — scripts imported after two parser fixes.
- Godot 4.7.2 `--headless --xr-mode off --path . --script tests/headless_suite.gd`: PASS — 9/9 mission logic paths.
- Main scene headless startup: PASS with Desktop fallback; no gameplay crash.
- Windows export: PASS after installing the official matching 4.7.2 Windows templates.
- Full build script: PASS after replacing the unavailable PowerShell archive module with `tar.exe` ZIP packaging.
- ZIP clean extraction and hidden executable smoke launch: PASS, exit code 0.
- Live packaged-app visual QA: PASS for language/profile/mode flow, Main Hub stability, and PC Easy room rendering. Visual QA found and fixed a non-current camera and floor-tunnelling spawn before the final build.
- Final ZIP: 38,043,306 bytes (36.28 MiB), SHA-256 `A1728F2C6501059247F2D30D18E153306511A01B250816F55A250B20DA5F2D8D`.

No physical-headset mission playthrough, complete nine-mission manual desktop playthrough, performance measurement, or narration listening test was performed.
