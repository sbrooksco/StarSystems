# StarSystems

A command line tool for managing, searching, and importing exoplanet star systems.
## Setup

### Clone the repository:
git clone <your-repo-url>
cd star-system-classifier

### Create a virtual environment:

python3 -m venv .venv

source .venv/bin/activate # macOS/Linux

.venv\Scripts\activate # Windows

### Install Dependencies:
pip install -r requirements.txt

### List available commands:
python star_system_cli.py --help

#### TODO 
Use setup.py or pyproject.toml to make it cleaner\
Use Flask for a web interface, not tkinter.

## Project Layout
```
StarSystems/
├── star_system_app.py          # StarSystems application class
├── star_system_cli.py          # CLI (text-based) application entry point
├── models.py                   # Contains StarSystem and Planet classes
├── database.py                 # Handles SQLite persistence
├── utils.py                    # CSV import/export, helper functions
├── web_data.py                 # Web import/export, helper functions
│
├── data/
│   ├── star_systems.db         # SQLite database file (not stored in git)
│   ├── sample_data.csv         # Example CSV input
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Unit tests for Planet and StarSystem
│   ├── test_database.py        # Tests for persistence layer
│   ├── test_utils.py           # Tests for CSV import/export
│   ├── test_import_from_web.py # Tests for web import
│
├── requirements.txt            # List of dependencies
├── README.md                   # Project description and setup instructions
└── .gitignore                  # Ignore db, pycache, etc.
```
## Running from the command line:
```
python3 star_system_cli.py
```
## Purposes of requirements.txt and setup.py/pyproject.toml:

| File                                  | Purpose                                                                                           | Used By                       | Typical Contents                                |
| ------------------------------------- | ------------------------------------------------------------------------------------------------- | ----------------------------- | ----------------------------------------------- |
| **`requirements.txt`**                | Lists *exact dependencies* for your runtime environment (used for deployment or reproducibility). | Developers, CI/CD, production | `flask==2.3.2`, `sqlalchemy>=2.0`               |
| **`setup.py`** / **`pyproject.toml`** | Define *metadata and dependencies for packaging your project as a Python module or tool*.         | `pip`, `setuptools`, `build`  | Name, version, dependencies, entry points, etc. |

### Summary
Use requirements.txt to describe your working environment.

Use setup.py + pyproject.toml` to make your project installable and shareable.

### To install it as a local cli do the following at the project root (where setup.py resides)
```
pip install -e .  (Or just pip install . if you don't want editable mode)
```
Then you can run the command:
```
starcli create "Epsilon Eridani" K2V 10.5 --planet "Epsilon Eridani b" 1.5 1.1 3.4 
```
or
```
starcli list
```

### Install dependencies for running or developing the project
```
pip install -r requirements.txt
```

## Running the interactive python for testing:

% python3
Python 3.13.7 (main, Aug 14 2025, 11:12:11) [Clang 17.0.0 (clang-1700.0.13.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
```
>>> from database import init_db, load_all_systems
>>> init_db()
>>> systems = load_all_systems()
>>> for s in systems: print(s)
```

++++++++++++++++++++++++++++

Running unit tests:

At project root:
```
% python3 -m unittest discover -s tests
```


