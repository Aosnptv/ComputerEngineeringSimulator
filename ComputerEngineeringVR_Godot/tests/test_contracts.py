import json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class ContentContracts(unittest.TestCase):
    def test_all_nine_missions_declared(self):
        text=(ROOT/'scripts/missions/mission_catalog.gd').read_text(encoding='utf-8')
        for room in ('pc','lan','programming'):
            self.assertIn(f'"{room}"', text)
        for level in ('easy','normal','hard'):
            self.assertGreaterEqual(text.count(f'"{level}"'), 3)

    def test_bilingual_catalogs_match(self):
        data=json.loads((ROOT/'data/localization/catalog.json').read_text(encoding='utf-8'))
        self.assertEqual(set(data['en']), set(data['th']))

    def test_hard_robot_has_two_scenarios(self):
        data=json.loads((ROOT/'data/missions/programming.json').read_text(encoding='utf-8'))
        self.assertEqual(data['hard']['scenario_count'], 2)
        self.assertIn('if_else', data['hard']['requires'])

    def test_release_preset(self):
        preset=(ROOT/'export_presets.cfg').read_text(encoding='utf-8')
        self.assertIn('platform="Windows Desktop"', preset)
        self.assertIn('ComputerEngineeringVR.exe', preset)

if __name__ == '__main__': unittest.main()

