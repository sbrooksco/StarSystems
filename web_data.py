import requests
from models import StarSystem, Planet

M_JUPITER_TO_EARTH = 317.8
R_JUPITER_TO_EARTH = 11.2
PARSEC_TO_LY = 3.26156

# Updated NASA Query - includes distance + star type
EXOPLANET_ARCHIVE_URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"
    "query=select+hostname,pl_name,pl_bmassj,pl_radj,pl_orbper,"
    "st_spectype,sy_dist+from+ps&format=json"
)

def acquire_data():
    try:
        response = requests.get(EXOPLANET_ARCHIVE_URL, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

def safe_float(value, default=0.0, multiplier=1.0):
    """Convert value to float with optional multiplier."""
    if value is None or value == "":
        return default
    try:
        return float(value) * multiplier
    except (TypeError, ValueError):
        return default

def get_web_data():
    data = acquire_data()
    if not data:
        print("No data received from NASA.")
        return []

    systems = {}

    for item in data:
        name = item.get("hostname") or "Unknown System"

        if name not in systems:
            star_type = item.get("st_spectype") or "Unknown"

            distance_pc = item.get("sy_dist")
            distance_ly = safe_float(distance_pc, default=0.0, multiplier=PARSEC_TO_LY)

            systems[name] = StarSystem(name, star_type, distance_ly)

        mass_earth = safe_float(item.get("pl_bmassj"), default=0.0, multiplier=M_JUPITER_TO_EARTH)
        radius_earth = safe_float(item.get("pl_radj"), default=0.0, multiplier=R_JUPITER_TO_EARTH)
        orbit_distance = safe_float(item.get("pl_orbper"), default=0.0)

        planet_name = item.get("pl_name") or "Unnamed Planet"
        planet = Planet(planet_name, mass_earth, radius_earth, orbit_distance)

        systems[name].add_planet(planet)

    return list(systems.values())
