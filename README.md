# StarSystems
Project Layout
```
StarSystems/
├── star_system_app.py          # CLI (text-based) application entry point
├── star_system_gui.py          # (optional) Tkinter GUI entry point
├── models.py                   # Contains StarSystem and Planet classes
├── database.py                 # Handles SQLite persistence
├── utils.py                    # (optional) for CSV import/export, helper functions
│
├── data/
│   ├── star_systems.db         # SQLite database file
│   ├── sample_data.csv         # Example CSV input
│
├── tests/
│   ├── __init__.py
│   ├── test_models.py          # Unit tests for Planet and StarSystem
│   ├── test_database.py        # Tests for persistence layer
│   ├── test_utils.py           # (optional) Tests for CSV import/export
│
├── requirements.txt            # List of dependencies
├── README.md                   # Project description and setup instructions
└── .gitignore                  # (if using Git) ignore db, pycache, etc.


```
Running from the command line:
```
python3 star_system_app.py
```

Running the interactive python for testing:

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

WHAT IS NEXT?

1. How about a web app front end?

    Use Flask for a web interface, not tkinter.

2. Also, figure out a requirements.txt file.


