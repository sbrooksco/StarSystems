import sqlite3
from models import StarSystem, Planet
from utils import load_from_csv, save_to_csv, search_planets_by_mass, search_planets_by_type, search_systems_by_distance
from database import save_system, load_systems, init_db, get_connection
from web_data import get_web_data

class StarSystemApp:

    def __init__(self):
        init_db()
        self.systems = load_systems() or [] # If you want to autoload from the database.
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

        system = StarSystem(name, star_type, distance)
        if planets:
            for p in planets:
                planet = Planet(p['name'], p['mass'], p['radius'], p['distance'])
                system.add_planet(planet)
            self.systems.append(system)
            return system
        return None

    def import_from_csv(self, path):
        imported = load_from_csv(path)
        self.systems.extend(imported)
        print(f"Imported {len(imported)} systems from {path}")

    def save_to_csv(self, path=None):
        if path is None:
            path = input("Enter file path to save CSV: ")
        try:
            save_to_csv(self.systems, path)
            print(f"Data saved to {path}")
        except Exception as e:
            print(f"Error saving CSV: {e}")

    """
    Fetches star systems from the web and adds them to self.systems.
    """
    def import_from_web(self):
        new_systems = get_web_data()
        if new_systems:
            # Avoid duplicates by system name
            existing_names = {s.name for s in self.systems}
            added_count = 0
            for s in new_systems:
                if s.name not in existing_names:
                    self.systems.append(s)
                    added_count += 1
            print(f"Imported {added_count} new star systems from the web.")
            self.save_to_db()
        else:
            print("No data fetched from the web.")

    def list_systems(self):
        if not self.systems:
            print("No star systems yet.")
            return
        for s in self.systems:
            print(f"System name: {s.name}, distance: {s.distance_from_earth} ")
            #print("\n" + str(s))

    def search_by_mass(self, min_mass):
        results = search_planets_by_mass(self.systems, min_mass)
        if results:
            for sys_name, planet in results:
                print(f"{planet.name} ({sys_name}): {planet}")
            return results
        else:
            print("No planets match that filter.")
            return None

    def search_by_type(self, planet_type):
        results = search_planets_by_type(self.systems, planet_type)
        return results

    """    
    Search for star systems that are within a given distance
    as measured in light years.
    """
    def search_by_distance(self, max_distance):
        results = search_systems_by_distance(self.systems, max_distance)
        return results

    def save_to_db(self):
        conn = get_connection()
        c = conn.cursor()

        systems_saved = 0
        failed_systems = 0

        for system in self.systems:
            try:
                save_system(system)  # this may do inserts/updates for multiple planets
                systems_saved += 1

                # Commit every 50 systems (reduces rollback impact)
                if systems_saved % 50 == 0:
                    conn.commit()

            except sqlite3.IntegrityError as e:
                failed_systems += 1
                print(f"Skipped entire system '{system.name}': {e}")

            except Exception as e:
                failed_systems += 1
                print(f"Unexpected error saving '{system.name}': {e}")

        # Final commit for remaining changes
        conn.commit()
        conn.close()

        print(f"Finished saving database: {systems_saved} systems saved, {failed_systems} failed.")

    def load_from_db(self):
        self.systems = load_systems()
        print(f"Reloaded {len(self.systems)} systems from database.")

