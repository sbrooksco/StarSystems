Running from the command line:

python3 star_system_app.py


Running the interactive python for testing:

% python3
Python 3.13.7 (main, Aug 14 2025, 11:12:11) [Clang 17.0.0 (clang-1700.0.13.3)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> from database import init_db, load_all_systems
>>> init_db()
>>> systems = load_all_systems()
>>> for s in systems: print(s)
... 
Star System: Solar System
 (G2V, 0.0 ly)
   Planets:
 Earth: Mass=1.0 Earth masses, Radius=1.0 Earth radii, Orbit=1.0 AU, (Terrestial)
 Mars: Mass=0.107 Earth masses, Radius=0.53 Earth radii, Orbit=1.52 AU, (Terrestial)
Star System: Alpha Centauri
 (G2V, 4.37 ly)
   Planets:
 Proxima b: Mass=1.27 Earth masses, Radius=1.1 Earth radii, Orbit=0.05 AU, (Terrestial)
