"""Service for fetching exoplanet data from NASA Exoplanet Archive."""

import requests
from typing import List, Optional
from ..models import StarSystem, Planet

# Conversion constants
M_JUPITER_TO_EARTH = 317.8
R_JUPITER_TO_EARTH = 11.2
PARSEC_TO_LY = 3.26156

# NASA Exoplanet Archive TAP query
EXOPLANET_ARCHIVE_URL = (
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync?"
    "query=select+hostname,pl_name,pl_bmassj,pl_radj,pl_orbper,"
    "st_spectype,sy_dist+from+ps&format=json"
)

"""Service for fetching and parsing exoplanet data."""
class ExoplanetService:

    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.url = EXOPLANET_ARCHIVE_URL

    """
    Fetch star systems from NASA Exoplanet Archive.

    Returns:
        List of StarSystem objects

    Raises:
        requests.RequestException: If the API request fails
    """
    def fetch_systems(self) -> List[StarSystem]:

        data = self._fetch_raw_data()
        if not data:
            return []

        return self._parse_systems(data)

    """
    Fetch raw JSON data from NASA Exoplanet Archive.

    Returns:
        List of dictionaries containing exoplanet data

    Raises:
        requests.RequestException: If the request fails
    """
    def _fetch_raw_data(self) -> List[dict]:

        try:
            response = requests.get(self.url, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching exoplanet data: {e}")
            raise

    """
    Parse raw NASA data into StarSystem objects.

    Args:
        data: Raw JSON data from NASA

    Returns:
        List of StarSystem objects with planets
    """
    def _parse_systems(self, data: List[dict]) -> List[StarSystem]:

        systems_dict = {}

        for item in data:
            # Get or create star system
            hostname = item.get("hostname") or "Unknown System"

            if hostname not in systems_dict:
                systems_dict[hostname] = self._create_system(item, hostname)

            # Add planet to system
            planet = self._create_planet(item)
            if planet:
                systems_dict[hostname].add_planet(planet)

        return list(systems_dict.values())

    """
    Create a StarSystem from NASA data.

    Args:
        item: Raw data dictionary
        hostname: Star system name

    Returns:
        StarSystem object
    """
    def _create_system(self, item: dict, hostname: str) -> StarSystem:

        spectral_type = item.get("st_spectype") or "Unknown"
        distance_pc = item.get("sy_dist")
        distance_ly = self._safe_float(distance_pc, 0.0, PARSEC_TO_LY)

        return StarSystem(
            name=hostname,
            spectral_type=spectral_type,
            distance_ly=distance_ly
        )

    """
    Create a Planet from NASA data.

    Args:
        item: Raw data dictionary

    Returns:
        Planet object or None if required data is missing
    """
    def _create_planet(self, item: dict) -> Optional[Planet]:

        planet_name = item.get("pl_name")
        if not planet_name:
            return None

        # Convert Jupiter masses/radii to Earth units
        mass_earth = self._safe_float(
            item.get("pl_bmassj"),
            0.0,
            M_JUPITER_TO_EARTH
        )

        radius_earth = self._safe_float(
            item.get("pl_radj"),
            0.0,
            R_JUPITER_TO_EARTH
        )

        orbit_distance = self._safe_float(item.get("pl_orbper"), 0.0)

        return Planet(
            name=planet_name,
            mass=mass_earth,
            radius=radius_earth,
            orbit_distance=orbit_distance
        )

    """
    Safely convert a value to float with optional multiplier.

    Args:
        value: Value to convert
        default: Default value if conversion fails
        multiplier: Multiplier to apply to converted value

    Returns:
        Converted float value or default
    """
    @staticmethod
    def _safe_float(value: any, default: float = 0.0,
                    multiplier: float = 1.0) -> float:

        if value is None or value == "":
            return default
        try:
            return float(value) * multiplier
        except (TypeError, ValueError):
            return default
