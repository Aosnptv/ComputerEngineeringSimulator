import json
import os
import sys
import tempfile
import unittest
import weakref
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
VR_SRC = ROOT / "ComputerEngineeringVR" / "src"
if str(VR_SRC) not in sys.path:
    sys.path.insert(0, str(VR_SRC))

from core.runtime_diagnostics import RuntimeDiagnostics, install_runtime_diagnostics


class _Object:
    pass


class RuntimeDiagnosticsTests(unittest.TestCase):
    def test_default_is_off_and_creates_no_collector(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertIsNone(install_runtime_diagnostics(_Object()))

    def test_enabled_collector_writes_jsonl_outside_repository(self):
        with tempfile.TemporaryDirectory() as temp_root:
            diagnostics = RuntimeDiagnostics(
                _Object(), log_root=temp_root, enable_tracemalloc=False
            )
            diagnostics.snapshot("test.sample")
            self.assertTrue(diagnostics.log_path.is_file())
            self.assertFalse(
                diagnostics.log_path.resolve().is_relative_to(ROOT.resolve())
            )
            records = [
                json.loads(line)
                for line in diagnostics.log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(records[-1]["phase"], "test.sample")

    def test_tracking_uses_weak_references_only(self):
        with tempfile.TemporaryDirectory() as temp_root:
            diagnostics = RuntimeDiagnostics(
                _Object(), log_root=temp_root, enable_tracemalloc=False
            )
            target = _Object()
            target_ref = weakref.ref(target)
            diagnostics.track("target", target)
            del target
            self.assertIsNone(target_ref())
            records = [
                json.loads(line)
                for line in diagnostics.log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertTrue(any(item.get("event") == "weakref.collected" for item in records))

    def test_transition_counts_pc_to_hub_cycles(self):
        with tempfile.TemporaryDirectory() as temp_root:
            diagnostics = RuntimeDiagnostics(
                _Object(), log_root=temp_root, enable_tracemalloc=False
            )
            diagnostics.transition_begin("hub", "pc_assembly")
            diagnostics.transition_begin("pc_assembly", "hub")
            records = [
                json.loads(line)
                for line in diagnostics.log_path.read_text(encoding="utf-8").splitlines()
            ]
            self.assertEqual(records[-1]["cycle"], 1)


if __name__ == "__main__":
    unittest.main()
