"""Tests for CLI application."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from argparse import Namespace
from io import StringIO
import sys

from starsystems.cli.app import StarSystemsCLI, main
from starsystems.models import StarSystem, Planet


class TestStarSystemsCLI:
    """Test cases for CLI initialization and setup."""

    def test_cli_initialization(self):
        """Test CLI initializes with required components."""
        cli = StarSystemsCLI()

        assert cli.db_conn is not None
        assert cli.repository is not None
        assert cli.exoplanet_service is not None
        assert cli.search_service is not None

    def test_create_parser(self):
        """Test argument parser is created with all commands."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        # Parser should have description
        assert 'StarSystems' in parser.description

        # Should have subparsers
        assert parser._subparsers is not None


class TestCLIInitCommand:
    """Test the 'init' command."""

    @patch('starsystems.cli.app.DatabaseConnection')
    def test_init_command(self, mock_db_class, capsys):
        """Test database initialization command."""
        # Setup mock
        mock_db = Mock()
        mock_db_class.return_value = mock_db

        cli = StarSystemsCLI()
        args = Namespace()

        # Execute init command
        cli._cmd_init(args)

        # Verify database initialization was called
        mock_db.initialize_schema.assert_called_once()

        # Check output
        captured = capsys.readouterr()
        assert "Initializing database" in captured.out
        assert "Database initialized" in captured.out


class TestCLISyncCommand:
    """Test the 'sync' command."""

    @patch('starsystems.cli.app.ExoplanetService')
    @patch('starsystems.cli.app.StarSystemRepository')
    def test_sync_command_success(self, mock_repo_class, mock_service_class, capsys):
        """Test successful sync from NASA."""
        # Setup mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Mock data
        sample_systems = [
            StarSystem("System 1", "G2V", 10.0),
            StarSystem("System 2", "K5V", 20.0),
        ]
        mock_service.fetch_systems.return_value = sample_systems
        mock_repo.save_batch.return_value = (2, 0)  # 2 success, 0 failed

        cli = StarSystemsCLI()
        args = Namespace()

        # Execute sync
        cli._cmd_sync(args)

        # Verify calls
        mock_service.fetch_systems.assert_called_once()
        mock_repo.save_batch.assert_called_once_with(sample_systems)

        # Check output
        captured = capsys.readouterr()
        assert "Fetching data" in captured.out
        assert "Retrieved 2 star systems" in captured.out
        assert "Saved 2 systems" in captured.out

    @patch('starsystems.cli.app.ExoplanetService')
    def test_sync_command_error(self, mock_service_class, capsys):
        """Test sync command handles errors."""
        # Setup mock to raise exception
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.fetch_systems.side_effect = Exception("API Error")

        cli = StarSystemsCLI()
        args = Namespace()

        # Execute sync - should exit with error
        with pytest.raises(SystemExit) as exc_info:
            cli._cmd_sync(args)

        assert exc_info.value.code == 1

        # Check error message
        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "API Error" in captured.out

    @patch('starsystems.cli.app.ExoplanetService')
    @patch('starsystems.cli.app.StarSystemRepository')
    def test_sync_command_partial_failure(self, mock_repo_class, mock_service_class, capsys):
        """Test sync with some failures."""
        mock_service = Mock()
        mock_service_class.return_value = mock_service

        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        sample_systems = [StarSystem("System 1", "G2V", 10.0)]
        mock_service.fetch_systems.return_value = sample_systems
        mock_repo.save_batch.return_value = (8, 2)  # 8 success, 2 failed

        cli = StarSystemsCLI()
        args = Namespace()

        cli._cmd_sync(args)

        captured = capsys.readouterr()
        assert "Saved 8 systems" in captured.out
        assert "Failed to save 2 systems" in captured.out


class TestCLIListCommand:
    """Test the 'list' command."""

    @patch('starsystems.cli.app.StarSystemRepository')
    def test_list_empty_database(self, mock_repo_class, capsys):
        """Test list command with empty database."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        mock_repo.find_all.return_value = []

        cli = StarSystemsCLI()
        args = Namespace(limit=None)

        cli._cmd_list(args)

        captured = capsys.readouterr()
        assert "No star systems in database" in captured.out

    @patch('starsystems.cli.app.StarSystemRepository')
    def test_list_with_systems(self, mock_repo_class, capsys):
        """Test list command with systems."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        systems = [
            StarSystem("Kepler-186", "M1V", 50.0),
            StarSystem("TRAPPIST-1", "M8V", 40.0),
        ]
        systems[0].add_planet(Planet("Kepler-186 f", 1.5, 1.2, 0.5))

        mock_repo.find_all.return_value = systems

        cli = StarSystemsCLI()
        args = Namespace(limit=None)

        cli._cmd_list(args)

        captured = capsys.readouterr()
        assert "Kepler-186" in captured.out
        assert "TRAPPIST-1" in captured.out
        assert "M1V" in captured.out
        assert "50.00 ly" in captured.out
        assert "Planets: 1" in captured.out

    @patch('starsystems.cli.app.StarSystemRepository')
    def test_list_with_limit(self, mock_repo_class, capsys):
        """Test list command with limit."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        systems = [
            StarSystem(f"System {i}", "G2V", float(i * 10))
            for i in range(10)
        ]
        mock_repo.find_all.return_value = systems

        cli = StarSystemsCLI()
        args = Namespace(limit=3)

        cli._cmd_list(args)

        captured = capsys.readouterr()
        # Should show "3 of 10"
        assert "3 of 10" in captured.out
        assert "System 0" in captured.out
        assert "System 2" in captured.out
        # System 3+ should not be shown
        assert "System 3" not in captured.out


class TestCLISearchCommand:
    """Test the 'search' command."""

    def test_search_by_distance(self, capsys):
        """Test search by distance."""
        cli = StarSystemsCLI()

        # Setup data
        all_systems = [
            StarSystem("Nearby", "G2V", 10.0),
            StarSystem("Far", "K5V", 100.0),
        ]
        filtered = [all_systems[0]]  # Only nearby

        # Mock the CLI's instances directly
        cli.repository.find_all = Mock(return_value=all_systems)
        cli.search_service.filter_systems = Mock(return_value=filtered)

        args = Namespace(
            distance=50.0,
            spectral_type=None,
            has_planets=False,
            no_planets=False,
            min_planets=None,
            name=None
        )

        cli._cmd_search(args)

        # Verify filter was called with correct parameters
        cli.search_service.filter_systems.assert_called_once()
        call_args = cli.search_service.filter_systems.call_args
        assert call_args[1]['max_distance'] == 50.0

        captured = capsys.readouterr()
        assert "Found 1 matching systems" in captured.out
        assert "Nearby" in captured.out

    def test_search_by_spectral_type(self, capsys):
        """Test search by spectral type."""
        cli = StarSystemsCLI()

        systems = [StarSystem("G Star", "G2V", 10.0)]
        cli.repository.find_all = Mock(return_value=systems)
        cli.search_service.filter_systems = Mock(return_value=systems)

        args = Namespace(
            distance=None,
            spectral_type=['G', 'K'],
            has_planets=False,
            no_planets=False,
            min_planets=None,
            name=None
        )

        cli._cmd_search(args)

        call_args = cli.search_service.filter_systems.call_args
        assert call_args[1]['spectral_types'] == ['G', 'K']

    def test_search_has_planets(self, capsys):
        """Test search for systems with planets."""
        cli = StarSystemsCLI()

        system = StarSystem("With Planets", "G2V", 10.0)
        system.add_planet(Planet("Planet", 1.0, 1.0, 1.0))

        cli.repository.find_all = Mock(return_value=[system])
        cli.search_service.filter_systems = Mock(return_value=[system])

        args = Namespace(
            distance=None,
            spectral_type=None,
            has_planets=True,
            no_planets=False,
            min_planets=None,
            name=None
        )

        cli._cmd_search(args)

        call_args = cli.search_service.filter_systems.call_args
        assert call_args[1]['has_planets'] is True

        captured = capsys.readouterr()
        assert "Planet" in captured.out
        assert "Terrestrial" in captured.out  # Classification

    def test_search_by_name(self, capsys):
        """Test search by system name."""
        cli = StarSystemsCLI()

        systems = [StarSystem("Kepler-186", "G2V", 50.0)]
        cli.repository.find_all = Mock(return_value=systems)
        cli.search_service.filter_systems = Mock(return_value=systems)
        cli.search_service.search_by_name = Mock(return_value=systems)

        args = Namespace(
            distance=None,
            spectral_type=None,
            has_planets=False,
            no_planets=False,
            min_planets=None,
            name="Kepler"
        )

        cli._cmd_search(args)

        # Verify name search was called
        cli.search_service.search_by_name.assert_called_once_with(systems, "Kepler")

    def test_search_no_results(self, capsys):
        """Test search with no matching results."""
        cli = StarSystemsCLI()

        cli.repository.find_all = Mock(return_value=[])
        cli.search_service.filter_systems = Mock(return_value=[])

        args = Namespace(
            distance=10.0,
            spectral_type=None,
            has_planets=False,
            no_planets=False,
            min_planets=None,
            name=None
        )

        cli._cmd_search(args)

        captured = capsys.readouterr()
        assert "No systems match the search criteria" in captured.out


class TestCLIInfoCommand:
    """Test the 'info' command."""

    def test_info_system_found(self, capsys):
        """Test info command with existing system."""
        cli = StarSystemsCLI()

        system = StarSystem("Kepler-186", "M1V", 50.0)
        system.add_planet(Planet("Kepler-186 f", 1.5, 1.2, 0.5))

        cli.repository.find_by_name = Mock(return_value=system)

        args = Namespace(name="Kepler-186")

        cli._cmd_info(args)

        cli.repository.find_by_name.assert_called_once_with("Kepler-186")

        captured = capsys.readouterr()
        assert "Kepler-186" in captured.out
        assert "M1V" in captured.out
        assert "50.00 ly" in captured.out
        assert "Kepler-186 f" in captured.out

    def test_info_system_not_found(self, capsys):
        """Test info command with non-existent system."""
        cli = StarSystemsCLI()
        cli.repository.find_by_name = Mock(return_value=None)

        args = Namespace(name="Nonexistent")

        cli._cmd_info(args)

        captured = capsys.readouterr()
        assert "not found" in captured.out
        assert "Nonexistent" in captured.out


class TestCLIStatsCommand:
    """Test the 'stats' command."""

    @patch('starsystems.cli.app.StarSystemRepository')
    @patch('starsystems.cli.app.SearchService')
    def test_stats_command(self, mock_search_class, mock_repo_class, capsys):
        """Test statistics command."""
        mock_repo = Mock()
        mock_search = Mock()
        mock_repo_class.return_value = mock_repo
        mock_search_class.return_value = mock_search

        systems = [
            StarSystem("System 1", "G2V", 10.0),
            StarSystem("System 2", "K5V", 20.0),
        ]
        systems[0].add_planet(Planet("Planet 1", 1.0, 1.0, 1.0))
        systems[0].add_planet(Planet("Planet 2", 2.0, 1.5, 2.0))

        mock_repo.find_all.return_value = systems

        stats = {
            'total_systems': 2,
            'systems_with_planets': 1,
            'total_planets': 2,
            'avg_distance': 15.0,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'G': 1, 'K': 1}
        }
        mock_search.get_statistics.return_value = stats

        cli = StarSystemsCLI()
        args = Namespace()

        cli._cmd_stats(args)

        mock_search.get_statistics.assert_called_once_with(systems)

        captured = capsys.readouterr()
        assert "Database Statistics" in captured.out
        assert "Total Systems: 2" in captured.out
        assert "Systems with Planets: 1" in captured.out
        assert "Total Planets: 2" in captured.out
        assert "Average Distance: 15.00 ly" in captured.out
        assert "Spectral Type Distribution" in captured.out
        assert "G: 1" in captured.out
        assert "K: 1" in captured.out


class TestCLICommandParsing:
    """Test command-line argument parsing."""

    def test_parser_init_command(self):
        """Test parser recognizes init command."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        args = parser.parse_args(['init'])
        assert args.command == 'init'

    def test_parser_sync_command(self):
        """Test parser recognizes sync command."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        args = parser.parse_args(['sync'])
        assert args.command == 'sync'

    def test_parser_list_command_with_limit(self):
        """Test parser handles list command with limit."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        args = parser.parse_args(['list', '--limit', '10'])
        assert args.command == 'list'
        assert args.limit == 10

    def test_parser_search_command_full(self):
        """Test parser handles search with all options."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        args = parser.parse_args([
            'search',
            '--distance', '100',
            '--spectral-type', 'G', 'K', 'M',
            '--has-planets',
            '--min-planets', '2',
            '--name', 'Kepler'
        ])

        assert args.command == 'search'
        assert args.distance == 100.0
        assert args.spectral_type == ['G', 'K', 'M']
        assert args.has_planets is True
        assert args.min_planets == 2
        assert args.name == 'Kepler'

    def test_parser_info_command(self):
        """Test parser handles info command."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        args = parser.parse_args(['info', 'Kepler-186'])
        assert args.command == 'info'
        assert args.name == 'Kepler-186'

    def test_parser_stats_command(self):
        """Test parser recognizes stats command."""
        cli = StarSystemsCLI()
        parser = cli._create_parser()

        args = parser.parse_args(['stats'])
        assert args.command == 'stats'


class TestCLIMainFunction:
    """Test the main entry point."""

    @patch('starsystems.cli.app.StarSystemsCLI')
    def test_main_function(self, mock_cli_class):
        """Test main function creates CLI and runs it."""
        mock_cli = Mock()
        mock_cli_class.return_value = mock_cli

        main()

        mock_cli_class.assert_called_once()
        mock_cli.run.assert_called_once()

    @patch('sys.argv', ['starsystems'])
    @patch('starsystems.cli.app.StarSystemsCLI')
    def test_main_no_args_shows_help(self, mock_cli_class, capsys):
        """Test running with no arguments shows help."""
        mock_cli = StarSystemsCLI()
        mock_cli_class.return_value = mock_cli

        # Run with no arguments should show help
        parser = mock_cli._create_parser()
        args = parser.parse_args([])

        # Should not have 'func' attribute when no command given
        assert not hasattr(args, 'func')


class TestCLIIntegration:
    """Integration tests for CLI."""

    @patch('sys.argv', ['starsystems', 'init'])
    @patch('starsystems.cli.app.DatabaseConnection')
    def test_full_init_workflow(self, mock_db_class):
        """Test complete init workflow from command line."""
        mock_db = Mock()
        mock_db_class.return_value = mock_db

        cli = StarSystemsCLI()
        cli.run()

        mock_db.initialize_schema.assert_called_once()