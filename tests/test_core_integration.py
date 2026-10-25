import unittest

from ComputerEngineeringVR.src.core.room_contract import (
    Room,
    RoomContext,
    RoomResult,
    RoomState,
)
from ComputerEngineeringVR.src.core.scene_manager import SceneManager
from ComputerEngineeringVR.src.core.session_state import SessionState
from pc_assembly_room.pc_assembly_room.score_policy import trial_stars


class FakeNode:
    def __init__(self, name="root"):
        self.name = name
        self.removed = False
        self.children = []

    def attachNewNode(self, name):
        child = FakeNode(name)
        self.children.append(child)
        return child

    def isEmpty(self):
        return self.removed

    def removeNode(self):
        self.removed = True


class FakeInputScope:
    def __init__(self):
        self.cleared = False

    def clear(self):
        self.cleared = True


class FakeApp:
    def __init__(self):
        self.render = FakeNode("render")
        self.aspect2d = FakeNode("aspect2d")


class RecordingRoom(Room):
    room_id = "recording"

    def __init__(self, events, fail_enter=False):
        super().__init__()
        self.events = events
        self.fail_enter = fail_enter

    def _on_load(self):
        self.events.append("load")

    def _on_enter(self):
        self.events.append("enter")
        if self.fail_enter:
            raise RuntimeError("enter failed")

    def _on_reset(self):
        self.events.append("reset")

    def _on_exit(self):
        self.events.append("exit")

    def _on_unload(self):
        self.events.append("unload")


class RoomContractTests(unittest.TestCase):
    def context(self):
        return RoomContext(
            app=None,
            scene_root=FakeNode(),
            ui_root=FakeNode(),
            input_scope=FakeInputScope(),
            language="en",
            session=SessionState(),
            navigate=lambda room: None,
            complete=lambda result: None,
            report_error=lambda room, error: None,
        )

    def test_lifecycle_and_duplicate_cleanup_are_safe(self):
        events = []
        room = RecordingRoom(events)
        room.load(self.context())
        room.enter()
        room.reset()
        room.exit()
        room.exit()
        room.unload()
        room.unload()
        self.assertEqual(events, ["load", "enter", "reset", "exit", "unload"])
        self.assertEqual(room.state, RoomState.UNLOADED)

    def test_enter_twice_is_rejected(self):
        room = RecordingRoom([])
        room.load(self.context())
        room.enter()
        with self.assertRaises(RuntimeError):
            room.enter()

    def test_result_validation(self):
        result = RoomResult("pc_assembly", "easy", 12.5, 1, 3)
        self.assertTrue(result.completed)
        with self.assertRaises(ValueError):
            RoomResult("pc_assembly", "easy", 1, 0, 4)


class SceneManagerTests(unittest.TestCase):
    def make_manager(self, errors=None):
        return SceneManager(
            FakeApp(),
            SessionState(language="th"),
            on_error=lambda room, error: errors.append((room, str(error))) if errors is not None else None,
            input_scope_factory=FakeInputScope,
        )

    def test_transition_cleans_previous_room_and_roots(self):
        first_events, second_events = [], []
        manager = self.make_manager()
        manager.register("hub", lambda: RecordingRoom(first_events))
        manager.register("pc", lambda: RecordingRoom(second_events))

        self.assertTrue(manager.go_to("hub"))
        first_context = manager.active_context
        self.assertTrue(manager.go_to("pc"))

        self.assertEqual(first_events, ["load", "enter", "exit", "unload"])
        self.assertTrue(first_context.input_scope.cleared)
        self.assertTrue(first_context.scene_root.removed)
        self.assertTrue(first_context.ui_root.removed)
        self.assertEqual(manager.session.current_room, "pc")

    def test_failed_room_returns_to_hub(self):
        errors, failed_events, hub_events = [], [], []
        manager = self.make_manager(errors)
        manager.register("hub", lambda: RecordingRoom(hub_events))
        manager.register("pc", lambda: RecordingRoom(failed_events, fail_enter=True))

        self.assertFalse(manager.go_to("pc"))
        self.assertEqual(manager.active_room_id, "hub")
        self.assertEqual(failed_events, ["load", "enter", "unload"])
        self.assertEqual(errors[0][0], "pc")

    def test_completion_updates_transient_session(self):
        manager = self.make_manager()
        result = RoomResult("pc_assembly", "medium", 20, 2, 2)
        manager._record_result(result)
        self.assertEqual(manager.session.last_result, result)
        self.assertEqual(manager.session.results["pc_assembly"], result)

    def test_ten_hub_room_round_trips_cleanup_every_context(self):
        manager = self.make_manager()
        manager.register("hub", lambda: RecordingRoom([]))
        manager.register("pc", lambda: RecordingRoom([]))
        retired_contexts = []

        manager.go_to("hub")
        for _ in range(10):
            retired_contexts.append(manager.active_context)
            manager.go_to("pc")
            retired_contexts.append(manager.active_context)
            manager.go_to("hub")

        for context in retired_contexts:
            self.assertTrue(context.input_scope.cleared)
            self.assertTrue(context.scene_root.removed)
            self.assertTrue(context.ui_root.removed)
        self.assertEqual(manager.active_room_id, "hub")


class SessionStateTests(unittest.TestCase):
    def test_reset_clears_results_without_disk_state(self):
        session = SessionState(language="en", current_room="pc")
        session.record_result(RoomResult("pc_assembly", "easy", 1, 0, 3))
        session.selected_difficulty = "easy"
        session.reset(language="th")
        self.assertEqual(session.language, "th")
        self.assertEqual(session.current_room, "")
        self.assertIsNone(session.last_result)
        self.assertEqual(session.results, {})


class PCScoringContractTests(unittest.TestCase):
    def test_existing_policy_maps_easy_and_medium_to_one_to_three_stars(self):
        for difficulty in ("easy", "medium"):
            self.assertEqual(trial_stars(difficulty, 1, 0), 3)
            self.assertEqual(trial_stars(difficulty, 10_000, 99), 1)


if __name__ == "__main__":
    unittest.main()
