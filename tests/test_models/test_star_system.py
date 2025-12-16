"""Tests for StarSystem model."""

import pytest
from starsystems.models import Planet, StarSystem


class TestStarSystem:
    """Test cases for StarSystem model."""
    
    def test_system_creation_minimal(self):
        """Test creating a star system with minimal data."""
        system = StarSystem("Alpha Centauri")
        
        assert system.name == "Alpha Centauri"
        assert system.spectral_type == "Unknown"
        assert system.distance_ly == 0.0
        assert len(system.planets) == 0
    
    def test_system_creation_full(self):
        """Test creating a star system with all data."""
        system = StarSystem(
            name="Solar System",
            spectral_type="G2V",
            distance_ly=0.0
        )
        
        assert system.name == "Solar System"
        assert system.spectral_type == "G2V"
        assert system.distance_ly == 0.0
    
    def test_add_planet(self):
        """Test adding planets to a system."""
        system = StarSystem("Test System")
        planet1 = Planet("Planet A", 1.0, 1.0, 1.0)
        planet2 = Planet("Planet B", 2.0, 1.5, 2.0)
        
        system.add_planet(planet1)
        assert len(system.planets) == 1
        assert system.planets[0].name == "Planet A"
        
        system.add_planet(planet2)
        assert len(system.planets) == 2
        assert system.planets[1].name == "Planet B"
    
    def test_has_planets_empty(self):
        """Test has_planet() with no planets."""
        system = StarSystem("Empty System")
        assert system.has_planet() is False
    
    def test_has_planets_with_planets(self):
        """Test has_planet() with planets."""
        system = StarSystem("Full System")
        system.add_planet(Planet("Planet", 1.0, 1.0, 1.0))
        assert system.has_planet() is True
    
    def test_planet_count(self):
        """Test planet_count() method."""
        system = StarSystem("Test System")
        assert system.planet_count() == 0
        
        system.add_planet(Planet("Planet 1", 1.0, 1.0, 1.0))
        assert system.planet_count() == 1
        
        system.add_planet(Planet("Planet 2", 2.0, 1.5, 2.0))
        assert system.planet_count() == 2
        
        system.add_planet(Planet("Planet 3", 3.0, 2.0, 3.0))
        assert system.planet_count() == 3
    
    def test_to_dict(self):
        """Test conversion to dictionary."""
        system = StarSystem("Test System", "G2V", 10.5)
        system.add_planet(Planet("Planet", 1.0, 1.0, 1.0))
        
        data = system.to_dict()
        
        assert data["name"] == "Test System"
        assert data["spectral_type"] == "G2V"
        assert data["distance_ly"] == 10.5
        assert data["planet_count"] == 1
        assert len(data["planets"]) == 1
        assert data["planets"][0]["name"] == "Planet"
    
    def test_to_dict_no_planets(self):
        """Test to_dict with no planets."""
        system = StarSystem("Empty System", "M3V", 5.0)
        data = system.to_dict()
        
        assert data["planet_count"] == 0
        assert data["planets"] == []
    
    def test_str_representation_no_planets(self):
        """Test string representation without planets."""
        system = StarSystem("Lonely Star", "K3V", 15.0)
        str_repr = str(system)
        
        assert "Lonely Star" in str_repr
        assert "K3V" in str_repr
        assert "15.00 ly" in str_repr
        assert "Planets (0)" in str_repr
        assert "No planets" in str_repr
    
    def test_str_representation_with_planets(self):
        """Test string representation with planets."""
        system = StarSystem("System with Planets", "G2V", 10.0)
        system.add_planet(Planet("Planet A", 1.0, 1.0, 1.0))
        system.add_planet(Planet("Planet B", 5.0, 2.0, 2.0))
        
        str_repr = str(system)
        
        assert "System with Planets" in str_repr
        assert "G2V" in str_repr
        assert "10.00 ly" in str_repr
        assert "Planets (2)" in str_repr
        assert "Planet A" in str_repr
        assert "Planet B" in str_repr


class TestStarSystemEdgeCases:
    """Test edge cases for StarSystem model."""
    
    def test_system_with_many_planets(self):
        """Test system with many planets."""
        system = StarSystem("Multi-Planet System")
        
        for i in range(10):
            system.add_planet(Planet(f"Planet {i}", i * 1.0, i * 0.5, i * 0.1))
        
        assert system.planet_count() == 10
        assert system.has_planet() is True
    
    def test_default_values(self):
        """Test default values are properly set."""
        system = StarSystem("Test")
        
        assert system.spectral_type == "Unknown"
        assert system.distance_ly == 0.0
        assert isinstance(system.planets, list)
    
    def test_zero_distance(self):
        """Test system at zero distance (e.g., Solar System)."""
        system = StarSystem("Solar System", "G2V", 0.0)
        assert system.distance_ly == 0.0
    
    def test_large_distance(self):
        """Test system with very large distance."""
        system = StarSystem("Distant System", "M5V", 10000.0)
        assert system.distance_ly == 10000.0
    
    def test_unusual_spectral_types(self):
        """Test various spectral type formats."""
        system1 = StarSystem("Star1", "G2V")
        assert system1.spectral_type == "G2V"
        
        system2 = StarSystem("Star2", "M5.5Ve")
        assert system2.spectral_type == "M5.5Ve"
        
        system3 = StarSystem("Star3", "A0V")
        assert system3.spectral_type == "A0V"
        
        system4 = StarSystem("Star4", "")
        assert system4.spectral_type == ""
    
    def test_adding_duplicate_planet_names(self):
        """Test adding planets with duplicate names (should be allowed)."""
        system = StarSystem("Test System")
        planet1 = Planet("Duplicate", 1.0, 1.0, 1.0)
        planet2 = Planet("Duplicate", 2.0, 1.5, 2.0)
        
        system.add_planet(planet1)
        system.add_planet(planet2)
        
        assert system.planet_count() == 2
        # Both planets are added despite same name
        assert all(p.name == "Duplicate" for p in system.planets)


class TestStarSystemDataClass:
    """Test dataclass-specific behavior."""
    
    def test_planets_field_independence(self):
        """Test that planets list is independent for each instance."""
        system1 = StarSystem("System 1")
        system2 = StarSystem("System 2")
        
        system1.add_planet(Planet("Planet A", 1.0, 1.0, 1.0))
        
        # system2 should not have system1's planet
        assert system1.planet_count() == 1
        assert system2.planet_count() == 0
    
    def test_immutable_after_creation(self):
        """Test that we can modify the system after creation."""
        system = StarSystem("Test")
        
        # These should work (mutable)
        system.spectral_type = "G5V"
        assert system.spectral_type == "G5V"
        
        system.distance_ly = 20.0
        assert system.distance_ly == 20.0
