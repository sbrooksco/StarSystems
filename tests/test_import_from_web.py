import unittest
from unittest.mock import patch
from star_system_app import StarSystemApp
from models import StarSystem, Planet


class TestImportFromWeb(unittest.TestCase):

    @patch("star_system_app.get_web_data")
    def test_import_from_web_adds_new_systems(self, mock_get_web_data):
        # Arrange: mock web data
        mock_system = StarSystem("Mock System", "G2V", 10)
        mock_system.add_planet(Planet("MockPlanet", 1.0, 1.0, 1.0))
        mock_get_web_data.return_value = [mock_system]

        app = StarSystemApp()
        app.systems = []  # isolate test from DB

        # Act
        app.import_from_web()

        # Assert
        self.assertEqual(len(app.systems), 1)
        self.assertEqual(app.systems[0].name, "Mock System")

    @patch("star_system_app.get_web_data")
    def test_import_from_web_ignores_duplicates(self, mock_get_web_data):
        # Arrange: existing system
        existing = StarSystem("Existing", "K1", 12)
        app = StarSystemApp()
        app.systems = [existing]

        # Mock supports duplicate name
        duplicate = StarSystem("Existing", "G2V", 10)
        mock_get_web_data.return_value = [duplicate]

        # Act
        app.import_from_web()

        # Assert
        self.assertEqual(len(app.systems), 1)
        self.assertEqual(app.systems[0].name, "Existing")

    @patch("star_system_app.get_web_data")
    def test_import_from_web_no_data(self, mock_get_web_data):
        # Arrange
        app = StarSystemApp()
        app.systems = []
        mock_get_web_data.return_value = None

        # Act
        app.import_from_web()

        # Assert
        self.assertEqual(len(app.systems), 0)


if __name__ == "__main__":
    unittest.main()
