from setuptools import setup, find_packages

setup(
    name="star_systems",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        # add dependencies here, e.g.:
        # "pandas", "sqlalchemy"
    ],
    entry_points={
        "console_scripts": [
            "starcli=star_systems.star_system_cli:main",
        ],
    },
    author="Your Name",
    description="A command-line Star System classifier and database manager",
    python_requires=">=3.8",
)

