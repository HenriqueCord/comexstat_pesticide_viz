# setup.py
from setuptools import setup, find_packages
from pathlib import Path

# Read requirements.txt
requirements = Path("requirements.txt").read_text().splitlines()

setup(
    name="comexstat_viz",
    version="0.1",
    packages=find_packages(),
    install_requires=requirements,
)