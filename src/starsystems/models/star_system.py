from dataclasses import dataclass, field

from .planet import Planet
from typing import List, Dict

# @dataclass auto creates the __init__, __eq__ and __repr__ methods
# Note: The defaults can still be defined as shown here.
@dataclass
class StarSystem:
    name: str
    spectral_type: str = "Unknown"
    distance_ly: float = 0.0
    planets: List[Planet] = field(default_factory=list)

    """
    Add a planet to this star system.
    Args:
        planet: Planet instance to add
    """
    def add_planet(self, planet: Planet):
        self.planets.append(planet)

    """
    Checks to see if this star system has a planet.
    Returns:
        True if this star system has at least one planet.
    """
    def has_planet(self) -> bool:
        return len(self.planets) > 0

    """
    Get the number of planets in this system.
    Returns:
        Number of planets
    """
    def planet_count(self) -> int:
        return len(self.planets)

    """
    Convert star system to dictionary representation.
    Returns:
        Dictionary with system attributes and planets
    """
    def to_dict(self) -> Dict[str, any]:
        return {
            "name": self.name,
            "spectral_type": self.spectral_type,
            "distance_ly": self.distance_ly,
            "planet_count": self.planet_count(),
            "planets": [p.to_dict() for p in self.planets]
        }

    """
    Creates/returns a string representation of this star system.
    """
    def __str__(self) -> str:
        planet_info = "\n  ".join(str(p) for p in self.planets) if self.planets else "No planets"
        return (
            f"Star System: {self.name}\n"
            f"  Spectral Type: {self.spectral_type}\n"
            f"  Distance: {self.distance_ly:.2f} ly\n"
            f"  Planets ({self.planet_count()}):\n  {planet_info}"
        )

