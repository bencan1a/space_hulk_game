"""
Tests for the ProductDesignerAgent.
These tests verify that the ProductDesignerAgent is properly configured and can be instantiated.
"""

import os
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add the src directory to the path so we can import the module
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))


class TestProductDesignerAgent(unittest.TestCase):
    """Test cases for the ProductDesignerAgent configuration."""

    def test_agent_exists_in_yaml_config(self):
        """Test that ProductDesignerAgent exists in agents.yaml configuration."""
        import yaml

        # Load the agents configuration
        config_path = Path(__file__).parent.parent / "src" / "space_hulk_game" / "config" / "agents.yaml"
        with open(config_path, encoding="utf-8") as f:
            agents_config = yaml.safe_load(f)

        # Verify ProductDesignerAgent exists
        self.assertIn("ProductDesignerAgent", agents_config)

        # Verify required fields
        agent_config = agents_config["ProductDesignerAgent"]
        self.assertIn("role", agent_config)
        self.assertIn("goal", agent_config)
        self.assertIn("description", agent_config)
        self.assertIn("backstory", agent_config)

    def test_agent_role_and_goal(self):
        """Test that ProductDesignerAgent has appropriate role and goal."""
        import yaml

        config_path = Path(__file__).parent.parent / "src" / "space_hulk_game" / "config" / "agents.yaml"
        with open(config_path, encoding="utf-8") as f:
            agents_config = yaml.safe_load(f)

        agent_config = agents_config["ProductDesignerAgent"]

        # Verify role contains product design or UX keywords
        role = agent_config["role"].lower()
        self.assertTrue(
            any(keyword in role for keyword in ["product", "designer", "ux", "experience"]),
            f"Role should contain product design or UX keywords: {agent_config['role']}"
        )

        # Verify goal mentions user needs, requirements, or design
        goal = agent_config["goal"].lower()
        self.assertTrue(
            any(keyword in goal for keyword in ["user", "requirement", "design", "need"]),
            f"Goal should mention user needs or requirements: {agent_config['goal']}"
        )

    def test_agent_backstory_contains_key_competencies(self):
        """Test that ProductDesignerAgent backstory mentions key competencies."""
        import yaml

        config_path = Path(__file__).parent.parent / "src" / "space_hulk_game" / "config" / "agents.yaml"
        with open(config_path, encoding="utf-8") as f:
            agents_config = yaml.safe_load(f)

        backstory = agents_config["ProductDesignerAgent"]["backstory"].lower()

        # Verify key competencies are mentioned
        key_competencies = [
            "human-centered",
            "user",
            "prd",
            "experience design",
            "user stories",
            "user journey"
        ]

        found_competencies = [comp for comp in key_competencies if comp in backstory]
        self.assertGreater(
            len(found_competencies),
            3,
            f"Backstory should mention multiple key competencies. Found: {found_competencies}"
        )

    @patch('sys.path', sys.path + [str(Path(__file__).parent.parent / 'src')])
    def test_agent_method_exists_in_crew(self):
        """Test that ProductDesignerAgent method exists in SpaceHulkGame crew."""
        try:
            # Try to import - skip test if dependencies not available
            sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
            from space_hulk_game.crew import SpaceHulkGame

            # Create instance
            game = SpaceHulkGame()

            # Verify the method exists
            self.assertTrue(hasattr(game, 'ProductDesignerAgent'))
            self.assertTrue(callable(game.ProductDesignerAgent))
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping test due to missing dependencies: {e}")

    def test_agent_can_be_instantiated(self):
        """Test that ProductDesignerAgent can be instantiated."""
        try:
            # Try to import - skip test if dependencies not available
            sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
            from space_hulk_game.crew import SpaceHulkGame

            game = SpaceHulkGame()
            agent = game.ProductDesignerAgent()

            # Verify agent was created
            self.assertIsNotNone(agent)
            # Verify it has the expected attributes from crewai.Agent
            self.assertTrue(hasattr(agent, 'role'))
        except ModuleNotFoundError as e:
            self.skipTest(f"Skipping test due to missing dependencies: {e}")


if __name__ == "__main__":
    unittest.main()
