from dataclasses import dataclass
from typing import Dict


@dataclass
class Planet:
    name: str
    mass: float
    radius: float
    orbit_distance: float

    """
    Classify this planet based on its physical properties.

    Returns:
        Classification string (Dwarf Planet, Terrestrial, Super-Earth, or Gas Giant)
    """
    def classify(self) -> str:
        if self.mass <= 0.1:
            return "Dwarf Planet"
        elif self.mass < 2 and self.radius < 1.5:
            return "Terrestrial"
        elif self.mass < 10:
            return "Super-Earth"
        else:
            return "Gas Giant"

    """
    Create a dictionary representation of the planet.
    
    Returns:
        Dictionary representation of the planet.
    """
    def to_dict(self) -> Dict[str, any]:
        return {
            "name": self.name,
            "mass": self.mass,
            "radius": self.radius,
            "orbital_distance": self.orbital_distance,
            "classification": self.classify()
        }
