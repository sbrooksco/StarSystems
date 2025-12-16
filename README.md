# StarSystems

An exoplanet database and search tool that fetches data from the NASA Exoplanet Archive, stores it locally in SQLite, and provides both CLI and web interfaces for searching and exploring star systems.

## Features

- **Automatic Data Sync**: Fetches confirmed exoplanet data from NASA Exoplanet Archive
- **Local Database**: SQLite storage for fast, offline querying
- **Advanced Filtering**: Search by distance, spectral type, and planet presence
- **Dual Interface**: Command-line tool and beautiful web application
- **Professional Architecture**: Clean separation of concerns with Repository and Service patterns
- **Type-Safe**: Full type hints throughout the codebase


## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/sbrooksco/StarSystems.git
cd StarSystems

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Or install dependencies only
pip install -r requirements.txt
```
### Development Installation

```bash
pip install -e ".[dev]"
# Or
pip install -r requirements-dev.txt
```

## Quick Start

### Command-Line Interface

```bash
# Initialize the database
starsystems init

# Sync data from NASA Exoplanet Archive
starsystems sync

# List all systems
starsystems list

# Search with filters
starsystems search --distance 100 --spectral-type G K M --has-planets

# Get system details
starsystems info "Kepler-186"

# Show statistics
starsystems stats
```

### Web Application

```bash
# Start the web server
uvicorn starsystems.web.app:app --reload

# Or use the module directly
python -m uvicorn starsystems.web.app:app --reload
```

Then visit http://localhost:8000

### Programmatic Usage

```python
from starsystems import (
    DatabaseConnection, 
    StarSystemRepository,
    ExoplanetService,
    SearchService
)

# Initialize components
db = DatabaseConnection()
db.initialize_schema()

repository = StarSystemRepository(db)
exoplanet_service = ExoplanetService()
search_service = SearchService()

# Fetch and save data
systems = exoplanet_service.fetch_systems()
repository.save_batch(systems)

# Search with filters
all_systems = repository.find_all()
nearby_g_stars = search_service.filter_systems(
    all_systems,
    max_distance=50,
    spectral_types=['G'],
    has_planets=True
)

# Get statistics
stats = search_service.get_statistics(all_systems)
print(f"Total systems: {stats['total_systems']}")
```
## Project Layout
```
starsystems/
├── src/
│   └── starsystems/
│       ├── models/              # Domain models (Planet, StarSystem)
│       ├── database/            # Data persistence (Repository pattern)
│       ├── services/            # Business logic (ExoplanetService, SearchService)
│       ├── cli/                 # Command-line interface
│       └── web/                 # Web application (FastAPI)
│           └── templates/       # HTML templates
├── tests/                       # Test suite
├── data/                        # Database storage (gitignored)
├── scripts/                     # Utility scripts
├── pyproject.toml              # Modern Python packaging
└── requirements.txt            # Dependencies
```
## Architecture

### Layers

1. **Models Layer** (`models/`)
   - Pure domain objects: `Planet`, `StarSystem`
   - Business logic for classification and representation
   - No dependencies on other layers

2. **Database Layer** (`database/`)
   - `DatabaseConnection`: Manages SQLite connections
   - `StarSystemRepository`: CRUD operations (Repository pattern)
   - Isolates data access from business logic

3. **Services Layer** (`services/`)
   - `ExoplanetService`: Fetches data from NASA API
   - `SearchService`: Handles filtering and search logic
   - Contains all business logic

4. **Interface Layers**
   - `cli/`: Command-line interface using argparse
   - `web/`: FastAPI web application with Jinja2 templates

### Design Patterns

- **Repository Pattern**: Clean separation between data access and business logic
- **Dependency Injection**: Services receive dependencies through constructors
- **Service Layer**: Business logic isolated from presentation
- **Single Responsibility**: Each module has one clear purpose

## CLI Commands

```bash
# Initialize database
starsystems init

# Sync data from NASA
starsystems sync

# List systems
starsystems list [--limit N]

# Search with filters
starsystems search [OPTIONS]
  --distance FLOAT          Maximum distance in light years
  --spectral-type TYPE...   Spectral types (e.g., G K M)
  --has-planets             Only systems with planets
  --no-planets              Only systems without planets
  --min-planets N           Minimum number of planets
  --name TEXT               Search by system name

# Get system details
starsystems info SYSTEM_NAME

# Show statistics
starsystems stats
```

## Web API Endpoints

- `GET /systems` - Web UI with filters
- `GET /api/systems` - JSON API for systems with query parameters
- `GET /api/systems/{name}` - Get specific system details
- `GET /api/stats` - Database statistics
- `POST /admin/sync` - Manual data sync (requires admin password)
- `GET /health` - Health check endpoint

### API Query Parameters

- `distance`: Maximum distance in light years
- `spectral_type`: Comma-separated spectral types (e.g., `G,K,M`)
- `has_planets`: Boolean filter for planet presence
- `min_planets`: Minimum number of planets
- `name`: Search by system name (partial match)
- `limit`: Maximum number of results

Example:
```bash
curl "http://localhost:8000/api/systems?distance=100&spectral_type=G,K&has_planets=true&limit=10"
```

## Configuration

### Environment Variables

- `STAR_SYSTEMS_DB`: Database file path (default: `data/star_systems.db`)
- `STARADMIN`: Admin password for web sync (default: `changeme`)
- `RENDER`: Set to `"true"` for Render deployment (uses `/tmp/star_systems.db`)

### Example `.env` file

```bash
STAR_SYSTEMS_DB=/path/to/database.db
STARADMIN=your_secure_password
```

## Deployment

### Render

Create a `Procfile`:
```
web: uvicorn starsystems.web.app:app --host 0.0.0.0 --port $PORT
```

Set environment variables in Render dashboard:
- `RENDER=true`
- `STARADMIN=<your_password>`

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "starsystems.web.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Development

### Running Tests

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# With coverage
pytest --cov=starsystems --cov-report=html
```

### Code Quality

```bash
# Format code
black src/

# Lint
ruff check src/

# Type checking
mypy src/
```

## Data Source

This project uses the [NASA Exoplanet Archive](https://exoplanetarchive.ipac.caltech.edu/) Planetary Systems (PS) table, which contains confirmed exoplanets and their properties.

## License

MIT License - See LICENSE file for details

## Author

Stephen Brooks - [GitHub](https://github.com/sbrooksco)

## Acknowledgments

- NASA Exoplanet Archive for providing the data
- The exoplanet research community
