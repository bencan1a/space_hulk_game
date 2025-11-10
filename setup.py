"""
Setup script for Space Hulk Game.

This file provides backward compatibility for older installation methods.
Modern installations should use pyproject.toml with uv or pip.
"""

from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        name="space_hulk_game",
        use_scm_version=False,
        packages=find_packages(where="src"),
        package_dir={"": "src"},
        python_requires=">=3.10,<3.13",
    )
