from models import StarSystem, Planet
from utils import load_from_csv, save_to_csv, search_planets_by_mass, search_planets_by_type
from database import save_system, load_systems, init_db

class StarSystemApp:

    def __init__(self):
        init_db()
        self.systems = load_systems()
        print(f"loaded {len(self.systems)} star systems from database")

    """
    Create a new StarSystem programmatically.

    Args:
        name (str): Name of the star system.
        star_type (str): Star classification (e.g., 'G2V', 'M1').
        distance (float): Distance from Earth in light years.
        planets (list[dict]): Optional list of planet data.
    """
    def create_star_system(self, name, star_type, distance, planets=None):
        #name = input("Enter star system name: ")
        #star_type = input("Enter star type (e.g. G2V, M1): ")
        #distance = float(input("Enter distance from Earth (light years): "))

        system = StarSystem(name, star_type, distance)
        if planets:
            for p in planets:
                planet = Planet(p['name'], p['mass'], p['radius'], p['distance'])
                system.add_planet(planet)
            self.systems.append(system)
            return system

    def import_from_csv(self, path):
        imported = load_from_csv(path)
        self.systems.extend(imported)
        print(f"Imported {len(imported)} systems from {path}")

    def list_systems(self):
        if not self.systems:
            print("No star systems yet.")
            return
        for s in self.systems:
            print("\n" + str(s))

    def save_to_csv(self):
        path = input("Enter file path to save CSV: ")
        try:
            save_to_csv(self.systems, path)
            print(f"Data saved to {path}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

    def search_by_mass(self, min_mass):
        results = search_planets_by_mass(self.systems, min_mass)
        if results:
            for sys_name, planet in results:
                print(f"{planet.name} ({sys_name}): {planet}")
            return results
        else:
            print("No planets match that filter.")
            return None

    def search_by_type(self):
        planet_type = input("Enter planet type: ")
        results = search_planets_by_type(self.systems, planet_type)
        if results:
            for sys_name, planet in results:
                print(f"{planet.name} ({sys_name}): {planet}")
        else:
            print("No planets match that type.")

    def save_to_db(self):
        for system in self.systems:
            save_system(system)
        print("All systems saved to database.")

    def load_from_db(self):
        self.systems = load_systems()
        print(f"Reloaded {len(self.systems)} systems from database.")

