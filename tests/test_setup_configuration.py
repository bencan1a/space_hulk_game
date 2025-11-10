"""
Integration tests for setup scripts and configuration.

These tests verify that:
1. All setup files exist and are valid
2. Configuration files are properly structured
3. Dependencies are correctly specified
"""

import os
import unittest
from pathlib import Path


class TestSetupConfiguration(unittest.TestCase):
    """Test cases for setup and configuration files."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_setup_sh_exists(self):
        """Test that setup.sh exists and is executable."""
        setup_sh = self.project_root / "setup.sh"
        self.assertTrue(setup_sh.exists(), "setup.sh should exist")
        # Check if file is executable (on Unix-like systems)
        if os.name != 'nt':  # Not Windows
            self.assertTrue(os.access(setup_sh, os.X_OK), "setup.sh should be executable")

    def test_setup_ps1_exists(self):
        """Test that setup.ps1 exists."""
        setup_ps1 = self.project_root / "setup.ps1"
        self.assertTrue(setup_ps1.exists(), "setup.ps1 should exist")

    def test_setup_py_exists(self):
        """Test that setup.py exists."""
        setup_py = self.project_root / "setup.py"
        self.assertTrue(setup_py.exists(), "setup.py should exist")

    def test_pyproject_toml_exists(self):
        """Test that pyproject.toml exists."""
        pyproject = self.project_root / "pyproject.toml"
        self.assertTrue(pyproject.exists(), "pyproject.toml should exist")

    def test_env_example_exists(self):
        """Test that .env.example exists."""
        env_example = self.project_root / ".env.example"
        self.assertTrue(env_example.exists(), ".env.example should exist")

    def test_setup_md_exists(self):
        """Test that SETUP.md documentation exists."""
        setup_md = self.project_root / "docs" / "SETUP.md"
        self.assertTrue(setup_md.exists(), "docs/SETUP.md should exist")

    def test_pyproject_toml_has_dependencies(self):
        """Test that pyproject.toml contains required dependencies."""
        pyproject = self.project_root / "pyproject.toml"
        content = pyproject.read_text()

        # Check for required dependencies
        required_deps = [
            "crewai",
            "mem0ai",
            "pyyaml",
            "litellm"
        ]

        for dep in required_deps:
            self.assertIn(dep, content.lower(),
                         f"pyproject.toml should contain {dep} dependency")

    def test_pyproject_toml_has_dev_dependencies(self):
        """Test that pyproject.toml contains development dependencies."""
        pyproject = self.project_root / "pyproject.toml"
        content = pyproject.read_text()

        # Check for dev dependencies
        dev_deps = [
            "pytest",
            "black",
            "flake8",
            "mypy"
        ]

        for dep in dev_deps:
            self.assertIn(dep, content.lower(),
                         f"pyproject.toml should contain {dep} in dev dependencies")

    def test_pyproject_toml_has_scripts(self):
        """Test that pyproject.toml contains project scripts."""
        pyproject = self.project_root / "pyproject.toml"
        content = pyproject.read_text()

        # Check for entry points
        self.assertIn("[project.scripts]", content,
                     "pyproject.toml should have [project.scripts] section")
        self.assertIn("space_hulk_game", content.lower(),
                     "pyproject.toml should have space_hulk_game entry point")

    def test_env_example_has_required_vars(self):
        """Test that .env.example contains required environment variables."""
        env_example = self.project_root / ".env.example"
        content = env_example.read_text()

        # Check for key configuration variables
        required_vars = [
            "OPENAI_MODEL_NAME",
            "OLLAMA_BASE_URL",
            "LOG_LEVEL"
        ]

        for var in required_vars:
            self.assertIn(var, content,
                         f".env.example should contain {var} configuration")

    def test_setup_sh_has_shebang(self):
        """Test that setup.sh has proper shebang."""
        setup_sh = self.project_root / "setup.sh"
        first_line = setup_sh.read_text().split('\n')[0]
        self.assertTrue(first_line.startswith("#!/bin/bash"),
                       "setup.sh should start with #!/bin/bash shebang")

    def test_documentation_files_exist(self):
        """Test that all documentation files exist."""
        # Root level should have a README and CONTRIBUTING.md
        root_readme = self.project_root / "README.md"
        self.assertTrue(root_readme.exists(), "README.md should exist at root")

        root_contributing = self.project_root / "CONTRIBUTING.md"
        self.assertTrue(root_contributing.exists(), "CONTRIBUTING.md should exist at root")

        # Main documentation should be in docs/
        docs_dir = self.project_root / "docs"
        self.assertTrue(docs_dir.exists(), "docs/ directory should exist")

        docs = ["README.md", "SETUP.md"]
        for doc in docs:
            doc_path = docs_dir / doc
            self.assertTrue(doc_path.exists(), f"docs/{doc} should exist")

    def test_gitignore_excludes_env(self):
        """Test that .gitignore excludes .env files."""
        gitignore = self.project_root / ".gitignore"
        if gitignore.exists():
            content = gitignore.read_text()
            self.assertIn(".env", content,
                         ".gitignore should exclude .env files")


class TestProjectStructure(unittest.TestCase):
    """Test cases for project structure."""

    def setUp(self):
        """Set up test fixtures."""
        self.project_root = Path(__file__).parent.parent

    def test_src_directory_exists(self):
        """Test that src directory exists."""
        src_dir = self.project_root / "src" / "space_hulk_game"
        self.assertTrue(src_dir.exists(), "src/space_hulk_game directory should exist")

    def test_config_directory_exists(self):
        """Test that config directory exists."""
        config_dir = self.project_root / "src" / "space_hulk_game" / "config"
        self.assertTrue(config_dir.exists(), "config directory should exist")

    def test_config_files_exist(self):
        """Test that required config files exist."""
        config_dir = self.project_root / "src" / "space_hulk_game" / "config"
        config_files = ["agents.yaml", "tasks.yaml", "gamedesign.yaml"]

        for config_file in config_files:
            config_path = config_dir / config_file
            self.assertTrue(config_path.exists(),
                           f"{config_file} should exist in config directory")

    def test_main_files_exist(self):
        """Test that main Python files exist."""
        src_dir = self.project_root / "src" / "space_hulk_game"
        main_files = ["__init__.py", "main.py", "crew.py"]

        for main_file in main_files:
            main_path = src_dir / main_file
            self.assertTrue(main_path.exists(),
                           f"{main_file} should exist in src/space_hulk_game")

    def test_tests_directory_exists(self):
        """Test that tests directory exists."""
        tests_dir = self.project_root / "tests"
        self.assertTrue(tests_dir.exists(), "tests directory should exist")


if __name__ == '__main__':
    unittest.main()
