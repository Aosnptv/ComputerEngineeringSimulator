"""Opt-in runtime resource diagnostics for Stage B.1.6C.

The collector is deliberately observational: it owns no Panda3D scene objects,
adds no tasks or messenger bindings, and never forces garbage collection.
"""

from __future__ import annotations

import json
import os
import tempfile
import time
import tracemalloc
import weakref
from pathlib import Path


ENVIRONMENT_FLAG = "CES_RESOURCE_DIAGNOSTICS"
MILESTONES = frozenset((0, 1, 2, 5, 10))


def diagnostics_enabled() -> bool:
    return os.environ.get(ENVIRONMENT_FLAG) == "1"


def install_runtime_diagnostics(app):
    """Return an enabled collector, or ``None`` with zero persistent hooks."""
    if not diagnostics_enabled():
        return None
    return RuntimeDiagnostics(app)


class RuntimeDiagnostics:
    def __init__(self, app, log_root=None, enable_tracemalloc=True):
        self._app_ref = weakref.ref(app)
        self._tracked: dict[str, list[weakref.ReferenceType]] = {}
        self._cycle = 0
        self._transition = 0
        self._previous_room = None
        self._trace_baseline: dict[str, int] | None = None
        self._tracemalloc_started_here = False
        root = Path(log_root or Path(tempfile.gettempdir()) / "CES-B1.6C")
        root.mkdir(parents=True, exist_ok=True)
        self.log_path = root / f"runtime-diagnostics-{os.getpid()}.jsonl"
        if enable_tracemalloc and not tracemalloc.is_tracing():
            tracemalloc.start(10)
            self._tracemalloc_started_here = True
        self.snapshot("diagnostics.enabled", extra={"log_path": str(self.log_path)})

    def transition_begin(self, source, destination):
        self._transition += 1
        self._previous_room = source
        if source == "pc_assembly" and destination == "hub":
            self._cycle += 1
        self.snapshot(
            "transition.begin",
            scene_name=destination,
            extra={"source": source, "destination": destination},
        )

    def track(self, label, obj):
        if obj is None:
            return
        owner_ref = weakref.ref(self)

        def collected(_reference, tracked_label=label, collector_ref=owner_ref):
            collector = collector_ref()
            if collector is not None:
                collector._write({
                    "event": "weakref.collected",
                    "label": tracked_label,
                    "cycle": collector._cycle,
                    "transition": collector._transition,
                })

        try:
            reference = weakref.ref(obj, collected)
        except TypeError:
            self._write({"event": "weakref.unsupported", "label": label})
            return
        self._tracked.setdefault(label, []).append(reference)

    def snapshot(self, phase, scene_name="", context=None, room=None,
                 extra=None, track=None):
        """Write one bounded snapshot; diagnostic failures never affect gameplay."""
        try:
            for label, target in (track or {}).items():
                self.track(label, target)
            app = self._app_ref()
            record = {
                "event": "snapshot",
                "phase": phase,
                "scene": scene_name,
                "cycle": self._cycle,
                "transition": self._transition,
                "process_id": os.getpid(),
                "weakrefs": self._weakref_status(),
            }
            if app is not None:
                record["tasks"] = self._task_metrics(app)
                record["messenger"] = self._messenger_metrics()
                record["nodes"] = {
                    "render_descendants": self._descendants(getattr(app, "render", None)),
                    "aspect2d_descendants": self._descendants(getattr(app, "aspect2d", None)),
                    "scene_root_descendants": self._descendants(
                        getattr(context, "scene_root", None)
                    ),
                    "ui_root_descendants": self._descendants(
                        getattr(context, "ui_root", None)
                    ),
                }
                record["directgui_approximation"] = {
                    "method": "aspect2d descendant NodePaths; not a Python object count",
                    "count": record["nodes"]["aspect2d_descendants"],
                }
            record["procedural_resources"] = self._resource_counts()
            if extra:
                record["extra"] = extra
            if self._cycle in MILESTONES and phase in {
                "diagnostics.enabled", "transition.complete", "pc.activity.started",
                "pc.activity.cleaned", "idle.sample",
            }:
                trace = self._trace_metrics()
                if trace is not None:
                    record["tracemalloc"] = trace
            self._write(record)
        except Exception as exc:
            try:
                self._write({"event": "diagnostics.error", "phase": phase,
                             "error": f"{type(exc).__name__}: {exc}"})
            except Exception:
                pass

    def _write(self, record):
        payload = {"timestamp": time.time(), **record}
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")

    def _weakref_status(self):
        status = {}
        for label, references in self._tracked.items():
            alive = [reference for reference in references if reference() is not None]
            status[label] = {"tracked": len(references), "alive": len(alive)}
        return status

    @staticmethod
    def _descendants(node):
        if node is None:
            return None
        try:
            if hasattr(node, "isEmpty") and node.isEmpty():
                return 0
            return int(node.findAllMatches("**").getNumPaths())
        except Exception:
            return None

    @staticmethod
    def _task_metrics(app):
        try:
            tasks = list(app.taskMgr.getTasks())
            return {
                "count": len(tasks),
                "names": sorted(str(task.getName()) for task in tasks),
            }
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}

    @staticmethod
    def _messenger_metrics():
        try:
            from direct.showbase.MessengerGlobal import messenger
            callbacks = getattr(messenger, "_Messenger__callbacks", None)
            if not isinstance(callbacks, dict):
                return {"supported": False}
            callback_count = 0
            for listeners in callbacks.values():
                try:
                    callback_count += len(listeners)
                except TypeError:
                    callback_count += 1
            return {
                "supported": True,
                "event_count": len(callbacks),
                "callback_count": callback_count,
                "events": sorted(str(name) for name in callbacks),
            }
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}

    @staticmethod
    def _resource_counts():
        try:
            from pc_assembly_room.pc_assembly_room.lab_visuals import (
                get_diagnostic_resource_counts,
            )
            return get_diagnostic_resource_counts()
        except Exception as exc:
            return {"supported": False, "error": f"{type(exc).__name__}: {exc}"}

    def _trace_metrics(self):
        if not tracemalloc.is_tracing():
            return None
        current, peak = tracemalloc.get_traced_memory()
        snapshot = tracemalloc.take_snapshot()
        stats = snapshot.statistics("lineno")[:12]
        current_map = {str(stat.traceback[0]): stat.size for stat in stats}
        baseline = self._trace_baseline or {}
        result = {
            "current_bytes": current,
            "peak_bytes": peak,
            "top_lines": [
                {
                    "location": location,
                    "bytes": size,
                    "delta_from_initial_bytes": size - baseline.get(location, 0),
                }
                for location, size in current_map.items()
            ],
        }
        if self._trace_baseline is None:
            self._trace_baseline = current_map
        del snapshot, stats
        return result
