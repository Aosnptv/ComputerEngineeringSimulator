import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SRC_ROOT = Path(__file__).resolve().parents[1] / "ComputerEngineeringVR" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from core.vr_mode import create_optional_vr_adapter, inspect_vr_readiness


class OptionalVRModeTests(unittest.TestCase):
    def test_desktop_is_default_and_does_not_require_vr(self):
        with patch("core.vr_mode._active_runtime_manifest", return_value=None), \
             patch("core.vr_mode.importlib.util.find_spec", return_value=None):
            adapter = create_optional_vr_adapter(False)
        self.assertFalse(adapter.active)
        self.assertFalse(adapter.readiness.requested)
        self.assertTrue(adapter.readiness.desktop_fallback)

    def test_vr_request_without_runtime_falls_back_cleanly(self):
        with patch("core.vr_mode._active_runtime_manifest", return_value=None), \
             patch("core.vr_mode.importlib.util.find_spec", return_value=None):
            status = inspect_vr_readiness(True)
        self.assertEqual(status.classification, "NOT AVAILABLE")
        self.assertTrue(status.desktop_fallback)

    def test_installed_runtime_without_backend_is_not_claimed_verified(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).parent) as directory:
            manifest = Path(directory) / "runtime.json"
            manifest.write_text(
                json.dumps({"runtime": {"name": "Test OpenXR"}}), encoding="utf-8"
            )
            with patch(
                "core.vr_mode._active_runtime_manifest", return_value=str(manifest)
            ), patch("core.vr_mode.importlib.util.find_spec", return_value=None):
                status = inspect_vr_readiness(True)
        self.assertEqual(status.runtime_name, "Test OpenXR")
        self.assertEqual(status.classification, "INSTALLED BUT NOT TESTED")
        self.assertFalse(status.integration_module_available)


if __name__ == "__main__":
    unittest.main()
