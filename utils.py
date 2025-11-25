from models import Planet, StarSystem
import csv

# -----------------------------
# CSV Functions
# -----------------------------
def load_from_csv(file_path):
    systems = {}
    with open(file_path, newline="") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            sys_name = row["system_name"]
            if sys_name not in systems:
                systems[sys_name] = StarSystem(
                    sys_name, row.get("star_type", "Unknown"), float(row.get("distance_ly", 0))
                )
            planet = Planet(
                row["planet_name"],
                float(row["mass"]),
                float(row["radius"]),
                float(row["orbit_distance"]),
            )
            systems[sys_name].add_planet(planet)
    return list(systems.values())


def save_to_csv(systems, file_path):
    with open(file_path, "w", newline="") as csvfile:
        fieldnames = ["system_name", "star_type", "distance_ly", "planet_name", "mass", "radius", "orbit_distance"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for system in systems:
            for planet in system.planets:
                writer.writerow({
                    "system_name": system.name,
                    "star_type": system.star_type,
                    "distance_ly": system.distance_from_earth,
                    "planet_name": planet.name,
                    "mass": planet.mass,
                    "radius": planet.radius,
                    "orbit_distance": planet.orbit_distance
                })

"""
Returns planets that are at least the specified mass.
"""
def search_planets_by_mass(systems, min_mass):
    results = []
    for system in systems:
        for planet in system.planets:
            if planet.mass > min_mass:
                results.append((system.name, planet))
    return results

"""
Returns planets of a given type.
"""
def search_planets_by_type(systems, planet_type):
    results = []
    for system in systems:
        for planet in system.planets:
            if planet.classify().lower() == planet_type.lower():
                results.append((system.name, planet))
    return results

"""
Finds star systems that are within a given distance.
Elide the systems that are report a distance of zero.
"""
def search_systems_by_distance(systems, distance):
    results = []
    for system in systems:
        if distance >= system.distance_from_earth > 0.0:
            #results.append((system.name, system.distance_from_earth))
            results.append(system)
    return results