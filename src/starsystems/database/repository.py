
import sqlite3
from typing import List, Optional, Dict, Any
from ..models import StarSystem, Planet
from .connection import DatabaseConnection

"""
Repository for CRUD operations on star systems.

This class isolates database operations from business logic,
following the repository pattern.
"""
class StarSystemRepository:

    def __init__(self, db_connection: DatabaseConnection = None):
        self.db = db_connection or DatabaseConnection()

    """
    Save or update a star system and its planets.

    Args:
        system: StarSystem to save
    """
    def save(self, system: StarSystem) -> None:

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Upsert star system
            cursor.execute("""
                INSERT INTO star_systems (name, spectral_type, distance_ly)
                VALUES (?, ?, ?)
                ON CONFLICT(name) DO UPDATE SET
                    spectral_type = excluded.spectral_type,
                    distance_ly = excluded.distance_ly
            """, (system.name, system.spectral_type, system.distance_ly))

            # Upsert planets
            for planet in system.planets:
                cursor.execute("""
                    INSERT INTO planets (name, mass, radius, orbit_distance, system_name)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(name, system_name) DO UPDATE SET
                        mass = excluded.mass,
                        radius = excluded.radius,
                        orbit_distance = excluded.orbit_distance
                """, (planet.name, planet.mass, planet.radius,
                      planet.orbit_distance, system.name))

            conn.commit()

    """
    Save multiple star systems in a transaction.

    Args:
        systems: List of StarSystems to save

    Returns:
        Tuple of (successful_count, failed_count)
    """
    def save_batch(self, systems: List[StarSystem]) -> tuple[int, int]:

        success_count = 0
        failed_count = 0

        with self.db.get_connection() as conn:
            for system in systems:
                try:
                    cursor = conn.cursor()

                    cursor.execute("""
                        INSERT INTO star_systems (name, spectral_type, distance_ly)
                        VALUES (?, ?, ?)
                        ON CONFLICT(name) DO UPDATE SET
                            spectral_type = excluded.spectral_type,
                            distance_ly = excluded.distance_ly
                    """, (system.name, system.spectral_type, system.distance_ly))

                    for planet in system.planets:
                        cursor.execute("""
                            INSERT INTO planets (name, mass, radius, orbit_distance, system_name)
                            VALUES (?, ?, ?, ?, ?)
                            ON CONFLICT(name, system_name) DO UPDATE SET
                                mass = excluded.mass,
                                radius = excluded.radius,
                                orbit_distance = excluded.orbit_distance
                        """, (planet.name, planet.mass, planet.radius,
                              planet.orbit_distance, system.name))

                    success_count += 1

                    # Commit every 50 systems
                    if success_count % 50 == 0:
                        conn.commit()

                except sqlite3.Error as e:
                    failed_count += 1
                    print(f"Failed to save system '{system.name}': {e}")

            conn.commit()

        return success_count, failed_count

    """
    Retrieve all star systems from the database.

    Returns:
        List of all StarSystem objects
    """
    def find_all(self) -> List[StarSystem]:

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Load systems
            systems_dict: Dict[str, StarSystem] = {}
            cursor.execute("SELECT name, spectral_type, distance_ly FROM star_systems")

            for name, spectral_type, distance_ly in cursor.fetchall():
                systems_dict[name] = StarSystem(
                    name=name,
                    spectral_type=spectral_type or "Unknown",
                    distance_ly=float(distance_ly) if distance_ly else 0.0
                )

            # Load planets
            cursor.execute("""
                SELECT name, mass, radius, orbit_distance, system_name 
                FROM planets
            """)

            for p_name, mass, radius, orbit, sys_name in cursor.fetchall():
                if sys_name in systems_dict:
                    planet = Planet(
                        name=p_name,
                        mass=float(mass) if mass else 0.0,
                        radius=float(radius) if radius else 0.0,
                        orbit_distance=float(orbit) if orbit else 0.0
                    )
                    systems_dict[sys_name].add_planet(planet)

            return list(systems_dict.values())

    """
    Find a star system by name.

    Args:
        name: System name to search for

    Returns:
        StarSystem if found, None otherwise
    """
    def find_by_name(self, name: str) -> Optional[StarSystem]:

        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT name, spectral_type, distance_ly 
                FROM star_systems 
                WHERE name = ?
            """, (name,))

            row = cursor.fetchone()
            if not row:
                return None

            system = StarSystem(
                name=row[0],
                spectral_type=row[1] or "Unknown",
                distance_ly=float(row[2]) if row[2] else 0.0
            )

            # Load planets
            cursor.execute("""
                SELECT name, mass, radius, orbit_distance 
                FROM planets 
                WHERE system_name = ?
            """, (name,))

            for p_name, mass, radius, orbit in cursor.fetchall():
                planet = Planet(
                    name=p_name,
                    mass=float(mass) if mass else 0.0,
                    radius=float(radius) if radius else 0.0,
                    orbit_distance=float(orbit) if orbit else 0.0
                )
                system.add_planet(planet)

            return system

    """
    Count the total number of star systems.

    Returns:
        Number of systems in database
    """
    def count(self) -> int:

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM star_systems")
            return cursor.fetchone()[0]

    def delete_all(self) -> None:
        """Delete all star systems and planets from the database."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM planets")
            cursor.execute("DELETE FROM star_systems")
            conn.commit()