"""StarSystems - Exoplanet database and search tool."""

__version__ = "2.0.0"
__author__ = "Stephen Brooks"

from .models import Planet, StarSystem
from .database import DatabaseConnection, StarSystemRepository
from .services import ExoplanetService, SearchService

__all__ = [
    'Planet',
    'StarSystem',
    'DatabaseConnection',
    'StarSystemRepository',
    'ExoplanetService',
    'SearchService',
]