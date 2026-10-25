"""รัน: python -m unittest discover -s tests -t ..   (จากในโฟลเดอร์ pc_assembly_room)
หรือ: python -m unittest pc_assembly_room.tests.test_logic  (จากโฟลเดอร์แม่)
ไม่ต้องติดตั้ง Panda3D"""
import itertools
import unittest

from pc_assembly_room.data import PARTS, RULES, SLOTS
from pc_assembly_room.logic import AssemblyState, Code
from pc_assembly_room.strings import TEXT


def new():
    return AssemblyState(PARTS, SLOTS, RULES)


def put(s, part, slot):
    assert s.select(part).ok
    return s.place(slot)


class LogicTests(unittest.TestCase):
    def test_full_valid_build_intel(self):
        s = new()
        for p, sl in [("psu_std", "psu"), ("mobo_lga", "motherboard"), ("cpu_intel", "cpu"),
                      ("cooler_std", "cooler"), ("ram_ddr4", "ram"), ("gpu_std", "gpu"),
                      ("ssd_std", "storage")]:
            self.assertTrue(put(s, p, sl).ok, (p, sl))
        self.assertTrue(s.check().complete)
        self.assertEqual(s.mistakes, 0)

    def test_full_valid_build_amd(self):
        s = new()
        for p, sl in [("mobo_am5", "motherboard"), ("cpu_amd", "cpu"), ("ram_ddr5", "ram"),
                      ("cooler_std", "cooler"), ("gpu_std", "gpu"), ("ssd_std", "storage"),
                      ("psu_std", "psu")]:
            self.assertTrue(put(s, p, sl).ok, (p, sl))
        self.assertTrue(s.check().complete)

    def test_need_first(self):
        s = new()
        r = put(s, "cpu_intel", "cpu")
        self.assertEqual((r.code, r.slot), (Code.NEED_FIRST, "motherboard"))
        self.assertEqual(s.mistakes, 1)

    def test_wrong_slot(self):
        s = new()
        self.assertEqual(put(s, "gpu_std", "psu").code, Code.WRONG_SLOT)
        self.assertEqual(s.mistakes, 1)

    def test_incompatible_cpu_and_ram(self):
        s = new()
        put(s, "mobo_lga", "motherboard")
        r = put(s, "cpu_amd", "cpu")
        self.assertEqual((r.code, r.slot), (Code.INCOMPATIBLE, "motherboard"))
        r = put(s, "ram_ddr5", "ram")
        self.assertEqual(r.code, Code.INCOMPATIBLE)
        self.assertEqual(s.mistakes, 2)

    def test_nothing_selected_not_mistake(self):
        s = new()
        self.assertEqual(s.place("psu").code, Code.NOTHING_SELECTED)
        self.assertEqual(s.mistakes, 0)

    def test_slot_filled_not_mistake(self):
        s = new()
        put(s, "mobo_lga", "motherboard")
        self.assertEqual(put(s, "mobo_am5", "motherboard").code, Code.SLOT_FILLED)
        self.assertEqual(s.mistakes, 0)

    def test_remove_blocked_by_dependents(self):
        s = new()
        put(s, "mobo_lga", "motherboard")
        put(s, "cpu_intel", "cpu")
        r = s.remove("motherboard")
        self.assertEqual(r.code, Code.HAS_DEPENDENTS)
        self.assertEqual(s.remove("cpu").code, Code.OK)
        self.assertEqual(s.remove("motherboard").code, Code.OK)

    def test_remove_empty_and_reinstall(self):
        s = new()
        self.assertEqual(s.remove("psu").code, Code.EMPTY_SLOT)
        put(s, "psu_std", "psu")
        self.assertEqual(s.select("psu_std").code, Code.ALREADY_INSTALLED)
        s.remove("psu")
        self.assertTrue(put(s, "psu_std", "psu").ok)

    def test_check_incomplete_lists_missing(self):
        s = new()
        put(s, "psu_std", "psu")
        c = s.check()
        self.assertFalse(c.complete)
        self.assertEqual(len(c.missing), len(SLOTS) - 1)

    def test_reset(self):
        s = new()
        put(s, "psu_std", "psu")
        put(s, "gpu_std", "psu")
        s.reset()
        self.assertEqual((s.installed, s.selected, s.mistakes), ({}, None, 0))

    def test_unknown_ids(self):
        s = new()
        self.assertEqual(s.select("nope").code, Code.UNKNOWN_PART)
        s.select("psu_std")
        self.assertEqual(s.place("nope").code, Code.UNKNOWN_SLOT)


class DataTests(unittest.TestCase):
    def test_every_slot_has_a_part(self):
        for sl in SLOTS:
            self.assertTrue(any(p.kind is sl.kind for p in PARTS), sl.id)

    def test_a_valid_full_solution_exists(self):
        by_slot = [[p for p in PARTS if p.kind is sl.kind] for sl in SLOTS]
        found = False
        for combo in itertools.product(*by_slot):
            s = new()
            order = sorted(zip(SLOTS, combo), key=lambda x: len(x[0].requires))
            if all(put(s, p.id, sl.id).ok for sl, p in order) and s.check().complete:
                found = True
                break
        self.assertTrue(found)


class StringTests(unittest.TestCase):
    def test_th_en_same_keys(self):
        self.assertEqual(set(TEXT["th"]), set(TEXT["en"]))

    def test_all_parts_slots_codes_have_text(self):
        for p in PARTS:
            self.assertIn(f"part.{p.id}", TEXT["th"])
        for sl in SLOTS:
            self.assertIn(f"slot.{sl.id}", TEXT["th"])
        for c in Code:
            if c is not Code.OK:
                self.assertIn(f"msg.{c.value}", TEXT["th"], c)


if __name__ == "__main__":
    unittest.main()
