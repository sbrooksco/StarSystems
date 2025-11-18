import requests
from models import StarSystem, Planet

M_JUPITER_TO_EARTH = 317.8
R_JUPITER_TO_EARTH = 11.2
EXOPLANET_ARCHIVE_URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"
    "query=select+hostname,pl_name,pl_bmassj,pl_radj,pl_orbper+from+ps&format=json"
)

def acquire_data():

    try:
        response = requests.get(EXOPLANET_ARCHIVE_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")

    return []

    """
    Safely get a numeric value from a dict.

    Args:
        item (dict): Source dictionary.
        key (str): Key to look up.
        default (numeric): Value to use if key is missing or None.
        multiplier (numeric): Optional factor to convert units.

    Returns:
        float: The numeric value (after applying multiplier)
    """
def safe_get(item: dict, key: str, default=0, multiplier=1.0):

    value = item.get(key)  # get the value (could be None)
    if value is None:
        value = default
    try:
        return float(value) * multiplier
    except (TypeError, ValueError):
        return default * multiplier

"""
Fetch exoplanet data from the web and convert it to StarSystem objects.
"""
def get_web_data():
    data = acquire_data()
    if not data:
        return []
    systems = {}
    for item in data:
        system_name = item.get('hostname', 'Unknown System')
        if system_name not in systems:
            systems[system_name] = StarSystem(system_name, "Unknown", 0)

        mass_earth = safe_get(item, "pl_bmassj", default=0, multiplier=M_JUPITER_TO_EARTH)
        radius_earth = safe_get(item, "pl_radj", default=0, multiplier=R_JUPITER_TO_EARTH)
        orbit_distance = safe_get(item, "pl_orbper", default=0)

        planet = Planet(
            name=item.get("pl_name"),
            mass=mass_earth,
            radius=radius_earth,
            orbit_distance=orbit_distance
        )

        systems[system_name].add_planet(planet)
    return list(systems.values())