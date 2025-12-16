"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os
from pathlib import Path
from typing import Generator

from starsystems.database import DatabaseConnection, StarSystemRepository
from starsystems.models import Planet, StarSystem
from starsystems.services import ExoplanetService, SearchService


@pytest.fixture
def temp_db_path() -> Generator[str, None, None]:
    """Create a temporary database file for testing.
    
    Yields:
        Path to temporary database file
    """
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db') as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def db_connection(temp_db_path: str) -> DatabaseConnection:
    """Create a database connection with initialized schema.
    
    Args:
        temp_db_path: Path to temporary database
        
    Returns:
        DatabaseConnection instance
    """
    db = DatabaseConnection(temp_db_path)
    db.initialize_schema()
    return db


@pytest.fixture
def repository(db_connection: DatabaseConnection) -> StarSystemRepository:
    """Create a repository instance.
    
    Args:
        db_connection: Database connection fixture
        
    Returns:
        StarSystemRepository instance
    """
    return StarSystemRepository(db_connection)


@pytest.fixture
def search_service() -> SearchService:
    """Create a search service instance.
    
    Returns:
        SearchService instance
    """
    return SearchService()


@pytest.fixture
def sample_planet() -> Planet:
    """Create a sample planet for testing.
    
    Returns:
        Planet instance
    """
    return Planet(
        name="Earth",
        mass=1.0,
        radius=1.0,
        orbit_distance=1.0
    )


@pytest.fixture
def sample_system(sample_planet: Planet) -> StarSystem:
    """Create a sample star system for testing.
    
    Args:
        sample_planet: Planet fixture
        
    Returns:
        StarSystem with one planet
    """
    system = StarSystem(
        name="Solar System",
        spectral_type="G2V",
        distance_ly=0.0
    )
    system.add_planet(sample_planet)
    return system


@pytest.fixture
def sample_systems() -> list[StarSystem]:
    """Create multiple sample star systems for testing.
    
    Returns:
        List of StarSystem instances with various properties
    """
    systems = []
    
    # Nearby G-type star with planets
    kepler = StarSystem("Kepler-186", "G2V", 50.0)
    kepler.add_planet(Planet("Kepler-186 f", 1.5, 1.2, 0.5))
    kepler.add_planet(Planet("Kepler-186 b", 0.8, 0.9, 0.3))
    systems.append(kepler)
    
    # Distant M-type star with planets
    trappist = StarSystem("TRAPPIST-1", "M8V", 200.0)
    trappist.add_planet(Planet("TRAPPIST-1 e", 0.9, 0.95, 0.4))
    systems.append(trappist)
    
    # Nearby K-type star with planets
    proxima = StarSystem("Proxima Centauri", "M5.5Ve", 4.24)
    proxima.add_planet(Planet("Proxima Centauri b", 1.3, 1.1, 0.05))
    systems.append(proxima)
    
    # Distant star without planets
    vega = StarSystem("Vega", "A0V", 25.0)
    systems.append(vega)
    
    # Unknown distance star with planets
    mysterious = StarSystem("Mysterious-1", "K3V", 0.0)
    mysterious.add_planet(Planet("Mysterious-1 b", 2.0, 1.5, 1.0))
    systems.append(mysterious)
    
    return systems


@pytest.fixture
def populated_repository(repository: StarSystemRepository, 
                        sample_systems: list[StarSystem]) -> StarSystemRepository:
    """Create a repository populated with sample data.
    
    Args:
        repository: Empty repository fixture
        sample_systems: Sample systems fixture
        
    Returns:
        Repository with saved systems
    """
    repository.save_batch(sample_systems)
    return repository
