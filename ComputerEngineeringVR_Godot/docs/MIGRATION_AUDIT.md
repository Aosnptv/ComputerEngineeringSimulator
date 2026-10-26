# Migration audit

Audit date: 2026-10-27. Source branch at audit: `feature/core-pc-assembly-integration`; rebuild branch: `feature/godot4-vr-complete-rebuild`.

The original `ComputerEngineeringVR`, `pc_assembly_room`, `LAN_Room_3D - D`, `programming_room`, and `MainVrGameCPE-main` trees remain intact. The legacy suite is a single Panda3D desktop host with room adapters. It contains useful domain rules, Thai/English strings, a Thai-capable Prompt font in the LAN room, and reference screenshots. Its Python scene objects, DirectGUI, collision handlers, and optional Python VR probe cannot be reused in Godot at runtime.

Concepts preserved: compact pale-blue/wood classroom palette; recognizable component stations; compatibility feedback; LAN preparation and IP concepts; grid robot missions; bilingual terminology; safe desktop fallback. Reimplemented natively: scene lifecycle, player/camera, interaction targets, mission state, scoring, persistence, OpenXR origin/controllers, UI, graph reachability, and robot interpretation.

Known legacy limitations include session-only progress, PC modes named easy/medium rather than the required three levels, no unified OpenXR controls, and no distributable Godot build. There is no repository-level license. Existing images and Prompt-Regular.ttf therefore remain references and are not copied into the distributable until provenance is resolved. New visuals use only procedural Godot geometry and colors.

