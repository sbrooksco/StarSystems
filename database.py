import sqlite3
from models import StarSystem, Planet

DB_FILE = "data/star_systems.db"


def init_db():
    """Create tables if they don’t exist yet."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # star_systems: name is unique so ON CONFLICT(name) works
    c.execute("""
    CREATE TABLE IF NOT EXISTS star_systems (
        name TEXT PRIMARY KEY,
        star_type TEXT,
        distance_ly REAL
    )
    """)

    # planets table linked to star_systems by system_name
    c.execute("""
    CREATE TABLE IF NOT EXISTS planets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mass REAL,
        radius REAL,
        orbit_distance REAL,
        system_name TEXT,
        FOREIGN KEY(system_name) REFERENCES star_systems(name)
    )
    """)

    conn.commit()
    conn.close()


def save_system(system: StarSystem):
    """
    Insert or update a star system and all its planets.
    If a system already exists, it’s updated (partial save).
    """
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # insert or update the star system
    c.execute("""
        INSERT INTO star_systems (name, star_type, distance_ly)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            star_type = excluded.star_type,
            distance_ly = excluded.distance_ly
    """, (system.name, system.star_type, system.distance_from_earth))

    # clear existing planets for this system before re-inserting
    c.execute("DELETE FROM planets WHERE system_name = ?", (system.name,))

    # add the planets
    for planet in system.planets:
        c.execute("""
            INSERT INTO planets (name, mass, radius, orbit_distance, system_name)
            VALUES (?, ?, ?, ?, ?)
        """, (planet.name, planet.mass, planet.radius, planet.orbit_distance, system.name))

    conn.commit()
    conn.close()


def load_systems():
    """Load all systems and planets from the database."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    c.execute("SELECT name, star_type, distance_ly FROM star_systems")
    systems = {}
    for name, star_type, distance in c.fetchall():
        systems[name] = StarSystem(name, star_type, distance)

    c.execute("SELECT name, mass, radius, orbit_distance, system_name FROM planets")
    for name, mass, radius, orbit, system_name in c.fetchall():
        planet = Planet(name, mass, radius, orbit)
        if system_name in systems:
            systems[system_name].add_planet(planet)

    conn.close()
    return list(systems.values())


def get_planets_by_type(planet_type: str):
    """Return all planets that match the given type (based on classification logic)."""
    systems = load_systems()
    results = []
    for s in systems:
        for p in s.planets:
            if p.type().lower() == planet_type.lower():
                results.append((s.name, p))
    return results


# Initialize the database when module is first imported
init_db()
