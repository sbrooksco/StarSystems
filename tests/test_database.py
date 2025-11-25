# tests/test_database.py
import unittest
import tempfile
import os
import importlib
from models import StarSystem, Planet

class TestDatabase(unittest.TestCase):
    def setUp(self):
        # Create a temporary SQLite DB file
        fd, self.temp_db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)

        # Set environment variable so database module picks it up
        os.environ["STAR_SYSTEMS_DB"] = self.temp_db_path

        # Import & reload database module after env var is set
        import database
        importlib.reload(database)

        # Initialize tables in temp DB
        database.init_db()
        self.db = database

    def tearDown(self):
        # Remove temporary DB file after test
        try:
            os.remove(self.temp_db_path)
        except OSError:
            pass
        os.environ.pop("STAR_SYSTEMS_DB", None)

    def test_save_and_load_system(self):
        # Create a test system with one planet
        system = StarSystem("Alpha Centauri", "G2V", 4.37)
        planet = Planet("Proxima b", 1.2, 1.1, 0.05)
        system.add_planet(planet)

        self.db.save_system(system)
        systems = self.db.load_systems()
        self.assertEqual(len(systems), 1)

        loaded = systems[0]
        self.assertEqual(loaded.name, "Alpha Centauri")
        self.assertEqual(len(loaded.planets), 1)

        loaded_planet = loaded.planets[0]
        self.assertEqual(loaded_planet.name, "Proxima b")
        self.assertAlmostEqual(loaded_planet.mass, 1.2)
        self.assertAlmostEqual(loaded_planet.radius, 1.1)
        self.assertAlmostEqual(loaded_planet.orbit_distance, 0.05)

    def test_partial_save(self):
        # Save system with one planet, then add another
        system = StarSystem("Beta", "K0", 50)
        planet1 = Planet("B-1", 1.0, 1.0, 1.0)
        system.add_planet(planet1)
        self.db.save_system(system)

        planet2 = Planet("B-2", 2.0, 1.5, 2.0)
        system.add_planet(planet2)
        self.db.save_system(system)

        systems = self.db.load_systems()
        self.assertEqual(len(systems), 1)
        self.assertEqual(len(systems[0].planets), 2)


if __name__ == "__main__":
    unittest.main()




