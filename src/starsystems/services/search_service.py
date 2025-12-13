"""Service for searching and filtering star systems."""

from typing import List, Optional, Set
from ..models import StarSystem


class SearchService:
    """Service for searching and filtering star systems.

    This class encapsulates all search/filter business logic,
    keeping it separate from data access and presentation layers.
    """

    def filter_systems(
            self,
            systems: List[StarSystem],
            max_distance: Optional[float] = None,
            spectral_types: Optional[List[str]] = None,
            has_planets: Optional[bool] = None,
            min_planets: Optional[int] = None
    ) -> List[StarSystem]:
        """Filter star systems by multiple criteria.

        Args:
            systems: List of star systems to filter
            max_distance: Maximum distance from Earth in light years
            spectral_types: List of spectral types to include (e.g., ['G', 'K', 'M'])
            has_planets: If True, only include systems with planets; if False, only without
            min_planets: Minimum number of planets required

        Returns:
            Filtered list of star systems
        """
        results = systems

        if max_distance is not None:
            results = self._filter_by_distance(results, max_distance)

        if spectral_types is not None and spectral_types:
            results = self._filter_by_spectral_type(results, spectral_types)

        if has_planets is not None:
            results = self._filter_by_has_planets(results, has_planets)

        if min_planets is not None:
            results = self._filter_by_min_planets(results, min_planets)

        return results

    def _filter_by_distance(
            self,
            systems: List[StarSystem],
            max_distance: float
    ) -> List[StarSystem]:
        """Filter systems within maximum distance.

        Args:
            systems: Systems to filter
            max_distance: Maximum distance in light years

        Returns:
            Systems within the distance threshold
        """
        return [
            s for s in systems
            if 0.0 < s.distance_ly <= max_distance
        ]

    def _filter_by_spectral_type(
            self,
            systems: List[StarSystem],
            spectral_types: List[str]
    ) -> List[StarSystem]:
        """Filter systems by spectral type.

        Spectral types are matched by first letter (e.g., 'G' matches 'G2V').

        Args:
            systems: Systems to filter
            spectral_types: List of spectral type prefixes (e.g., ['G', 'K', 'M'])

        Returns:
            Systems matching any of the spectral types
        """
        # Normalize spectral types to uppercase for comparison
        normalized_types = {st.upper() for st in spectral_types}

        results = []
        for system in systems:
            if system.spectral_type and system.spectral_type != "Unknown":
                # Extract first character of spectral type
                first_char = system.spectral_type[0].upper()
                if first_char in normalized_types:
                    results.append(system)

        return results

    def _filter_by_has_planets(
            self,
            systems: List[StarSystem],
            has_planets: bool
    ) -> List[StarSystem]:
        """Filter systems by whether they have planets.

        Args:
            systems: Systems to filter
            has_planets: True for systems with planets, False for systems without

        Returns:
            Filtered systems
        """
        if has_planets:
            return [s for s in systems if s.has_planet()]
        else:
            return [s for s in systems if not s.has_planet()]

    def _filter_by_min_planets(
            self,
            systems: List[StarSystem],
            min_planets: int
    ) -> List[StarSystem]:
        """Filter systems by minimum planet count.

        Args:
            systems: Systems to filter
            min_planets: Minimum number of planets

        Returns:
            Systems with at least min_planets planets
        """
        return [s for s in systems if s.planet_count() >= min_planets]

    def search_by_name(
            self,
            systems: List[StarSystem],
            query: str
    ) -> List[StarSystem]:
        """Search for systems by name (case-insensitive partial match).

        Args:
            systems: Systems to search
            query: Search query string

        Returns:
            Systems matching the query
        """
        query_lower = query.lower()
        return [
            s for s in systems
            if query_lower in s.name.lower()
        ]

    def get_statistics(self, systems: List[StarSystem]) -> dict:
        """Generate statistics about a set of star systems.

        Args:
            systems: Systems to analyze

        Returns:
            Dictionary with statistics
        """
        if not systems:
            return {
                "total_systems": 0,
                "systems_with_planets": 0,
                "total_planets": 0,
                "avg_distance": 0.0,
                "spectral_type_distribution": {}
            }

        total_planets = sum(s.planet_count() for s in systems)
        systems_with_planets = sum(1 for s in systems if s.has_planet())

        # Calculate average distance (excluding zero/unknown distances)
        valid_distances = [s.distance_ly for s in systems if s.distance_ly > 0]
        avg_distance = sum(valid_distances) / len(valid_distances) if valid_distances else 0.0

        # Spectral type distribution
        spectral_dist = {}
        for system in systems:
            if system.spectral_type and system.spectral_type != "Unknown":
                first_char = system.spectral_type[0].upper()
                spectral_dist[first_char] = spectral_dist.get(first_char, 0) + 1

        return {
            "total_systems": len(systems),
            "systems_with_planets": systems_with_planets,
            "total_planets": total_planets,
            "avg_distance": round(avg_distance, 2),
            "avg_planets_per_system": round(total_planets / len(systems), 2),
            "spectral_type_distribution": spectral_dist
        }