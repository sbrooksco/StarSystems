"""Tests for FastAPI web application."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from fastapi.testclient import TestClient

from starsystems.web.app import app, import_status
from starsystems.models import StarSystem, Planet


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def sample_systems():
    """Create sample systems for testing."""
    systems = []

    # System with planets
    kepler = StarSystem("Kepler-186", "M1V", 50.0)
    kepler.add_planet(Planet("Kepler-186 f", 1.5, 1.2, 0.5))
    kepler.add_planet(Planet("Kepler-186 b", 0.8, 0.9, 0.3))
    systems.append(kepler)

    # System without planets
    vega = StarSystem("Vega", "A0V", 25.0)
    systems.append(vega)

    # Another system with planets
    trappist = StarSystem("TRAPPIST-1", "M8V", 40.0)
    trappist.add_planet(Planet("TRAPPIST-1 e", 0.9, 0.95, 0.4))
    systems.append(trappist)

    return systems


@pytest.fixture
def complete_stats():
    """Create complete statistics dictionary for template rendering."""
    return {
        'total_systems': 3,
        'systems_with_planets': 2,
        'total_planets': 3,
        'avg_distance': 38.33,
        'avg_planets_per_system': 1.0,
        'spectral_type_distribution': {'M': 2, 'A': 1}
    }


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock()


@pytest.fixture
def mock_search_service():
    """Create a mock search service."""
    return Mock()


class TestRootEndpoint:
    """Test the root endpoint."""

    def test_root_redirects_to_systems(self, client):
        """Test that root redirects to /systems."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/systems"


class TestSystemsPage:
    """Test the main systems page."""

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_loads(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test systems page loads successfully."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'M': 2, 'A': 1}
        }

        response = client.get("/systems")

        assert response.status_code == 200
        assert "Kepler-186" in response.text
        assert "TRAPPIST-1" in response.text
        assert "Vega" in response.text

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_with_distance_filter(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test filtering by distance."""
        # Only nearby systems
        nearby = [sample_systems[1]]  # Vega at 25 ly

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = nearby
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 0,
            'total_planets': 0,
            'avg_distance': 25.0,
            'avg_planets_per_system': 0.0,
            'spectral_type_distribution': {}
        }

        response = client.get("/systems?distance=30")

        assert response.status_code == 200
        # Verify filter was applied
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['max_distance'] == 30.0

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_with_spectral_type_filter(self, mock_search, mock_repo, client, sample_systems,
                                                    complete_stats):
        """Test filtering by spectral type."""
        m_stars = [sample_systems[0], sample_systems[2]]  # Both M-type

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = m_stars
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 45.0,
            'avg_planets_per_system': 1.5,
            'spectral_type_distribution': {'M': 2}
        }

        response = client.get("/systems?spectral_type=M")

        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['spectral_types'] == ['M']

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_with_multiple_spectral_types(self, mock_search, mock_repo, client, sample_systems,
                                                       complete_stats):
        """Test filtering by multiple spectral types."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'M': 2, 'A': 1}
        }

        response = client.get("/systems?spectral_type=M,A,G")

        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['spectral_types'] == ['M', 'A', 'G']

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_filter_has_planets_true(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test filtering for systems with planets."""
        with_planets = [sample_systems[0], sample_systems[2]]

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = with_planets
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 45.0,
            'avg_planets_per_system': 1.5,
            'spectral_type_distribution': {'M': 2}
        }

        response = client.get("/systems?has_planets=true")

        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['has_planets'] is True

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_filter_has_planets_false(self, mock_search, mock_repo, client, sample_systems,
                                                   complete_stats):
        """Test filtering for systems without planets."""
        without_planets = [sample_systems[1]]  # Vega

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = without_planets
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 0,
            'total_planets': 0,
            'avg_distance': 25.0,
            'avg_planets_per_system': 0.0,
            'spectral_type_distribution': {'A': 1}
        }

        response = client.get("/systems?has_planets=false")

        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['has_planets'] is False

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_search_by_name(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test name search."""
        kepler_only = [sample_systems[0]]

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.search_by_name.return_value = kepler_only
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'M': 2, 'A': 1}
        }

        response = client.get("/systems?name=Kepler")

        assert response.status_code == 200
        mock_search.search_by_name.assert_called_once()


class TestAPISystemsEndpoint:
    """Test the /api/systems endpoint."""

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_api_systems_returns_json(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test API returns JSON data."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems

        response = client.get("/api/systems")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3
        assert data[0]['name'] == 'Kepler-186'

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_api_systems_with_filters(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test API with query parameters."""
        filtered = [sample_systems[0]]

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = filtered

        response = client.get("/api/systems?distance=50&spectral_type=M&has_planets=true")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1

        # Verify filters were applied
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['max_distance'] == 50.0
        assert call_args[1]['spectral_types'] == ['M']
        assert call_args[1]['has_planets'] is True

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_api_systems_with_min_planets(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test filtering by minimum planet count."""
        multi_planet = [sample_systems[0]]  # Kepler-186 has 2 planets

        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = multi_planet

        response = client.get("/api/systems?min_planets=2")

        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['min_planets'] == 2

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_api_systems_with_name_search(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test name search in API."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.search_by_name.return_value = [sample_systems[2]]

        response = client.get("/api/systems?name=TRAPPIST")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]['name'] == 'TRAPPIST-1'

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_api_systems_with_limit(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test result limiting."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems

        response = client.get("/api/systems?limit=2")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2


class TestAPISystemDetailEndpoint:
    """Test the /api/systems/{name} endpoint."""

    @patch('starsystems.web.app.repository')
    def test_api_system_detail_found(self, mock_repo, client, sample_systems):
        """Test getting details of existing system."""
        mock_repo.find_by_name.return_value = sample_systems[0]

        response = client.get("/api/systems/Kepler-186")

        assert response.status_code == 200
        data = response.json()
        assert data['name'] == 'Kepler-186'
        assert data['spectral_type'] == 'M1V'
        assert data['distance_ly'] == 50.0
        assert data['planet_count'] == 2
        assert len(data['planets']) == 2

    @patch('starsystems.web.app.repository')
    def test_api_system_detail_not_found(self, mock_repo, client):
        """Test 404 for non-existent system."""
        mock_repo.find_by_name.return_value = None

        response = client.get("/api/systems/NonexistentSystem")

        assert response.status_code == 404
        assert response.json()['detail'] == 'System not found'


class TestAPIStatsEndpoint:
    """Test the /api/stats endpoint."""

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_api_stats(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test statistics endpoint."""
        mock_repo.find_all.return_value = sample_systems
        stats = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'M': 2, 'A': 1}
        }
        mock_search.get_statistics.return_value = stats

        response = client.get("/api/stats")

        assert response.status_code == 200
        data = response.json()
        assert data['total_systems'] == 3
        assert data['systems_with_planets'] == 2
        assert data['total_planets'] == 3


class TestAdminSyncEndpoint:
    """Test the /admin/sync endpoint."""

    @patch('starsystems.web.app.exoplanet_service')
    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.ADMIN_PASSWORD', 'test_password')
    def test_admin_sync_success(self, mock_repo, mock_service, client, sample_systems):
        """Test successful manual sync."""
        mock_service.fetch_systems.return_value = sample_systems
        mock_repo.save_batch.return_value = (3, 0)

        response = client.post(
            "/admin/sync",
            data={"admin_key": "test_password"},
            follow_redirects=False
        )

        assert response.status_code == 303  # See Other redirect
        assert response.headers["location"] == "/systems"
        mock_service.fetch_systems.assert_called_once()
        mock_repo.save_batch.assert_called_once()

    @patch('starsystems.web.app.ADMIN_PASSWORD', 'correct_password')
    def test_admin_sync_wrong_password(self, client):
        """Test sync with incorrect password."""
        response = client.post(
            "/admin/sync",
            data={"admin_key": "wrong_password"}
        )

        assert response.status_code == 401
        assert response.json()['detail'] == 'Unauthorized'

    @patch('starsystems.web.app.exoplanet_service')
    @patch('starsystems.web.app.ADMIN_PASSWORD', 'test_password')
    def test_admin_sync_api_error(self, mock_service, client):
        """Test sync when API fails."""
        mock_service.fetch_systems.side_effect = Exception("API Error")

        response = client.post(
            "/admin/sync",
            data={"admin_key": "test_password"}
        )

        assert response.status_code == 500
        assert "API Error" in response.json()['detail']


class TestHealthCheckEndpoint:
    """Test the /health endpoint."""

    @patch('starsystems.web.app.repository')
    def test_health_check(self, mock_repo, client):
        """Test health check returns correct status."""
        mock_repo.count.return_value = 42

        response = client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'
        assert data['systems_count'] == 42


class TestStartupEvent:
    """Test application startup behavior."""

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.db_conn')
    def test_startup_initializes_database(self, mock_db, mock_repo):
        """Test database is initialized on startup."""
        mock_repo.count.return_value = 100  # Non-empty database

        # Import to trigger startup
        from starsystems.web.app import startup_event
        startup_event()

        mock_db.initialize_schema.assert_called_once()

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.exoplanet_service')
    @patch('starsystems.web.app.db_conn')
    @patch('threading.Thread')
    def test_startup_syncs_if_empty(self, mock_thread_class, mock_db, mock_service, mock_repo):
        """Test background sync starts if database is empty."""
        mock_repo.count.return_value = 0  # Empty database
        mock_thread = Mock()
        mock_thread_class.return_value = mock_thread

        from starsystems.web.app import startup_event
        startup_event()

        # Verify thread was created and started
        mock_thread_class.assert_called_once()
        mock_thread.start.assert_called_once()


class TestImportStatus:
    """Test import status tracking."""

    def test_import_status_initial_state(self):
        """Test import status has correct initial state."""
        assert import_status["running"] is False
        assert import_status["completed"] is False
        assert import_status["count"] == 0
        assert import_status["error"] is None


class TestTemplateContext:
    """Test that templates receive correct context."""

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_context(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test systems page receives all required context variables."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {}
        }

        response = client.get("/systems?distance=100&name=Test")

        assert response.status_code == 200
        # Context should include systems, stats, filters, import_status
        assert "systems" in response.text or "Kepler" in response.text


class TestErrorHandling:
    """Test error handling in endpoints."""

    @patch('starsystems.web.app.repository')
    def test_api_handles_empty_database(self, mock_repo, client):
        """Test API handles empty database gracefully."""
        mock_repo.find_all.return_value = []

        response = client.get("/api/systems")

        assert response.status_code == 200
        assert response.json() == []

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_systems_page_handles_empty_database(self, mock_search, mock_repo, client):
        """Test page handles empty database gracefully."""
        mock_repo.find_all.return_value = []
        mock_search.filter_systems.return_value = []
        mock_search.get_statistics.return_value = {
            'total_systems': 0,
            'systems_with_planets': 0,
            'total_planets': 0,
            'avg_distance': 0.0,
            'avg_planets_per_system': 0.0,
            'spectral_type_distribution': {}
        }

        response = client.get("/systems")

        assert response.status_code == 200


class TestQueryParameterParsing:
    """Test parsing of query parameters."""

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_boolean_parameter_parsing(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test has_planets boolean parsing."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'M': 2, 'A': 1}
        }

        # Test "true"
        response = client.get("/systems?has_planets=true")
        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['has_planets'] is True

        # Test "false"
        response = client.get("/systems?has_planets=false")
        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['has_planets'] is False

        # Test neither (should be None)
        response = client.get("/systems")
        assert response.status_code == 200
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['has_planets'] is None

    @patch('starsystems.web.app.repository')
    @patch('starsystems.web.app.search_service')
    def test_spectral_type_parsing(self, mock_search, mock_repo, client, sample_systems, complete_stats):
        """Test spectral type comma-separated parsing."""
        mock_repo.find_all.return_value = sample_systems
        mock_search.filter_systems.return_value = sample_systems
        mock_search.get_statistics.return_value = {
            'total_systems': 3,
            'systems_with_planets': 2,
            'total_planets': 3,
            'avg_distance': 38.33,
            'avg_planets_per_system': 1.0,
            'spectral_type_distribution': {'M': 2, 'A': 1}
        }

        # Single type
        response = client.get("/systems?spectral_type=M")
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['spectral_types'] == ['M']

        # Multiple types
        response = client.get("/systems?spectral_type=G,K,M")
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['spectral_types'] == ['G', 'K', 'M']

        # With spaces
        response = client.get("/systems?spectral_type=G, K, M")
        call_args = mock_search.filter_systems.call_args
        assert call_args[1]['spectral_types'] == ['G', 'K', 'M']