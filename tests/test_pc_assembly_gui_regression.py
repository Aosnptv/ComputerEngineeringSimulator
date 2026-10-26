import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch


SRC_ROOT = Path(__file__).resolve().parents[1] / "ComputerEngineeringVR" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from rooms.adapters.pc_assembly_adapter import PCAssemblyAdapter
from pc_assembly_room.pc_assembly_room.room3d import (
    COUNTER_LAYOUT,
    PROGRESS_BAR_POS,
    TOP_HUD_LAYOUT,
)
from pc_assembly_room.pc_assembly_room.strings import TEXT


class FakeWidget:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.destroyed = False

    def destroy(self):
        self.destroyed = True


class FakeController:
    def __init__(self):
        self.enabled_changes = []

    def set_enabled(self, enabled):
        self.enabled_changes.append(enabled)


class FakeWindow:
    def __init__(self):
        self.requests = []

    def requestProperties(self, properties):
        self.requests.append(properties)


class FakeInputScope:
    def __init__(self):
        self.bindings = []

    def bind(self, event, method, extra_args=None):
        self.bindings.append((event, method, extra_args))


class FakeApp:
    def __init__(self):
        self.win = FakeWindow()
        self.ignored = []
        self.accepted = []

    def ignore(self, event):
        self.ignored.append(event)

    def accept(self, event, method):
        self.accepted.append((event, method))

    def handle_escape(self):
        pass


class NavigationMenuTests(unittest.TestCase):
    def make_adapter(self):
        destinations = []
        adapter = PCAssemblyAdapter(font=None)
        adapter.context = SimpleNamespace(
            language="en",
            ui_root=object(),
            app=FakeApp(),
            input_scope=FakeInputScope(),
            navigate=destinations.append,
        )
        adapter.controller = FakeController()
        adapter.room = object()
        return adapter, destinations

    def test_navigation_menu_releases_and_restores_first_person_cursor(self):
        adapter, _ = self.make_adapter()
        with patch("rooms.adapters.pc_assembly_adapter.DirectFrame", FakeWidget), \
             patch("rooms.adapters.pc_assembly_adapter.DirectLabel", FakeWidget), \
             patch("rooms.adapters.pc_assembly_adapter.DirectButton", FakeWidget):
            adapter._toggle_navigation()
            panel = adapter.navigation_panel
            self.assertIsNotNone(panel)
            self.assertEqual(adapter.controller.enabled_changes, [False])
            self.assertEqual(len(adapter.context.app.win.requests), 1)

            adapter._toggle_navigation()
            self.assertTrue(panel.destroyed)
            self.assertIsNone(adapter.navigation_panel)
            self.assertEqual(adapter.controller.enabled_changes, [False, True])
            self.assertEqual(len(adapter.context.app.win.requests), 2)

    def test_navigation_menu_can_return_to_hub(self):
        adapter, destinations = self.make_adapter()
        adapter._navigate_hub()
        self.assertEqual(destinations, ["hub"])

    def test_navigation_shortcut_is_ignored_outside_gameplay(self):
        adapter, _ = self.make_adapter()
        adapter.controller = None
        adapter._toggle_navigation()
        self.assertIsNone(adapter.navigation_panel)

    def test_escape_is_reserved_for_shared_pause_menu(self):
        adapter, _ = self.make_adapter()
        self.assertFalse(hasattr(adapter, "_claim_escape_navigation"))
        self.assertFalse(hasattr(adapter, "_restore_application_escape"))


class HudLayoutTests(unittest.TestCase):
    def test_top_hud_rows_have_safe_vertical_spacing(self):
        ordered = [TOP_HUD_LAYOUT[name] for name in ("hint", "status", "progress")]
        for (upper_y, upper_scale), (lower_y, lower_scale) in zip(ordered, ordered[1:]):
            self.assertGreaterEqual(upper_y - lower_y, upper_scale + lower_scale)

    def test_counter_and_progress_bar_stay_in_the_top_right_lane(self):
        (counter_x, counter_y), counter_scale = COUNTER_LAYOUT
        bar_x, _, bar_y = PROGRESS_BAR_POS
        self.assertGreater(counter_x, 1.0)
        self.assertGreater(bar_x, 1.0)
        self.assertGreater(counter_y - counter_scale, bar_y)


class IntegrationCopyTests(unittest.TestCase):
    def test_menu_copy_describes_completed_main_hub_integration(self):
        self.assertNotIn("pending", TEXT["en"]["menu.note"].lower())
        self.assertNotIn("ยังไม่ได้", TEXT["th"]["menu.note"])
        self.assertIn("Main Hub", TEXT["en"]["menu.note"])
        self.assertIn("Main Hub", TEXT["th"]["menu.note"])

    def test_gameplay_help_matches_integrated_navigation(self):
        for language in ("en", "th"):
            self.assertIn("Tab", TEXT[language]["ui.hint_walk"])
            self.assertNotIn("exit test", TEXT[language]["ui.hint_walk"].lower())


if __name__ == "__main__":
    unittest.main()
