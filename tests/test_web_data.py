import unittest
from unittest.mock import patch
from web_data import get_web_data

class TestWebDataParsing(unittest.TestCase):

    @patch("web_data.acquire_data")
    def test_get_web_data_parsing(self, mock_acquire):
        # Fake API JSON output
        mock_acquire.return_value = [
            {
                "hostname": "Kepler-22",
                "pl_name": "Kepler-22b",
                "pl_bmassj": 0.5,
                "pl_radj": 1.2,
                "pl_orbper": 290
            }
        ]

        systems = get_web_data()

        # Assertions
        self.assertEqual(len(systems), 1)
        system = systems[0]
        self.assertEqual(system.name, "Kepler-22")
        self.assertEqual(len(system.planets), 1)
        self.assertEqual(system.planets[0].name, "Kepler-22b")

if __name__ == "__main__":
    unittest.main()
