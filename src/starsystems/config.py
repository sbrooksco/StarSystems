"""Configuration management for StarSystems application."""

import os
from pathlib import Path
from typing import Optional

"""Application configuration."""
class Config:

    def __init__(self):
        self.db_path = self._get_db_path()
        self.admin_password = os.getenv("STARADMIN", "changeme")

    """Determine database path based on environment.

    Returns:
        Path to SQLite database file
    """
    def _get_db_path(self) -> str:

        # Check for explicit DB path
        db_path = os.getenv("STAR_SYSTEMS_DB")
        if db_path:
            return db_path

        # Render deployment (ephemeral filesystem)
        if os.getenv("RENDER") == "true":
            return "/tmp/star_systems.db"

        # Local development - create data directory if needed
        data_dir = Path(__file__).parent.parent.parent.parent / "data"
        data_dir.mkdir(exist_ok=True)
        return str(data_dir / "star_systems.db")


# Singleton instance
config = Config()