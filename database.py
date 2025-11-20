import os
import sqlite3
from models import StarSystem, Planet

# -----------------------------
# Determine default database path
# -----------------------------
DB_PATH = os.getenv("STAR_SYSTEMS_DB")
if not DB_PATH:
    if os.getenv("RENDER") == "true":
        DB_PATH = "/tmp/star_systems.db"  # writable path on Render
    else:
        DB_PATH = "data/star_systems.db"  # local dev default


def init_db(db_path=DB_PATH):
    """Create tables if they don’t exist yet."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()

    # star_systems table
    c.execute("""
    CREATE TABLE IF NOT EXISTS star_systems (
        name TEXT PRIMARY KEY,
        star_type TEXT,
        distance_ly REAL
    )
    """)

    # planets table
    c.execute("""
    CREATE TABLE IF NOT EXISTS planets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        mass REAL,
        radius REAL,
        orbit_distance REAL,
        system_name TEXT,
        UNIQUE(name, system_name),
        FOREIGN KEY(system_name) REFERENCES star_systems(name)
    )
    """)

    conn.commit()
    conn.close()


def get_connection(db_path=None):
    """Return a sqlite3 connection to the DB."""
    return sqlite3.connect(db_path or DB_PATH)


def save_system(system: StarSystem, conn=None):
    """
    Insert or update a star system and all its planets.
    If conn is provided, use it. Otherwise, open a new connection.
    """
    own_conn = False
    if conn is None:
        conn = sqlite3.connect(DB_PATH)
        own_conn = True

    c = conn.cursor()

    # Insert or update star system
    c.execute("""
        INSERT INTO star_systems (name, star_type, distance_ly)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            star_type = excluded.star_type,
            distance_ly = excluded.distance_ly
    """, (system.name, system.star_type, system.distance_from_earth))

    # Insert or update planets
    for planet in system.planets:
        c.execute("""
            INSERT INTO planets (name, mass, radius, orbit_distance, system_name)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(name, system_name)
            DO UPDATE SET
                mass = excluded.mass,
                radius = excluded.radius,
                orbit_distance = excluded.orbit_distance
        """, (planet.name, planet.mass, planet.radius, planet.orbit_distance, system.name))

    if own_conn:
        conn.commit()
        conn.close()


def load_systems(db_path=None):
    """Load all star systems and their planets from the database."""
    path = db_path or DB_PATH
    conn = sqlite3.connect(path)
    c = conn.cursor()

    systems = {}

    # Load star systems
    c.execute("SELECT name, star_type, distance_ly FROM star_systems")
    for name, star_type, distance_ly in c.fetchall():
        # Ensure values exist
        star_type = star_type if star_type else "Unknown"
        distance_ly = float(distance_ly) if distance_ly else 0.0

        systems[name] = StarSystem(name, star_type, distance_ly)

    # Load planets and attach to systems
    c.execute("SELECT name, mass, radius, orbit_distance, system_name FROM planets")
    for p_name, mass, radius, orbit, sys_name in c.fetchall():
        mass = float(mass) if mass else 0.0
        radius = float(radius) if radius else 0.0
        orbit = float(orbit) if orbit else 0.0

        planet = Planet(p_name, mass, radius, orbit)
        if sys_name in systems:
            systems[sys_name].add_planet(planet)

    conn.close()
    return list(systems.values())


def get_planets_by_type(planet_type: str, db_path=None):
    """Return all planets that match the given type (based on classification logic)."""
    systems = load_systems(db_path=db_path)
    results = []
    for s in systems:
        for p in s.planets:
            if p.type().lower() == planet_type.lower():
                results.append((s.name, p))
    return results

