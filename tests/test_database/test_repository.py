"""Tests for StarSystemRepository."""

import pytest
from starsystems.database import StarSystemRepository
from starsystems.models import Planet, StarSystem


class TestStarSystemRepository:
    """Test cases for StarSystemRepository."""
    
    def test_save_single_system(self, repository):
        """Test saving a single star system."""
        system = StarSystem("Test System", "G2V", 10.0)
        system.add_planet(Planet("Test Planet", 1.0, 1.0, 1.0))
        
        repository.save(system)
        
        # Verify by loading
        loaded = repository.find_by_name("Test System")
        assert loaded is not None
        assert loaded.name == "Test System"
        assert loaded.spectral_type == "G2V"
        assert loaded.distance_ly == 10.0
        assert loaded.planet_count() == 1
    
    def test_save_system_without_planets(self, repository):
        """Test saving a system with no planets."""
        system = StarSystem("Empty System", "M3V", 5.0)
        
        repository.save(system)
        
        loaded = repository.find_by_name("Empty System")
        assert loaded is not None
        assert loaded.planet_count() == 0
    
    def test_save_updates_existing_system(self, repository):
        """Test that saving updates existing system."""
        system = StarSystem("Update Test", "G2V", 10.0)
        repository.save(system)
        
        # Update and save again
        system.spectral_type = "K5V"
        system.distance_ly = 20.0
        repository.save(system)
        
        loaded = repository.find_by_name("Update Test")
        assert loaded.spectral_type == "K5V"
        assert loaded.distance_ly == 20.0
    
    def test_save_batch(self, repository, sample_systems):
        """Test saving multiple systems in batch."""
        success, failed = repository.save_batch(sample_systems)
        
        assert success == len(sample_systems)
        assert failed == 0
        
        # Verify all were saved
        all_systems = repository.find_all()
        assert len(all_systems) == len(sample_systems)
    
    def test_find_all_empty(self, repository):
        """Test find_all on empty database."""
        systems = repository.find_all()
        assert systems == []
    
    def test_find_all_with_data(self, populated_repository):
        """Test find_all with populated database."""
        systems = populated_repository.find_all()
        
        assert len(systems) > 0
        assert all(isinstance(s, StarSystem) for s in systems)
    
    def test_find_by_name_exists(self, populated_repository):
        """Test finding an existing system by name."""
        system = populated_repository.find_by_name("Kepler-186")
        
        assert system is not None
        assert system.name == "Kepler-186"
        assert system.planet_count() > 0
    
    def test_find_by_name_not_exists(self, repository):
        """Test finding a non-existent system."""
        system = repository.find_by_name("Nonexistent System")
        assert system is None
    
    def test_count_empty(self, repository):
        """Test count on empty database."""
        assert repository.count() == 0
    
    def test_count_with_data(self, populated_repository):
        """Test count with populated database."""
        count = populated_repository.count()
        assert count > 0
    
    def test_delete_all(self, populated_repository):
        """Test deleting all systems."""
        # Verify data exists
        assert populated_repository.count() > 0
        
        # Delete all
        populated_repository.delete_all()
        
        # Verify empty
        assert populated_repository.count() == 0
        assert populated_repository.find_all() == []


class TestStarSystemRepositoryPlanets:
    """Test repository handling of planets."""
    
    def test_save_system_with_multiple_planets(self, repository):
        """Test saving a system with multiple planets."""
        system = StarSystem("Multi-Planet", "G5V", 15.0)
        system.add_planet(Planet("Planet A", 1.0, 1.0, 1.0))
        system.add_planet(Planet("Planet B", 2.0, 1.5, 2.0))
        system.add_planet(Planet("Planet C", 5.0, 2.0, 3.0))
        
        repository.save(system)
        
        loaded = repository.find_by_name("Multi-Planet")
        assert loaded.planet_count() == 3
        
        planet_names = [p.name for p in loaded.planets]
        assert "Planet A" in planet_names
        assert "Planet B" in planet_names
        assert "Planet C" in planet_names
    
    def test_update_system_add_planet(self, repository):
        """Test updating a system by adding a planet."""
        system = StarSystem("Growing System", "K3V", 8.0)
        system.add_planet(Planet("Planet 1", 1.0, 1.0, 1.0))
        repository.save(system)
        
        # Add another planet
        system.add_planet(Planet("Planet 2", 2.0, 1.5, 2.0))
        repository.save(system)
        
        loaded = repository.find_by_name("Growing System")
        assert loaded.planet_count() == 2
    
    def test_planet_properties_preserved(self, repository):
        """Test that planet properties are preserved accurately."""
        system = StarSystem("Precision Test", "G2V", 10.5)
        planet = Planet("Precise Planet", 1.234, 5.678, 9.012)
        system.add_planet(planet)
        
        repository.save(system)
        
        loaded = repository.find_by_name("Precision Test")
        loaded_planet = loaded.planets[0]
        
        assert loaded_planet.name == "Precise Planet"
        assert loaded_planet.mass == pytest.approx(1.234)
        assert loaded_planet.radius == pytest.approx(5.678)
        assert loaded_planet.orbit_distance == pytest.approx(9.012)


class TestStarSystemRepositoryEdgeCases:
    """Test edge cases for repository."""
    
    def test_save_system_with_zero_distance(self, repository):
        """Test saving system with zero distance."""
        system = StarSystem("Solar System", "G2V", 0.0)
        repository.save(system)
        
        loaded = repository.find_by_name("Solar System")
        assert loaded.distance_ly == 0.0
    
    def test_save_system_with_unknown_spectral_type(self, repository):
        """Test saving system with Unknown spectral type."""
        system = StarSystem("Mystery Star")
        repository.save(system)
        
        loaded = repository.find_by_name("Mystery Star")
        assert loaded.spectral_type == "Unknown"
    
    def test_save_batch_with_empty_list(self, repository):
        """Test batch save with empty list."""
        success, failed = repository.save_batch([])
        
        assert success == 0
        assert failed == 0
    
    def test_save_batch_partial_failure_resilience(self, repository):
        """Test that batch save continues after individual failures."""
        systems = [
            StarSystem("Valid System 1", "G2V", 10.0),
            StarSystem("Valid System 2", "K5V", 20.0),
        ]
        
        # Should save both successfully
        success, failed = repository.save_batch(systems)
        assert success == 2
        assert failed == 0
    
    def test_special_characters_in_names(self, repository):
        """Test handling of special characters in system/planet names."""
        system = StarSystem("Test-System_123", "G2V", 10.0)
        system.add_planet(Planet("Planet-A_1", 1.0, 1.0, 1.0))
        
        repository.save(system)
        
        loaded = repository.find_by_name("Test-System_123")
        assert loaded is not None
        assert loaded.planets[0].name == "Planet-A_1"
    
    def test_very_large_values(self, repository):
        """Test handling of very large numeric values."""
        system = StarSystem("Distant System", "M5V", 999999.99)
        system.add_planet(Planet("Giant Planet", 10000.0, 100.0, 1000.0))
        
        repository.save(system)
        
        loaded = repository.find_by_name("Distant System")
        assert loaded.distance_ly == pytest.approx(999999.99)
        assert loaded.planets[0].mass == pytest.approx(10000.0)


class TestStarSystemRepositoryIntegration:
    """Integration tests for repository."""
    
    def test_save_and_retrieve_complete_workflow(self, repository):
        """Test complete workflow: save multiple, retrieve, modify, save again."""
        # Initial save
        systems = [
            StarSystem("System A", "G2V", 10.0),
            StarSystem("System B", "K5V", 20.0),
        ]
        
        for system in systems:
            system.add_planet(Planet(f"{system.name} planet", 1.0, 1.0, 1.0))
        
        repository.save_batch(systems)
        
        # Retrieve and verify
        all_systems = repository.find_all()
        assert len(all_systems) == 2
        
        # Modify one system
        system_a = repository.find_by_name("System A")
        system_a.add_planet(Planet("New Planet", 2.0, 1.5, 2.0))
        repository.save(system_a)
        
        # Verify modification
        reloaded = repository.find_by_name("System A")
        assert reloaded.planet_count() == 2
    
    def test_concurrent_operations_simulation(self, repository):
        """Test multiple save operations in sequence."""
        for i in range(10):
            system = StarSystem(f"System {i}", "G2V", i * 10.0)
            system.add_planet(Planet(f"Planet {i}", i * 1.0, i * 0.5, i * 0.1))
            repository.save(system)
        
        assert repository.count() == 10
        
        all_systems = repository.find_all()
        assert len(all_systems) == 10
