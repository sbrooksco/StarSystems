# Testing Guide for StarSystems

This guide explains how to run and write tests for the StarSystems application.

## Test Structure

```
tests/
├── conftest.py                    # Shared fixtures
├── test_models/
│   ├── test_planet.py            # Planet model tests
│   └── test_star_system.py       # StarSystem model tests
├── test_database/
│   ├── test_connection.py        # Database connection tests
│   └── test_repository.py        # Repository pattern tests
└── test_services/
    ├── test_exoplanet_service.py # NASA API service tests
    └── test_search_service.py    # Search/filter service tests
```

## Running Tests
Activate the virtual env:
```
source venv/bin/activate
```
### Run All Tests

```bash
# Basic run
pytest

# With verbose output
pytest -v

# With coverage report
pytest --cov=starsystems --cov-report=term-missing

# With HTML coverage report
pytest --cov=starsystems --cov-report=html
```

### Run Specific Test Files

```bash
# Run just model tests
pytest tests/test_models/

# Run just database tests
pytest tests/test_database/

# Run a specific test file
pytest tests/test_models/test_planet.py

# Run a specific test class
pytest tests/test_models/test_planet.py::TestPlanet

# Run a specific test method
pytest tests/test_models/test_planet.py::TestPlanet::test_planet_creation
```

## Test Organization

### 1. Fixtures (conftest.py)

Fixtures provide reusable test data and setup:

```python
@pytest.fixture
def temp_db_path():
    """Provides a temporary database for testing."""
    
@pytest.fixture
def sample_planet():
    """Provides a sample planet instance."""
    
@pytest.fixture
def sample_systems():
    """Provides multiple test systems."""
```

**Usage:**
```python
def test_something(sample_planet):
    # sample_planet is automatically provided by pytest
    assert sample_planet.name == "Earth"
```

### 2. Test Classes

Tests are organized into classes by functionality:

```python
class TestPlanet:
    """Tests for basic Planet functionality"""
    
class TestPlanetEdgeCases:
    """Tests for edge cases and boundaries"""
```

### 3. Test Methods

Each test method tests one specific behavior:

```python
def test_planet_classification_terrestrial(self):
    """Test that Earth-like planets are classified as Terrestrial."""
    planet = Planet("Earth", 1.0, 1.0, 1.0)
    assert planet.classify() == "Terrestrial"
```

## Writing New Tests

### Testing Models

Models are pure Python classes with no dependencies - easy to test:

```python
def test_new_planet_feature(self):
    """Test description."""
    # Arrange
    planet = Planet("Test Planet", 5.0, 2.0, 1.5)
    
    # Act
    result = planet.some_method()
    
    # Assert
    assert result == expected_value
```

### Testing Database Operations

Use the `repository` fixture for database tests:

```python
def test_save_and_retrieve(repository):
    """Test saving and retrieving a system."""
    # Arrange
    system = StarSystem("Test", "G2V", 10.0)
    
    # Act
    repository.save(system)
    loaded = repository.find_by_name("Test")
    
    # Assert
    assert loaded is not None
    assert loaded.name == "Test"
```

### Testing Services

#### With Real Data

```python
def test_search_filter(search_service, sample_systems):
    """Test filtering systems."""
    results = search_service.filter_systems(
        sample_systems,
        max_distance=50.0
    )
    assert all(s.distance_ly <= 50.0 for s in results)
```

#### With Mocked API Calls

```python
from unittest.mock import Mock, patch

@patch('starsystems.services.exoplanet_service.requests.get')
def test_fetch_from_nasa(mock_get):
    """Test fetching data from NASA API."""
    # Arrange
    mock_response = Mock()
    mock_response.json.return_value = [...]
    mock_get.return_value = mock_response
    
    service = ExoplanetService()
    
    # Act
    systems = service.fetch_systems()
    
    # Assert
    assert len(systems) > 0
```

## Test Coverage

### Check Coverage

```bash
# Generate coverage report
pytest --cov=starsystems --cov-report=term-missing

# See which lines aren't covered
pytest --cov=starsystems --cov-report=html
# Then open htmlcov/index.html
```

## Common Testing Patterns

### 1. Arrange-Act-Assert (AAA)

```python
def test_example():
    # Arrange - set up test data
    planet = Planet("Earth", 1.0, 1.0, 1.0)
    
    # Act - perform the action
    classification = planet.classify()
    
    # Assert - verify the result
    assert classification == "Terrestrial"
```

### 2. Testing for Exceptions

```python
def test_invalid_input():
    with pytest.raises(ValueError):
        Planet("Test", -1.0, -1.0, -1.0)
```

### 3. Parametrized Tests

Test multiple inputs efficiently:

```python
@pytest.mark.parametrize("mass,radius,expected", [
    (0.05, 0.5, "Dwarf Planet"),
    (1.0, 1.0, "Terrestrial"),
    (5.0, 2.0, "Super-Earth"),
    (300.0, 10.0, "Gas Giant"),
])
def test_planet_classification(mass, radius, expected):
    planet = Planet("Test", mass, radius, 1.0)
    assert planet.classify() == expected
```

### 4. Testing with Temporary Files

```python
def test_with_temp_file(temp_db_path):
    """temp_db_path fixture provides a temporary database."""
    db = DatabaseConnection(temp_db_path)
    # Test operations
    # File is automatically cleaned up
```

## Mocking External Dependencies

### Mock HTTP Requests

```python
from unittest.mock import Mock, patch

@patch('starsystems.services.exoplanet_service.requests.get')
def test_api_call(mock_get):
    # Set up mock
    mock_response = Mock()
    mock_response.json.return_value = {"data": "test"}
    mock_get.return_value = mock_response
    
    # Test code that calls requests.get()
    service = ExoplanetService()
    result = service.fetch_systems()
```

### Mock Database

Handled by fixtures - each test gets a fresh temporary database.

## Continuous Integration

### GitHub Actions Example

Create `.github/workflows/tests.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements-dev.txt
    
    - name: Run tests
      run: |
        pytest --cov=starsystems --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

## Debugging Failed Tests

### Run with print statements

```bash
pytest -s  # Shows print() output
```

### Run with pdb debugger

```bash
pytest --pdb  # Drops into debugger on failure
```

### Run last failed tests only

```bash
pytest --lf  # Last failed
pytest --ff  # Failed first, then others
```

### Increase verbosity

```bash
pytest -vv  # Very verbose
```

## Example Test Session

```bash
# 1. Run all tests
$ pytest -v

# 2. Check coverage
$ pytest --cov=starsystems --cov-report=term-missing

# 3. Run specific area
$ pytest tests/test_models/ -v

# 4. Generate HTML coverage report
$ pytest --cov=starsystems --cov-report=html

# 5. Open coverage report
$ open htmlcov/index.html  # macOS
$ xdg-open htmlcov/index.html  # Linux
```

## Resources

- pytest documentation: https://docs.pytest.org/
- pytest fixtures: https://docs.pytest.org/en/stable/fixture.html
- unittest.mock: https://docs.python.org/3/library/unittest.mock.html
- Coverage.py: https://coverage.readthedocs.io/

