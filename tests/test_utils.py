import unittest
import os
from src.starsystems.models.models import Planet, StarSystem
from utils import save_to_csv, load_from_csv, search_planets_by_mass, search_planets_by_type

class TestCSVUtilities(unittest.TestCase):

    def setUp(self):
        # Prepare a temporary CSV path
        self.csv_file = "tests/temp_systems.csv"
        # Create sample systems
        self.systems = []
        s = StarSystem("TestSys", "G2V", 10)
        s.add_planet(Planet("Earth", 1, 1, 1))
        s.add_planet(Planet("Jupiter", 317.8, 11.2, 5.2))
        self.systems.append(s)

    def tearDown(self):
        if os.path.exists(self.csv_file):
            os.remove(self.csv_file)

    def test_save_and_load_csv(self):
        save_to_csv(self.systems, self.csv_file)
        loaded = load_from_csv(self.csv_file)
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].name, "TestSys")
        self.assertEqual(len(loaded[0].planets), 2)

    def test_search_by_mass(self):
        results = search_planets_by_mass(self.systems, 100)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1].name, "Jupiter")

    def test_search_by_type(self):
        results = search_planets_by_type(self.systems, "Terrestrial")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][1].name, "Earth")