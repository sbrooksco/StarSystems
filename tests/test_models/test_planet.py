"""Tests for Planet model."""

import pytest
from starsystems.models import Planet


class TestPlanet:
    """Test cases for Planet model."""

    def test_planet_creation(self):
        """Test creating a planet with valid data."""
        planet = Planet(
            name="Earth",
            mass=1.0,
            radius=1.0,
            orbit_distance=1.0
        )

        assert planet.name == "Earth"
        assert planet.mass == 1.0
        assert planet.radius == 1.0
        assert planet.orbit_distance == 1.0

    def test_planet_classification_dwarf(self):
        """Test classification of dwarf planet."""
        planet = Planet("Pluto", 0.002, 0.18, 39.5)
        assert planet.classify() == "Dwarf Planet"

    def test_planet_classification_terrestrial(self):
        """Test classification of terrestrial planet."""
        planet = Planet("Earth", 1.0, 1.0, 1.0)
        assert planet.classify() == "Terrestrial"

        planet2 = Planet("Mars", 0.107, 0.53, 1.52)
        assert planet2.classify() == "Terrestrial"

    def test_planet_classification_super_earth(self):
        """Test classification of super-Earth."""
        planet = Planet("Super Earth", 5.0, 1.8, 0.5)
        assert planet.classify() == "Super-Earth"

        planet2 = Planet("Large Terrestrial", 9.9, 2.0, 1.0)
        assert planet2.classify() == "Super-Earth"

    def test_planet_classification_gas_giant(self):
        """Test classification of gas giant."""
        planet = Planet("Jupiter", 317.8, 11.2, 5.2)
        assert planet.classify() == "Gas Giant"

        planet2 = Planet("Large Planet", 100.0, 15.0, 3.0)
        assert planet2.classify() == "Gas Giant"

    def test_planet_to_dict(self):
        """Test planet conversion to dictionary."""
        planet = Planet("Earth", 1.0, 1.0, 1.0)
        data = planet.to_dict()

        assert data["name"] == "Earth"
        assert data["mass"] == 1.0
        assert data["radius"] == 1.0
        assert data["orbit_distance"] == 1.0
        assert data["classification"] == "Terrestrial"

    def test_planet_str_representation(self):
        """Test planet string representation."""
        planet = Planet("Earth", 1.0, 1.0, 1.0)
        str_repr = str(planet)

        assert "Earth" in str_repr
        assert "1.00 M⊕" in str_repr
        assert "1.00 R⊕" in str_repr
        assert "1.00 AU" in str_repr
        assert "Terrestrial" in str_repr

    def test_planet_with_zero_mass(self):
        """Test planet with zero mass classification."""
        planet = Planet("Tiny", 0.0, 0.5, 1.0)
        assert planet.classify() == "Dwarf Planet"

    def test_planet_with_large_values(self):
        """Test planet with large values."""
        planet = Planet("Massive", 1000.0, 50.0, 100.0)
        assert planet.classify() == "Gas Giant"

        data = planet.to_dict()
        assert data["mass"] == 1000.0
        assert data["radius"] == 50.0


class TestPlanetEdgeCases:
    """Test edge cases for Planet model."""

    def test_classification_boundary_dwarf_terrestrial(self):
        """Test classification at dwarf/terrestrial boundary."""
        # Just below terrestrial threshold
        planet1 = Planet("Boundary1", 0.099, 1.0, 1.0)
        assert planet1.classify() == "Dwarf Planet"

        # At the threshold (0.1 is NOT < 0.1, so Terrestrial)
        planet2 = Planet("Boundary2", 0.1, 1.0, 1.0)
        assert planet2.classify() == "Terrestrial"

        # Just above threshold (clearly Terrestrial)
        planet3 = Planet("Boundary3", 0.11, 1.0, 1.0)
        assert planet3.classify() == "Terrestrial"

    def test_classification_boundary_terrestrial_super_earth(self):
        """Test classification at terrestrial/super-Earth boundary."""
        # Terrestrial (mass and radius both under limits)
        planet1 = Planet("Terrestrial", 1.99, 1.49, 1.0)
        assert planet1.classify() == "Terrestrial"

        # Super-Earth (mass at boundary)
        planet2 = Planet("Super", 2.0, 1.0, 1.0)
        assert planet2.classify() == "Super-Earth"

        # Super-Earth (radius at boundary)
        planet3 = Planet("Super2", 1.0, 1.5, 1.0)
        assert planet3.classify() == "Super-Earth"

    def test_classification_boundary_super_earth_gas_giant(self):
        """Test classification at super-Earth/gas giant boundary."""
        # Just below gas giant threshold
        planet1 = Planet("Large", 9.99, 3.0, 1.0)
        assert planet1.classify() == "Super-Earth"

        # Just at gas giant threshold
        planet2 = Planet("Giant", 10.0, 3.0, 1.0)
        assert planet2.classify() == "Gas Giant"

    def test_negative_values(self):
        """Test planet with negative values (invalid but should not crash)."""
        planet = Planet("Invalid", -1.0, -1.0, -1.0)
        # Should still classify (dwarf due to negative mass < 0.1)
        classification = planet.classify()
        assert isinstance(classification, str)
