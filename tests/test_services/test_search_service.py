"""Tests for SearchService."""

import pytest
from starsystems.services import SearchService
from starsystems.models import Planet, StarSystem


class TestSearchServiceFiltering:
    """Test filtering functionality of SearchService."""
    
    def test_filter_by_distance(self, search_service, sample_systems):
        """Test filtering by maximum distance."""
        # Filter for systems within 50 light years
        results = search_service.filter_systems(
            sample_systems,
            max_distance=50.0
        )
        
        assert len(results) > 0
        assert all(0 < s.distance_ly <= 50.0 for s in results)
    
    def test_filter_by_distance_excludes_zero(self, search_service, sample_systems):
        """Test that zero-distance systems are excluded from distance filter."""
        results = search_service.filter_systems(
            sample_systems,
            max_distance=100.0
        )
        
        # Systems with distance_ly == 0 should be excluded
        assert all(s.distance_ly > 0 for s in results)
    
    def test_filter_by_spectral_type_single(self, search_service, sample_systems):
        """Test filtering by single spectral type."""
        results = search_service.filter_systems(
            sample_systems,
            spectral_types=['G']
        )
        
        assert len(results) > 0
        assert all(s.spectral_type.startswith('G') for s in results)
    
    def test_filter_by_spectral_type_multiple(self, search_service, sample_systems):
        """Test filtering by multiple spectral types."""
        results = search_service.filter_systems(
            sample_systems,
            spectral_types=['G', 'K', 'M']
        )
        
        assert len(results) > 0
        for system in results:
            first_char = system.spectral_type[0] if system.spectral_type else ''
            assert first_char in ['G', 'K', 'M']
    
    def test_filter_has_planets_true(self, search_service, sample_systems):
        """Test filtering for systems with planets."""
        results = search_service.filter_systems(
            sample_systems,
            has_planets=True
        )
        
        assert len(results) > 0
        assert all(s.has_planet() for s in results)
    
    def test_filter_has_planets_false(self, search_service, sample_systems):
        """Test filtering for systems without planets."""
        results = search_service.filter_systems(
            sample_systems,
            has_planets=False
        )
        
        assert len(results) > 0
        assert all(not s.has_planet() for s in results)
    
    def test_filter_min_planets(self, search_service, sample_systems):
        """Test filtering by minimum planet count."""
        results = search_service.filter_systems(
            sample_systems,
            min_planets=2
        )
        
        assert all(s.planet_count() >= 2 for s in results)
    
    def test_filter_combined(self, search_service, sample_systems):
        """Test combining multiple filters."""
        results = search_service.filter_systems(
            sample_systems,
            max_distance=100.0,
            spectral_types=['G', 'K'],
            has_planets=True
        )
        
        for system in results:
            assert 0 < system.distance_ly <= 100.0
            assert system.spectral_type[0] in ['G', 'K']
            assert system.has_planet()
    
    def test_filter_no_filters_returns_all(self, search_service, sample_systems):
        """Test that no filters returns all systems."""
        results = search_service.filter_systems(sample_systems)
        assert len(results) == len(sample_systems)


class TestSearchServiceNameSearch:
    """Test name search functionality."""
    
    def test_search_by_name_exact(self, search_service):
        """Test exact name match."""
        systems = [
            StarSystem("Kepler-186", "G2V", 50.0),
            StarSystem("Kepler-452", "G2V", 60.0),
            StarSystem("TRAPPIST-1", "M8V", 40.0),
        ]
        
        results = search_service.search_by_name(systems, "TRAPPIST-1")
        assert len(results) == 1
        assert results[0].name == "TRAPPIST-1"
    
    def test_search_by_name_partial(self, search_service):
        """Test partial name match."""
        systems = [
            StarSystem("Kepler-186", "G2V", 50.0),
            StarSystem("Kepler-452", "G2V", 60.0),
            StarSystem("TRAPPIST-1", "M8V", 40.0),
        ]
        
        results = search_service.search_by_name(systems, "Kepler")
        assert len(results) == 2
        assert all("Kepler" in s.name for s in results)
    
    def test_search_by_name_case_insensitive(self, search_service):
        """Test that name search is case-insensitive."""
        systems = [
            StarSystem("Kepler-186", "G2V", 50.0),
            StarSystem("TRAPPIST-1", "M8V", 40.0),
        ]
        
        results = search_service.search_by_name(systems, "kepler")
        assert len(results) == 1
        
        results = search_service.search_by_name(systems, "KEPLER")
        assert len(results) == 1
        
        results = search_service.search_by_name(systems, "trappist")
        assert len(results) == 1
    
    def test_search_by_name_no_match(self, search_service):
        """Test search with no matching systems."""
        systems = [
            StarSystem("Kepler-186", "G2V", 50.0),
            StarSystem("TRAPPIST-1", "M8V", 40.0),
        ]
        
        results = search_service.search_by_name(systems, "Nonexistent")
        assert len(results) == 0


class TestSearchServiceStatistics:
    """Test statistics generation."""
    
    def test_statistics_empty_list(self, search_service):
        """Test statistics on empty list."""
        stats = search_service.get_statistics([])
        
        assert stats["total_systems"] == 0
        assert stats["systems_with_planets"] == 0
        assert stats["total_planets"] == 0
        assert stats["avg_distance"] == 0.0
        assert stats["spectral_type_distribution"] == {}
    
    def test_statistics_basic(self, search_service):
        """Test basic statistics calculation."""
        systems = [
            StarSystem("System 1", "G2V", 10.0),
            StarSystem("System 2", "K5V", 20.0),
            StarSystem("System 3", "M5V", 30.0),
        ]
        
        systems[0].add_planet(Planet("Planet 1", 1.0, 1.0, 1.0))
        systems[1].add_planet(Planet("Planet 2", 2.0, 1.5, 2.0))
        systems[1].add_planet(Planet("Planet 3", 3.0, 2.0, 3.0))
        
        stats = search_service.get_statistics(systems)
        
        assert stats["total_systems"] == 3
        assert stats["systems_with_planets"] == 2
        assert stats["total_planets"] == 3
        assert stats["avg_distance"] == 20.0  # (10 + 20 + 30) / 3
        assert stats["avg_planets_per_system"] == 1.0  # 3 planets / 3 systems
    
    def test_statistics_spectral_distribution(self, search_service):
        """Test spectral type distribution calculation."""
        systems = [
            StarSystem("G Star 1", "G2V", 10.0),
            StarSystem("G Star 2", "G5V", 15.0),
            StarSystem("K Star", "K3V", 20.0),
            StarSystem("M Star", "M5V", 25.0),
        ]
        
        stats = search_service.get_statistics(systems)
        
        dist = stats["spectral_type_distribution"]
        assert dist["G"] == 2
        assert dist["K"] == 1
        assert dist["M"] == 1
    
    def test_statistics_excludes_unknown_distance(self, search_service):
        """Test that zero distances are excluded from average."""
        systems = [
            StarSystem("System 1", "G2V", 10.0),
            StarSystem("System 2", "K5V", 20.0),
            StarSystem("System 3", "M5V", 0.0),  # Zero distance
        ]
        
        stats = search_service.get_statistics(systems)
        
        # Average should be (10 + 20) / 2 = 15, excluding the zero
        assert stats["avg_distance"] == 15.0


class TestSearchServiceEdgeCases:
    """Test edge cases for SearchService."""
    
    def test_empty_systems_list(self, search_service):
        """Test operations on empty systems list."""
        results = search_service.filter_systems([], max_distance=100.0)
        assert results == []
        
        results = search_service.search_by_name([], "Test")
        assert results == []
    
    def test_filter_spectral_type_case_insensitive(self, search_service):
        """Test that spectral type filtering is case-insensitive."""
        systems = [
            StarSystem("System 1", "G2V", 10.0),
            StarSystem("System 2", "g5V", 15.0),
        ]
        
        # Should match both regardless of case
        results = search_service.filter_systems(
            systems,
            spectral_types=['g']
        )
        assert len(results) == 2
        
        results = search_service.filter_systems(
            systems,
            spectral_types=['G']
        )
        assert len(results) == 2
    
    def test_filter_unknown_spectral_types_excluded(self, search_service):
        """Test that Unknown spectral types are excluded from filtering."""
        systems = [
            StarSystem("Known", "G2V", 10.0),
            StarSystem("Unknown", "Unknown", 15.0),
            StarSystem("Empty", "", 20.0),
        ]
        
        results = search_service.filter_systems(
            systems,
            spectral_types=['G']
        )
        
        assert len(results) == 1
        assert results[0].name == "Known"
    
    def test_filter_spectral_type_empty_list(self, search_service, sample_systems):
        """Test filtering with empty spectral type list."""
        # Empty list should return all systems
        results = search_service.filter_systems(
            sample_systems,
            spectral_types=[]
        )
        assert len(results) == len(sample_systems)
    
    def test_very_large_distance_filter(self, search_service):
        """Test filtering with very large distance."""
        systems = [
            StarSystem("Nearby", "G2V", 10.0),
            StarSystem("Far", "K5V", 10000.0),
        ]
        
        results = search_service.filter_systems(
            systems,
            max_distance=999999.0
        )
        
        assert len(results) == 2
    
    def test_min_planets_zero(self, search_service, sample_systems):
        """Test minimum planets filter with zero."""
        results = search_service.filter_systems(
            sample_systems,
            min_planets=0
        )
        
        # All systems should pass (even those with no planets)
        assert len(results) == len(sample_systems)
