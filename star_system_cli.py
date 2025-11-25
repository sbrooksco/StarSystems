import argparse
from star_system_app import StarSystemApp


def main():
    parser = argparse.ArgumentParser(
        description="Star System Classifier CLI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # -----------------------------
    # create command
    # -----------------------------
    create_parser = subparsers.add_parser(
        "create", help="Create a new star system"
    )
    create_parser.add_argument("name", help="Name of the star system")
    create_parser.add_argument("star_type", help="Star classification (e.g., G2V, M1)")
    create_parser.add_argument("distance", type=float, help="Distance from Earth (light years)")
    create_parser.add_argument(
        "--planet", action="append", nargs=4, metavar=("NAME", "MASS", "RADIUS", "DISTANCE"),
        help="Add planet: NAME MASS RADIUS DISTANCE (repeatable)"
    )

    # -----------------------------
    # import/export commands
    # -----------------------------
    import_parser = subparsers.add_parser("import", help="Import systems from a CSV file")
    import_parser.add_argument("path", help="CSV file path to import")

    export_parser = subparsers.add_parser("export", help="Export systems to a CSV file")
    export_parser.add_argument("path", help="CSV file path to save")

    import_web_parser = subparsers.add_parser("import-web", help="Import systems data from NASA")

    # -----------------------------
    # search commands
    # -----------------------------
    search_mass_parser = subparsers.add_parser("search-mass", help="Search planets by minimum mass")
    search_mass_parser.add_argument("min_mass", type=float, help="Minimum mass (Earth masses)")

    search_type_parser = subparsers.add_parser("search-type", help="Search planets by type")
    search_type_parser.add_argument("planet_type", help="Planet type to search")

    search_distance_parser = subparsers.add_parser("search-distance", help="Search systems by distance")
    search_distance_parser.add_argument("distance", type=float, help="Distance from Earth (light years)")

    # -----------------------------
    # database commands
    # -----------------------------
    subparsers.add_parser("save-db", help="Save all systems to the database")
    subparsers.add_parser("load-db", help="Reload all systems from the database")
    subparsers.add_parser("list", help="List all current star systems")

    args = parser.parse_args()
    app = StarSystemApp()

    # -----------------------------
    # Command dispatch
    # -----------------------------
    if args.command == "create":
        planets = []
        if args.planet:
            for p in args.planet:
                pname, pmass, pradius, pdist = p
                planets.append({
                    "name": pname,
                    "mass": float(pmass),
                    "radius": float(pradius),
                    "distance": float(pdist),
                })
        system = app.create_star_system(args.name, args.star_type, args.distance, planets)
        print(f"Created system: {system.name}")

    elif args.command == "import":
        app.import_from_csv(args.path)

    elif args.command == "export":
        app.save_to_csv(args.path)

    elif args.command == "import-web":
        print ("Importing systems from NASA")
        app.import_from_web()

    elif args.command == "search-mass":
        results = app.search_by_mass(args.min_mass)
        if results:
            for sys_name, planet in results:
                print(f"{planet.name} ({sys_name}): {planet}")
        else:
            print("No matching planets found.")

    elif args.command == "search-type":
        results = app.search_by_type(args.planet_type)
        if results:
            for sys_name, planet in results:
                print(f"{planet.name} ({sys_name}): {planet}")
        else:
            print("No matching planets found.")

    elif args.command == "search-distance":
        results = app.search_by_distance(args.distance)
        if results:
            for system in results:
                print(f"{system.name}: {system.distance_from_earth:.2f}")
        else:
            print("No star systems found in the given radius.")

    elif args.command == "save-db":
        app.save_to_db()

    elif args.command == "load-db":
        app.load_from_db()

    elif args.command == "list":
        app.list_systems()


if __name__ == "__main__":
    main()
