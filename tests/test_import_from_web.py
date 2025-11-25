# tests/test_import_from_web.py
import unittest
from unittest.mock import patch
import tempfile
import os
import importlib
from models import StarSystem, Planet

class TestImportFromWeb(unittest.TestCase):

    def setUp(self):
        # Temporary DB file for this test
        fd, self.temp_db_path = tempfile.mkstemp(suffix=".sqlite")
        os.close(fd)
        os.environ["STAR_SYSTEMS_DB"] = self.temp_db_path

        # Import & reload database module after env var
        import database
        import star_system_app
        importlib.reload(database)
        importlib.reload(star_system_app)

        # Initialize DB tables
        database.init_db()

        self.app_cls = star_system_app.StarSystemApp
        self.db = database

    def tearDown(self):
        try:
            os.remove(self.temp_db_path)
        except OSError:
            pass
        os.environ.pop("STAR_SYSTEMS_DB", None)

    @patch("star_system_app.get_web_data")
    def test_import_from_web_adds_new_systems(self, mock_get_web_data):
        mock_system = StarSystem("Mock System", "G2V", 10)
        mock_system.add_planet(Planet("MockPlanet", 1.0, 1.0, 1.0))
        mock_get_web_data.return_value = [mock_system]

        app = self.app_cls()
        app.systems = []

        app.import_from_web()

        self.assertEqual(len(app.systems), 1)
        self.assertEqual(app.systems[0].name, "Mock System")
        self.assertEqual(len(app.systems[0].planets), 1)

    @patch("star_system_app.get_web_data")
    def test_import_from_web_ignores_duplicates(self, mock_get_web_data):
        existing = StarSystem("Existing", "K1", 12)
        app = self.app_cls()
        app.systems = [existing]

        duplicate = StarSystem("Existing", "G2V", 10)
        mock_get_web_data.return_value = [duplicate]

        app.import_from_web()

        self.assertEqual(len(app.systems), 1)
        self.assertEqual(app.systems[0].name, "Existing")

    @patch("star_system_app.get_web_data")
    def test_import_from_web_no_data(self, mock_get_web_data):
        app = self.app_cls()
        app.systems = []
        mock_get_web_data.return_value = None

        app.import_from_web()

        self.assertEqual(len(app.systems), 0)


if __name__ == "__main__":
    unittest.main()


