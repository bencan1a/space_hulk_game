"""
Pytest configuration file for test suite.

This file is automatically loaded by pytest and configures test behavior.
"""

import os
from pathlib import Path


def pytest_configure(config):
    """
    Load environment variables from .env file before running tests.

    This allows tests to access environment variables defined in .env,
    including OPENROUTER_API_KEY and RUN_REAL_API_TESTS.
    """
    # Find project root (parent of tests directory)
    project_root = Path(__file__).parent.parent
    env_file = project_root / ".env"

    if env_file.exists():
        # Manually load .env file (without requiring python-dotenv)
        with open(env_file, encoding="utf-8") as f:
            for line in f:
                line = line.strip()  # noqa: PLW2901
                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue
                # Parse key=value pairs
                if "=" in line:
                    # Split only on first =, in case value contains =
                    key, value = line.split("=", 1)
                    key = key.strip()
                    # Remove inline comments
                    if "#" in value:
                        value = value.split("#")[0]
                    value = value.strip()
                    # Only set if not already in environment (env vars take precedence)
                    if key not in os.environ:
                        os.environ[key] = value

        print(f"\n✓ Loaded environment variables from {env_file}")

        # Display test configuration
        if os.getenv("RUN_REAL_API_TESTS") == "1":
            print("✓ Real API tests ENABLED")
            print(
                f"  OPENROUTER_API_KEY: {'set' if os.getenv('OPENROUTER_API_KEY') else 'NOT SET'}"
            )
            print(f"  Model: {os.getenv('OPENAI_MODEL_NAME', 'not specified')}")
        else:
            print("⚠ Real API tests DISABLED (set RUN_REAL_API_TESTS=1 to enable)")
    else:
        print(f"\n⚠ No .env file found at {env_file}")
