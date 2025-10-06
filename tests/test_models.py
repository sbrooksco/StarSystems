# tests/test_models.py
import unittest
from models import Planet, StarSystem

class TestPlanet(unittest.TestCase):

    def test_classify_terrestrial(self):
        p = Planet("Earth", 1, 1, 1)
        self.assertEqual(p.classify(), "Terrestrial")

    def test_classify_super_earth(self):
        p = Planet("SuperEarth", 5, 2, 1)
        self.assertEqual(p.classify(), "Super-Earth")

    def test_classify_gas_giant(self):
        p = Planet("Jupiter", 317.8, 11.2, 5.2)
        self.assertEqual(p.classify(), "Gas Giant")

    def test_str_includes_classification(self):
        p = Planet("Mars", 0.107, 0.53, 1.52)
        self.assertIn("Terrestrial", str(p))

class TestStarSystem(unittest.TestCase):

    def test_add_planet(self):
        s = StarSystem("Solar System", "G2V", 0)
        p = Planet("Earth", 1, 1, 1)
        s.add_planet(p)
        self.assertEqual(len(s.planets), 1)
        self.assertEqual(s.planets[0].name, "Earth")

    def test_str_contains_planet_names(self):
        s = StarSystem("TestSys", "K1V", 12)
        s.add_planet(Planet("PlanetX", 1, 1, 1))
        self.assertIn("PlanetX", str(s))