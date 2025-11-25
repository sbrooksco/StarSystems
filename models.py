# -----------------------------
# Data Model Classes
# -----------------------------
class Planet:
    def __init__(self, name, mass, radius, orbit_distance):
        self.name = name
        self.mass = mass
        self.radius = radius
        self.orbit_distance = orbit_distance

    def classify(self):
        if self.mass < 0.1:
            return "Dwarf Planet"
        elif self.mass < 2 and self.radius < 1.5:
            return "Terrestrial"
        elif self.mass < 10:
            return "Super-Earth"
        else:
            return "Gas Giant"

    def to_dict(self):
        return {
            "name": self.name,
            "mass": self.mass,
            "radius": self.radius,
            "orbit_distance": self.orbit_distance
        }

    def __str__(self):
        return (
            f"{self.name}: Mass={self.mass} Earth masses, "
            f"Radius={self.radius} Earth radii, "
            f"Orbit={self.orbit_distance} AU, "
            f"({self.classify()})"
        )

class StarSystem:
    def __init__(self, name, star_type="Unknown", distance_from_earth=0.0):
        self.name = name
        self.star_type = star_type
        self.distance_from_earth = distance_from_earth
        self.planets = []

    def add_planet(self, planet):
        self.planets.append(planet)

    def to_dict(self):
        return {
            "name": self.name,
            "star_type": self.star_type,
            "distance_from_earth": self.distance_from_earth,
            "planets": [p.to_dict() for p in self.planets]
        }

    def __str__(self):
        planets_info = "\n ".join(str(p) for p in self.planets)
        return (
            f"Star System: {self.name}\n "
            f"({self.star_type}, {self.distance_from_earth} ly)\n "
            f"  Planets:\n {planets_info if planets_info else 'No planets yet.'}"
        )