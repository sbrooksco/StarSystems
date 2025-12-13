"""Command-line interface for StarSystems."""

import argparse
import sys
from typing import List, Optional
from ..database import DatabaseConnection, StarSystemRepository
from ..services import ExoplanetService, SearchService
from ..models import StarSystem


class StarSystemsCLI:
    """Command-line interface for managing and searching star systems."""

    def __init__(self):
        self.db_conn = DatabaseConnection()
        self.repository = StarSystemRepository(self.db_conn)
        self.exoplanet_service = ExoplanetService()
        self.search_service = SearchService()

    def run(self):
        """Main entry point for CLI."""
        parser = self._create_parser()
        args = parser.parse_args()

        if hasattr(args, 'func'):
            args.func(args)
        else:
            parser.print_help()

    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser with subcommands."""
        parser = argparse.ArgumentParser(
            description='StarSystems - Exoplanet database manager'
        )

        subparsers = parser.add_subparsers(title='commands', dest='command')

        # Initialize command
        init_parser = subparsers.add_parser(
            'init',
            help='Initialize the database'
        )
        init_parser.set_defaults(func=self._cmd_init)

        # Sync command
        sync_parser = subparsers.add_parser(
            'sync',
            help='Fetch and sync data from NASA Exoplanet Archive'
        )
        sync_parser.set_defaults(func=self._cmd_sync)

        # List command
        list_parser = subparsers.add_parser(
            'list',
            help='List all star systems'
        )
        list_parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of results'
        )
        list_parser.set_defaults(func=self._cmd_list)

        # Search command
        search_parser = subparsers.add_parser(
            'search',
            help='Search star systems'
        )
        search_parser.add_argument(
            '--distance',
            type=float,
            help='Maximum distance in light years'
        )
        search_parser.add_argument(
            '--spectral-type',
            nargs='+',
            help='Spectral types (e.g., G K M)'
        )
        search_parser.add_argument(
            '--has-planets',
            action='store_true',
            help='Only systems with planets'
        )
        search_parser.add_argument(
            '--no-planets',
            action='store_true',
            help='Only systems without planets'
        )
        search_parser.add_argument(
            '--min-planets',
            type=int,
            help='Minimum number of planets'
        )
        search_parser.add_argument(
            '--name',
            type=str,
            help='Search by system name'
        )
        search_parser.set_defaults(func=self._cmd_search)

        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Show information about a specific system'
        )
        info_parser.add_argument(
            'name',
            help='System name'
        )
        info_parser.set_defaults(func=self._cmd_info)

        # Stats command
        stats_parser = subparsers.add_parser(
            'stats',
            help='Show database statistics'
        )
        stats_parser.set_defaults(func=self._cmd_stats)

        return parser

    def _cmd_init(self, args):
        """Initialize the database."""
        print("Initializing database...")
        self.db_conn.initialize_schema()
        print(f"✓ Database initialized")

    def _cmd_sync(self, args):
        """Sync data from NASA Exoplanet Archive."""
        print("Fetching data from NASA Exoplanet Archive...")

        try:
            systems = self.exoplanet_service.fetch_systems()
            print(f"Retrieved {len(systems)} star systems")

            print("Saving to database...")
            success, failed = self.repository.save_batch(systems)

            print(f"✓ Saved {success} systems")
            if failed > 0:
                print(f"⚠ Failed to save {failed} systems")

        except Exception as e:
            print(f"✗ Error: {e}")
            sys.exit(1)

    def _cmd_list(self, args):
        """List all star systems."""
        systems = self.repository.find_all()

        if not systems:
            print("No star systems in database. Run 'sync' first.")
            return

        limit = args.limit if args.limit else len(systems)

        print(f"\nStar Systems ({min(limit, len(systems))} of {len(systems)}):\n")
        for system in systems[:limit]:
            print(f"  {system.name}")
            print(f"    Type: {system.spectral_type}, Distance: {system.distance_ly:.2f} ly")
            print(f"    Planets: {system.planet_count()}")
            print()

    def _cmd_search(self, args):
        """Search star systems with filters."""
        systems = self.repository.find_all()

        # Determine has_planets filter
        has_planets = None
        if args.has_planets:
            has_planets = True
        elif args.no_planets:
            has_planets = False

        # Apply filters
        results = self.search_service.filter_systems(
            systems,
            max_distance=args.distance,
            spectral_types=args.spectral_type,
            has_planets=has_planets,
            min_planets=args.min_planets
        )

        # Apply name search if provided
        if args.name:
            results = self.search_service.search_by_name(results, args.name)

        # Display results
        if not results:
            print("No systems match the search criteria.")
            return

        print(f"\nFound {len(results)} matching systems:\n")
        for system in results:
            print(f"  {system.name}")
            print(f"    Type: {system.spectral_type}, Distance: {system.distance_ly:.2f} ly")
            print(f"    Planets: {system.planet_count()}")
            if system.planets:
                for planet in system.planets:
                    print(f"      - {planet.name} ({planet.classify()})")
            print()

    def _cmd_info(self, args):
        """Show detailed information about a system."""
        system = self.repository.find_by_name(args.name)

        if not system:
            print(f"System '{args.name}' not found.")
            return

        print(f"\n{system}\n")

    def _cmd_stats(self, args):
        """Show database statistics."""
        systems = self.repository.find_all()
        stats = self.search_service.get_statistics(systems)

        print("\nDatabase Statistics:\n")
        print(f"  Total Systems: {stats['total_systems']}")
        print(f"  Systems with Planets: {stats['systems_with_planets']}")
        print(f"  Total Planets: {stats['total_planets']}")
        print(f"  Average Distance: {stats['avg_distance']:.2f} ly")
        print(f"  Average Planets per System: {stats['avg_planets_per_system']:.2f}")

        if stats['spectral_type_distribution']:
            print("\n  Spectral Type Distribution:")
            for stype, count in sorted(stats['spectral_type_distribution'].items()):
                print(f"    {stype}: {count}")
        print()


def main():
    """Entry point for CLI."""
    cli = StarSystemsCLI()
    cli.run()


if __name__ == '__main__':
    main()