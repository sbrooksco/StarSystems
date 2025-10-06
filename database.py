import sqlite3
from models import StarSystem, Planet

DB_FILE = "star_system.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS star_systems (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            star_type TEXT,
            distance_ly REAL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS planets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            mass REAL,
            radius REAL,
            orbit_distance REAL,
            system_id INTEGER,
            FOREIGN KEY(system_id) REFERENCES star_systems(id),
            UNIQUE(name, system_id)
        )
    """)

    conn.commit()
    conn.close()

def save_star_system(system: StarSystem):
    """Insert or update a star system and its planets."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Insert or update the star system
    c.execute("""
        INSERT OR IGNORE INTO star_systems (name, star_type, distance_ly)
        VALUES (?, ?, ?)
        ON CONFLICT(name) DO UPDATE SET
            star_type = excluded.star_type,
            distance_ly = excluded.distance_ly
    """, (system.name, system.star_type, system.distance_from_earth))

    # Get the system id
    c.execute("SELECT id FROM star_systems WHERE name = ?", (system.name,))
    system_id = c.fetchone()[0]

    # Load existing planet names for this system
    c.execute("SELECT name FROM planets WHERE system_id = ?", (system_id,))
    existing_planets = {row[0] for row in c.fetchall()}

    # Insert or update planets
    for p in system.planets:
        if p.name in existing_planets:
            # update existing planet
            c.execute("""
                UPDATE planets
                SET mass = ?, radius = ?, orbit_distance = ?
                WHERE name = ? AND system_id = ?
            """, (p.mass, p.radius, p.orbit_distance, p.name, system_id))
        else:
            # insert new planet
            c.execute("""
                INSERT INTO planets (name, mass, radius, orbit_distance, system_id)
                VALUES (?, ?, ?, ?, ?)
            """, (p.name, p.mass, p.radius, p.orbit_distance, system_id))

    # Optionally: delete planets that no longer exist in memory
    # (uncomment this block if you want deletions to sync automatically)
    #
    # for old_name in existing_planets - {p.name for p in system.planets}:
    #     c.execute("DELETE FROM planets WHERE name = ? AND system_id = ?", (old_name, system_id))

    conn.commit()
    conn.close()



def load_all_systems():
    """Load all star systems and their planets."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    systems = {}
    for row in c.execute("SELECT id, name, star_type, distance_ly FROM star_systems"):
        sys_id, name, star_type, distance = row
        systems[sys_id] = StarSystem(name, star_type, distance)

    for row in c.execute("SELECT name, mass, radius, orbit_distance, system_id FROM planets"):
        name, mass, radius, orbit, sys_id = row
        planet = Planet(name, mass, radius, orbit)
        if sys_id in systems:
            systems[sys_id].add_planet(planet)

    conn.close()
    return list(systems.values())


def update_planet(system_name, planet: Planet):
    """Update a single planet’s data without re-saving the whole system."""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT id FROM star_systems WHERE name = ?", (system_name,))
    result = c.fetchone()
    if not result:
        raise ValueError(f"System {system_name} not found.")
    system_id = result[0]

    c.execute("""
        UPDATE planets
        SET mass = ?, radius = ?, orbit_distance = ?
        WHERE name = ? AND system_id = ?
    """, (planet.mass, planet.radius, planet.orbit_distance, planet.name, system_id))

    conn.commit()
    conn.close()