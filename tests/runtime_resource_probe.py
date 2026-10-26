"""Repeatable native-window transition probe for Panda3D resource growth.

Run from the repository root with bytecode disabled, for example::

    python -B tests/runtime_resource_probe.py --scenario pc --cycles 10 \
        --output reports/beta_readiness/resource-pc-10.json

This is a diagnostic helper, not a unit test.  It exercises the real room
lifecycle, cursor/window handling and renderer without simulating a successful
playthrough.  The small native window is positioned outside the visible desktop.
"""

from __future__ import annotations

import argparse
import ctypes
import gc
import json
import sys
import time
from pathlib import Path

import psutil
from panda3d.core import loadPrcFileData
from panda3d.core import AmbientLight, AntialiasAttrib, DirectionalLight, PointLight


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "ComputerEngineeringVR" / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

loadPrcFileData(
    "resource-probe",
    "\n".join(
        (
            "window-type onscreen",
            "win-size 640 360",
            "win-origin -32000 -32000",
            "audio-library-name null",
            "sync-video false",
            "show-frame-rate-meter false",
            "notify-level warning",
        )
    ),
)

from direct.showbase.MessengerGlobal import messenger
from main import ComputerEngineeringApp
from rooms.main_hub import MainHub
from pc_assembly_room.pc_assembly_room import scene3d as pc_scene3d


def _prepared_counts(app):
    prepared = app.win.getGsg().getPreparedObjects()
    return {
        "total": prepared.getNumPrepared(),
        "geoms": prepared.getNumPreparedGeoms(),
        "textures": prepared.getNumPreparedTextures(),
        "vertex_buffers": prepared.getNumPreparedVertexBuffers(),
        "index_buffers": prepared.getNumPreparedIndexBuffers(),
        "shaders": prepared.getNumPreparedShaders(),
    }


def _event_counts():
    callbacks = getattr(messenger, "_Messenger__callbacks", {})
    listeners = 0
    for value in callbacks.values():
        try:
            listeners += len(value)
        except TypeError:
            listeners += 1
    return {"events": len(callbacks), "listeners": listeners}


def _snapshot(app, label):
    process = psutil.Process()
    memory = process.memory_info()
    full = process.memory_full_info()
    get_current_process = ctypes.windll.kernel32.GetCurrentProcess
    get_current_process.restype = ctypes.c_void_p
    get_gui_resources = ctypes.windll.user32.GetGuiResources
    get_gui_resources.argtypes = (ctypes.c_void_p, ctypes.c_uint)
    get_gui_resources.restype = ctypes.c_uint
    process_handle = get_current_process()
    gdi_handles = get_gui_resources(process_handle, 0)
    user_handles = get_gui_resources(process_handle, 1)
    total_handles = process.num_handles()
    return {
        "label": label,
        "private_bytes": getattr(full, "private", None),
        "working_set_bytes": memory.rss,
        "handles": total_handles,
        "gdi_handles": gdi_handles,
        "user_handles": user_handles,
        "other_handles": total_handles - gdi_handles - user_handles,
        "tasks": len(app.taskMgr.getTasks()),
        **_event_counts(),
        "render_descendants": app.render.findAllMatches("**").getNumPaths(),
        "aspect2d_descendants": app.aspect2d.findAllMatches("**").getNumPaths(),
        "prepared": _prepared_counts(app),
    }


def _frames(app, count):
    started = time.perf_counter()
    for _ in range(count):
        app.taskMgr.step()
        app.graphicsEngine.renderFrame()
    elapsed = time.perf_counter() - started
    return count / elapsed if elapsed else None


def _configure_hub_variant(variant):
    if variant == "all":
        return
    if variant in {
        "no_ui", "no_ui_no_world_text", "empty", "environment_only",
        "lit_environment", "lighting_only", "stations_only", "robot_only",
        "shared_lighting",
    }:
        MainHub.create_ui = lambda self: None
        MainHub.update_nearby = lambda self: None
    if variant in {"no_ui_no_world_text", "environment_only"}:
        original_build_environment = MainHub.build_environment

        def build_environment_without_text(self):
            original_build_environment(self)
            for node in self.root.findAllMatches("**/+TextNode"):
                node.removeNode()

        MainHub.build_environment = build_environment_without_text
    if variant == "environment_only":
        MainHub.build_lighting = lambda self: None
        MainHub.build_stations = lambda self: None
        MainHub.build_robot = lambda self: None
        MainHub.update = lambda self, task: task.cont
    if variant == "lit_environment":
        original_build_environment = MainHub.build_environment

        def build_lit_environment_without_text(self):
            original_build_environment(self)
            for node in self.root.findAllMatches("**/+TextNode"):
                node.removeNode()

        MainHub.build_environment = build_lit_environment_without_text
        MainHub.build_stations = lambda self: None
        MainHub.build_robot = lambda self: None
        MainHub.update = lambda self, task: task.cont
    if variant == "lighting_only":
        MainHub.build_environment = lambda self: None
        MainHub.build_stations = lambda self: None
        MainHub.build_robot = lambda self: None
        MainHub.update = lambda self, task: task.cont
    if variant == "stations_only":
        MainHub.build_lighting = lambda self: None
        MainHub.build_environment = lambda self: None
        MainHub.build_robot = lambda self: None
        MainHub.update = lambda self, task: task.cont
    if variant == "robot_only":
        MainHub.build_lighting = lambda self: None
        MainHub.build_environment = lambda self: None
        MainHub.build_stations = lambda self: None
    if variant == "shared_lighting":
        original_build_environment = MainHub.build_environment

        def build_environment_without_text(self):
            original_build_environment(self)
            for node in self.root.findAllMatches("**/+TextNode"):
                node.removeNode()

        def build_shared_lighting(self):
            self.root.setAntialias(AntialiasAttrib.MAuto)
            nodes = getattr(self.app, "_resource_probe_hub_lights", None)
            if nodes is None:
                owner = self.app.render.attachNewNode("probe_shared_hub_lights")
                ambient = AmbientLight("soft_ambient")
                ambient.setColor((0.42, 0.51, 0.64, 1))
                ambient_node = owner.attachNewNode(ambient)
                sun = DirectionalLight("lab_key_light")
                sun.setColor((0.48, 0.56, 0.67, 1))
                sun_node = owner.attachNewNode(sun)
                sun_node.setHpr(-35, -55, 0)
                nodes = (ambient_node, sun_node)
                self.app._resource_probe_hub_lights = nodes
            for node in nodes:
                self.root.setLight(node)

        MainHub.build_environment = build_environment_without_text
        MainHub.build_lighting = build_shared_lighting
    if variant == "empty":
        MainHub.build_lighting = lambda self: None
        MainHub.build_environment = lambda self: None
        MainHub.build_stations = lambda self: None
        MainHub.build_robot = lambda self: None
        MainHub.update = lambda self, task: task.cont


def _configure_pc_variant(variant, app):
    if variant == "all":
        return
    if variant == "shared_lights":
        def setup_shared_lights(root, render):
            nodes = getattr(app, "_resource_probe_pc_lights", None)
            if nodes is None:
                owner = render.attachNewNode("probe_shared_pc_lights")
                ambient = AmbientLight("lab_ambient")
                ambient.setColor((.55, .57, .62, 1))
                nodes = [owner.attachNewNode(ambient)]
                for name, heading, pitch, color in (
                    ("key", -35, -65, (.70, .68, .64, 1)),
                    ("fill", 140, -35, (.28, .34, .42, 1)),
                ):
                    light = DirectionalLight(name)
                    light.setColor(color)
                    node = owner.attachNewNode(light)
                    node.setHpr(heading, pitch, 0)
                    nodes.append(node)
                for x in (-3.1, 3.1):
                    light = PointLight("blue_accent")
                    light.setColor((.015, .10, .30, 1))
                    light.setAttenuation((1, 0, .8))
                    node = owner.attachNewNode(light)
                    node.setPos(x, 4.5, 1)
                    nodes.append(node)
                app._resource_probe_pc_lights = tuple(nodes)
            for node in nodes:
                root.setLight(node)

        pc_scene3d.setup_lights = setup_shared_lights


def run(scenario, cycles, frames_per_state, hub_variant="all", pc_variant="all"):
    _configure_hub_variant(hub_variant)
    app = ComputerEngineeringApp()
    try:
        _configure_pc_variant(pc_variant, app)
        app.intro.finish()
        app.language_screen.select("en")
        _frames(app, frames_per_state)
        samples = [_snapshot(app, "baseline.hub")]
        frame_rates = []

        for cycle in range(1, cycles + 1):
            if scenario == "hub":
                app.scene_manager.close_active()
                if not app.scene_manager.go_to("hub"):
                    raise RuntimeError(f"Hub recreation failed in cycle {cycle}")
                frame_rates.append(_frames(app, frames_per_state))
                gc.collect()
                samples.append(_snapshot(app, f"cycle.{cycle}.hub"))
                continue
            if not app.scene_manager.go_to("pc_assembly"):
                raise RuntimeError(f"PC Assembly activation failed in cycle {cycle}")
            if scenario == "pc":
                app.scene_manager.active_room._start("easy")
                if app.scene_manager.active_room.room is None:
                    raise RuntimeError(f"PC gameplay failed to start in cycle {cycle}")
            frame_rates.append(_frames(app, frames_per_state))
            if not app.scene_manager.go_to("hub"):
                raise RuntimeError(f"Hub activation failed in cycle {cycle}")
            _frames(app, frames_per_state)
            gc.collect()
            samples.append(_snapshot(app, f"cycle.{cycle}.hub"))

        first, last = samples[0], samples[-1]
        return {
            "scenario": scenario,
            "hub_variant": hub_variant,
            "pc_variant": pc_variant,
            "cycles": cycles,
            "frames_per_state": frames_per_state,
            "python": sys.version,
            "renderer": app.win.getGsg().getDriverRenderer(),
            "vendor": app.win.getGsg().getDriverVendor(),
            "average_probe_fps": sum(frame_rates) / len(frame_rates),
            "samples": samples,
            "delta": {
                "private_bytes": last["private_bytes"] - first["private_bytes"],
                "working_set_bytes": last["working_set_bytes"] - first["working_set_bytes"],
                "handles": last["handles"] - first["handles"],
                "gdi_handles": last["gdi_handles"] - first["gdi_handles"],
                "user_handles": last["user_handles"] - first["user_handles"],
                "other_handles": last["other_handles"] - first["other_handles"],
                "tasks": last["tasks"] - first["tasks"],
                "events": last["events"] - first["events"],
                "listeners": last["listeners"] - first["listeners"],
                "render_descendants": (
                    last["render_descendants"] - first["render_descendants"]
                ),
                "aspect2d_descendants": (
                    last["aspect2d_descendants"] - first["aspect2d_descendants"]
                ),
                "prepared": {
                    name: last["prepared"][name] - first["prepared"][name]
                    for name in first["prepared"]
                },
            },
        }
    finally:
        app.destroy()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--scenario", choices=("hub", "menu", "pc"), required=True)
    parser.add_argument("--cycles", type=int, default=10)
    parser.add_argument("--frames-per-state", type=int, default=3)
    parser.add_argument(
        "--hub-variant",
        choices=(
            "all", "no_ui", "no_ui_no_world_text", "empty",
            "environment_only", "lit_environment", "lighting_only",
            "stations_only", "robot_only", "shared_lighting",
        ),
        default="all",
    )
    parser.add_argument("--pc-variant", choices=("all", "shared_lights"), default="all")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = run(
        args.scenario,
        args.cycles,
        args.frames_per_state,
        args.hub_variant,
        args.pc_variant,
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


if __name__ == "__main__":
    main()
