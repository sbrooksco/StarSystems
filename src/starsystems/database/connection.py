import sqlite3
from contextlib import contextmanager
from typing import Generator
from ..config import config

"""
Manage SQLite databse connection and schema initialization.
"""
class DatabaseConnection:

    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.db_path

    def initialize_schema(self) -> None:
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Star systems table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS star_systems (
                    name TEXT PRIMARY KEY,
                    spectral_type TEXT,
                    distance_ly REAL
                )
            """)

            # Planets table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS planets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    mass REAL,
                    radius REAL,
                    orbit_distance REAL,
                    system_name TEXT,
                    UNIQUE(name, system_name),
                    FOREIGN KEY(system_name) REFERENCES systems(name)
                        ON DELETE CASCADE
                )
            """)

            # Index for common queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_distance 
                ON star_systems(distance_ly)
            """)

            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_spectral_type
                ON star_systems(spectral_type)
            """)

    """
    Context manager for database connections.

    Yields:
        SQLite connection object
    """
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()


"""
Module-level function for backwards compatibility
Get a database connection.

Args:
    db_path: Optional database path (uses config default if None)

Returns:
    SQLite connection
"""
def get_connection(db_path: str = None) -> sqlite3.Connection:
    return sqlite3.connect(db_path or config.db_path)