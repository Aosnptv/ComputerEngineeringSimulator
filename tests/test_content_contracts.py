import sys
import unittest
from pathlib import Path


SRC_ROOT = Path(__file__).resolve().parents[1] / "ComputerEngineeringVR" / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from content import STATIONS, station_text
from rooms.room_selector import ROOMS


class KnowledgeStationContractTests(unittest.TestCase):
    def test_six_unique_bilingual_stations_are_present(self):
        self.assertEqual(len(STATIONS), 6)
        self.assertEqual(len({station["id"] for station in STATIONS}), 6)
        for station in STATIONS:
            for language in ("en", "th"):
                name, description = station_text(station, language)
                self.assertTrue(name.strip())
                self.assertTrue(description.strip())


class IntegratedRoomMenuContractTests(unittest.TestCase):
    def test_selector_routes_to_three_original_rooms_without_quizzes(self):
        self.assertEqual(tuple(ROOMS), ("pc", "lan", "code"))
        for room in ROOMS.values():
            self.assertTrue(room["en"].strip())
            self.assertTrue(room["th"].strip())
            self.assertNotIn("questions", room)


if __name__ == "__main__":
    unittest.main()
