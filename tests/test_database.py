import unittest
import sqlite3
import os
from models import StarSystem, Planet
from database import DB_FILE, init_db, save_system, load_systems

class TestDatabase(unittest.TestCase):

    def setUp(self):
        # Use a temporary DB file
        self.test_db = "tests/test_db.sqlite"
        self.original_db_file = DB_FILE
        # Monkey-patch DB_FILE to test DB
        import database
        database.DB_FILE = self.test_db
        init_db()

    def tearDown(self):
        import database
        database.DB_FILE = self.original_db_file
        if os.path.exists(self.test_db):
            os.remove(self.test_db)

    def test_save_and_load_system(self):
        s = StarSystem("Alpha Centauri", "G2V", 4.37)
        s.add_planet(Planet("Proxima b", 1.3, 1.1, 0.05))
        save_system(s)

        systems = load_systems()
        self.assertEqual(len(systems), 1)
        self.assertEqual(systems[0].name, "Alpha Centauri")
        self.assertEqual(len(systems[0].planets), 1)
        self.assertEqual(systems[0].planets[0].name, "Proxima b")

    def test_partial_save_add_planet(self):
        s = StarSystem("Alpha Centauri", "G2V", 4.37)
        s.add_planet(Planet("Proxima b", 1.3, 1.1, 0.05))
        save_system(s)

        # Add a new planet and save again
        s.add_planet(Planet("Proxima c", 7.0, 1.8, 1.5))
        save_system(s)

        systems = load_systems()
        self.assertEqual(len(systems[0].planets), 2)
        names = {p.name for p in systems[0].planets}
        self.assertIn("Proxima b", names)
        self.assertIn("Proxima c", names)

    def test_partial_save_update_planet(self):
        s = StarSystem("Alpha Centauri", "G2V", 4.37)
        s.add_planet(Planet("Proxima b", 1.3, 1.1, 0.05))
        save_system(s)

        # Update Proxima b’s radius
        s.planets[0].radius = 1.05
        save_system(s)

        systems = load_systems()
        self.assertAlmostEqual(systems[0].planets[0].radius, 1.05)
