from models import StarSystem, Planet
from utils import load_from_csv, save_to_csv, search_planets_by_mass, search_planets_by_type
from database import save_star_system, load_all_systems, init_db


# -----------------------------
# Interactive Functions
# -----------------------------
def create_star_system():
    name = input("Enter star system name: ")
    star_type = input("Enter star type (e.g. G2V, M1): ")
    distance = float(input("Enter distance from Earth (light years): "))

    system = StarSystem(name, star_type, distance)

    while True:
        add_planet = input("Add a planet? (y/n): ").lower()
        if add_planet != "y":
            break
        pname = input("  Planet name: ")
        pmass = float(input("  Mass (Earth masses): "))
        pradius = float(input("  Radius (Earth radii): "))
        pdist = float(input("  Orbit distance (AU): "))
        system.add_planet(Planet(pname, pmass, pradius, pdist))

    return system




# -----------------------------
# Main Menu
# -----------------------------
def main():

    init_db()
    systems = load_all_systems()
    print(f"loaded {len(systems)} star systems from database")

    while True:
        print("\n=== Star System Classifier ===")
        print("1. Create new star system")
        print("2. Import from CSV")
        print("3. List all systems")
        print("4. Save to CSV")
        print("5. Search planets by mass")
        print("6. Search planets by type")
        print("7. Save to database")
        print("8. Load from database")
        print("9. Exit")

        choice = input("Select an option: ").strip()

        if choice == "1":
            system = create_star_system()
            systems.append(system)
            print(f"Added system: {system.name}")
        elif choice == "2":
            path = input("Enter CSV file path to import: ")
            try:
                imported = load_from_csv(path)
                systems.extend(imported)
                print(f"Imported {len(imported)} systems from {path}")
            except Exception as e:
                print(f"Error importing CSV: {e}")
        elif choice == "3":
            if not systems:
                print("No star systems yet.")
            for s in systems:
                print("\n" + str(s))
        elif choice == "4":
            path = input("Enter file path to save CSV: ")
            try:
                save_to_csv(systems, path)
                print(f"Data saved to {path}")
            except Exception as e:
                print(f"Error saving CSV: {e}")
        elif choice == "5":
            min_mass = float(input("Show planets with mass greater than: "))
            results = search_planets_by_mass(systems, min_mass)
            if results:
                for sys_name, planet in results:
                    print(f"{planet.name} ({sys_name}): {planet}")
            else:
                print("No planets match that filter.")
        elif choice == "6":
            planet_type = input("Enter planet type: ")
            results = search_planets_by_type(systems, planet_type)
            if results:
                for sys_name, planet in results:
                    print(f"{planet.name} ({sys_name}): {planet}")
            else:
                print("No planets match that type.")
        elif choice == "7":
            for system in systems:
                save_star_system(system)
            print("All systems saved to database.")
        elif choice == "8":
            systems = load_all_systems()
            print(f"Reloaded {len(systems)} systems from database.")
        elif choice == "9":
            print("Goodbye!")
            break
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
