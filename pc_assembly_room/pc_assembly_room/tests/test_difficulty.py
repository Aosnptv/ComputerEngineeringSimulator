import unittest
from pc_assembly_room.difficulty import LEVELS, available_parts, initial_parts
from pc_assembly_room.data import SLOTS, RULES
from pc_assembly_room.logic import AssemblyState
class DifficultyTests(unittest.TestCase):
 def test_levels(self):
  solution=[('psu','psu_std'),('motherboard','mobo_lga'),('cpu','cpu_intel'),('ram','ram_ddr4'),('storage','ssd_std'),('cooler','cooler_std'),('gpu','gpu_std')]
  for level in LEVELS:
   with self.subTest(level=level):
    state=AssemblyState(available_parts(level),SLOTS,RULES)
    for sid,pid in initial_parts(level):
     state.select(pid);self.assertTrue(state.place(sid).ok)
    self.assertEqual(len(state.installed),2 if level=='easy' else 0)
    for sid,pid in solution:
     if state.part_in(sid):continue
     state.select(pid);self.assertTrue(state.place(sid).ok)
    self.assertTrue(state.check().complete)
    self.assertEqual(state.mistakes,0)
    state.reset();self.assertEqual(state.installed,{})
 def test_invalid_level(self):
  with self.assertRaises(ValueError):available_parts('unknown')
