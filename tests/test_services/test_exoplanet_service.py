"""Tests for ExoplanetService."""

import pytest
from unittest.mock import Mock, patch
from starsystems.services import ExoplanetService
from starsystems.models import StarSystem, Planet


# Sample NASA API response data
SAMPLE_NASA_DATA = [
    {
        "hostname": "Kepler-186",
        "pl_name": "Kepler-186 f",
        "pl_bmassj": 0.0047,  # Jupiter masses
        "pl_radj": 0.1,       # Jupiter radii
        "pl_orbper": 0.5,     # Orbital period
        "st_spectype": "M1V",
        "sy_dist": 48.8       # Distance in parsecs
    },
    {
        "hostname": "Kepler-186",
        "pl_name": "Kepler-186 b",
        "pl_bmassj": 0.003,
        "pl_radj": 0.08,
        "pl_orbper": 0.2,
        "st_spectype": "M1V",
        "sy_dist": 48.8
    },
    {
        "hostname": "TRAPPIST-1",
        "pl_name": "TRAPPIST-1 e",
        "pl_bmassj": 0.003,
        "pl_radj": 0.09,
        "pl_orbper": 6.1,
        "st_spectype": "M8V",
        "sy_dist": 12.43
    },
]


class TestExoplanetService:
    """Test cases for ExoplanetService."""
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_fetch_systems_success(self, mock_get):
        """Test successful fetching of systems from NASA."""
        # Mock the API response
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_NASA_DATA
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        # Should have 2 systems (Kepler-186 and TRAPPIST-1)
        assert len(systems) == 2
        
        # Verify Kepler-186 has 2 planets
        kepler = next(s for s in systems if s.name == "Kepler-186")
        assert kepler.planet_count() == 2
        assert kepler.spectral_type == "M1V"
        
        # Verify TRAPPIST-1 has 1 planet
        trappist = next(s for s in systems if s.name == "TRAPPIST-1")
        assert trappist.planet_count() == 1
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_fetch_systems_converts_units(self, mock_get):
        """Test that Jupiter units are converted to Earth units."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_NASA_DATA
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        kepler = next(s for s in systems if s.name == "Kepler-186")
        planet = kepler.planets[0]
        
        # 0.0047 Jupiter masses * 317.8 = ~1.49 Earth masses
        assert planet.mass == pytest.approx(0.0047 * 317.8, rel=0.01)
        
        # 0.1 Jupiter radii * 11.2 = 1.12 Earth radii
        assert planet.radius == pytest.approx(0.1 * 11.2, rel=0.01)
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_fetch_systems_converts_distance(self, mock_get):
        """Test that parsecs are converted to light years."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_NASA_DATA
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        kepler = next(s for s in systems if s.name == "Kepler-186")
        
        # 48.8 parsecs * 3.26156 = ~159.2 light years
        expected_ly = 48.8 * 3.26156
        assert kepler.distance_ly == pytest.approx(expected_ly, rel=0.01)
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_fetch_systems_handles_missing_data(self, mock_get):
        """Test handling of missing/null data."""
        data_with_nulls = [
            {
                "hostname": "Partial System",
                "pl_name": None,  # Missing planet name
                "pl_bmassj": None,
                "pl_radj": "",
                "pl_orbper": None,
                "st_spectype": None,
                "sy_dist": None
            }
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = data_with_nulls
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        # Should create system with defaults
        assert len(systems) == 1
        system = systems[0]
        assert system.name == "Partial System"
        assert system.spectral_type == "Unknown"
        assert system.distance_ly == 0.0
        
        # Planet with null name shouldn't be added
        assert system.planet_count() == 0
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_fetch_systems_api_error(self, mock_get):
        """Test handling of API errors."""
        mock_get.side_effect = Exception("API Error")
        
        service = ExoplanetService()
        
        with pytest.raises(Exception):
            service.fetch_systems()
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_fetch_systems_empty_response(self, mock_get):
        """Test handling of empty API response."""
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        assert systems == []


class TestExoplanetServiceHelperMethods:
    """Test helper methods of ExoplanetService."""
    
    def test_safe_float_valid_value(self):
        """Test safe_float with valid value."""
        result = ExoplanetService._safe_float(5.5)
        assert result == 5.5
    
    def test_safe_float_with_multiplier(self):
        """Test safe_float with multiplier."""
        result = ExoplanetService._safe_float(10.0, multiplier=2.0)
        assert result == 20.0
    
    def test_safe_float_none_value(self):
        """Test safe_float with None."""
        result = ExoplanetService._safe_float(None, default=99.0)
        assert result == 99.0
    
    def test_safe_float_empty_string(self):
        """Test safe_float with empty string."""
        result = ExoplanetService._safe_float("", default=42.0)
        assert result == 42.0
    
    def test_safe_float_invalid_value(self):
        """Test safe_float with invalid value."""
        result = ExoplanetService._safe_float("not a number", default=10.0)
        assert result == 10.0
    
    def test_safe_float_string_number(self):
        """Test safe_float with string representation of number."""
        result = ExoplanetService._safe_float("123.45")
        assert result == 123.45


class TestExoplanetServiceIntegration:
    """Integration tests for ExoplanetService."""
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_complete_workflow(self, mock_get):
        """Test complete workflow of fetching and parsing."""
        mock_response = Mock()
        mock_response.json.return_value = SAMPLE_NASA_DATA
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        # Verify all systems created
        assert len(systems) == 2
        
        # Verify all data properly parsed
        for system in systems:
            assert isinstance(system, StarSystem)
            assert system.name
            assert system.spectral_type
            assert system.distance_ly >= 0
            
            for planet in system.planets:
                assert isinstance(planet, Planet)
                assert planet.name
                assert planet.mass >= 0
                assert planet.radius >= 0
    
    @patch('starsystems.services.exoplanet_service.requests.get')
    def test_duplicate_systems_merged(self, mock_get):
        """Test that multiple planets for same system are merged."""
        # Data with 3 planets for same system
        data = [
            {
                "hostname": "Test System",
                "pl_name": "Planet A",
                "pl_bmassj": 1.0,
                "pl_radj": 1.0,
                "pl_orbper": 1.0,
                "st_spectype": "G2V",
                "sy_dist": 10.0
            },
            {
                "hostname": "Test System",
                "pl_name": "Planet B",
                "pl_bmassj": 2.0,
                "pl_radj": 1.5,
                "pl_orbper": 2.0,
                "st_spectype": "G2V",
                "sy_dist": 10.0
            },
            {
                "hostname": "Test System",
                "pl_name": "Planet C",
                "pl_bmassj": 3.0,
                "pl_radj": 2.0,
                "pl_orbper": 3.0,
                "st_spectype": "G2V",
                "sy_dist": 10.0
            },
        ]
        
        mock_response = Mock()
        mock_response.json.return_value = data
        mock_response.raise_for_status = Mock()
        mock_get.return_value = mock_response
        
        service = ExoplanetService()
        systems = service.fetch_systems()
        
        # Should be 1 system with 3 planets
        assert len(systems) == 1
        assert systems[0].planet_count() == 3


class TestExoplanetServiceConfiguration:
    """Test service configuration."""
    
    def test_custom_timeout(self):
        """Test creating service with custom timeout."""
        service = ExoplanetService(timeout=60)
        assert service.timeout == 60
    
    def test_default_timeout(self):
        """Test default timeout value."""
        service = ExoplanetService()
        assert service.timeout == 30
    
    def test_url_configuration(self):
        """Test that URL is properly configured."""
        service = ExoplanetService()
        assert "exoplanetarchive.ipac.caltech.edu" in service.url
        assert "TAP/sync" in service.url
