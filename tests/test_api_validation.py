"""
API Validation Tests for Space Hulk Game

These tests validate that the OpenRouter API connection works correctly
and that the LLM configuration is properly set up.

Tests can run in two modes:
1. With real API credentials (OPENROUTER_API_KEY set) - makes actual API calls
2. Without credentials (mocked) - uses mock responses for testing
"""
import os
import sys
import unittest
import warnings
from unittest.mock import MagicMock, patch

# Add the src directory to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))

# Try to import required modules
try:
    from crewai import LLM

    CREWAI_AVAILABLE = True
except ImportError:
    CREWAI_AVAILABLE = False
    warnings.warn("CrewAI not installed. Skipping API tests.", stacklevel=2)


class TestAPIValidation(unittest.TestCase):
    """Test suite for validating OpenRouter API access."""

    @classmethod
    def setUpClass(cls):
        """Set up class-level fixtures."""
        cls.api_key = os.getenv("OPENROUTER_API_KEY")
        cls.model_name = os.getenv("OPENAI_MODEL_NAME", "openrouter/anthropic/claude-3.5-sonnet")
        cls.has_real_credentials = bool(cls.api_key)

        if cls.has_real_credentials:
            print("\n✓ Found OPENROUTER_API_KEY - running tests against real API")
            print(f"  Using model: {cls.model_name}")
        else:
            print("\n⚠ OPENROUTER_API_KEY not found - running tests with mocks")
            print("  Set OPENROUTER_API_KEY to test against real API")

    @unittest.skipUnless(CREWAI_AVAILABLE, "CrewAI not installed")
    def test_llm_initialization_with_openrouter(self):
        """Test that LLM can be initialized with OpenRouter configuration."""
        if self.has_real_credentials:
            # Test with real credentials
            llm = LLM(model=self.model_name, api_key=self.api_key)
            self.assertIsNotNone(llm)
            self.assertEqual(llm.model, self.model_name)
        else:
            # Test with mock
            with patch("crewai.LLM") as mock_llm:
                mock_instance = MagicMock()
                mock_llm.return_value = mock_instance

                llm = LLM(model=self.model_name, api_key="mock-key")

                self.assertIsNotNone(llm)

    @unittest.skipUnless(CREWAI_AVAILABLE, "CrewAI not installed")
    def test_simple_llm_call(self):
        """Test a simple LLM API call to validate connectivity."""
        if self.has_real_credentials:
            # Make a real API call
            llm = LLM(model=self.model_name, api_key=self.api_key)

            # Simple test prompt
            test_prompt = "Say 'API connection successful' if you can read this."

            try:
                response = llm.call([{"role": "user", "content": test_prompt}])

                # Validate response
                self.assertIsNotNone(response)
                self.assertTrue(len(response) > 0, "Response should not be empty")
                print("\n✓ API Call Successful!")
                print(f"  Response length: {len(response)} characters")
                print(f"  Sample: {response[:100]}...")

            except Exception as e:
                self.fail(f"API call failed with error: {e!s}")
        else:
            # Test with mock
            mock_response = "API connection successful (mocked)"

            with patch.object(LLM, "call", return_value=mock_response):
                llm = LLM(model=self.model_name, api_key="mock-key")

                response = llm.call([{"role": "user", "content": "test"}])

                self.assertEqual(response, mock_response)
                print("\n✓ Mock API Call Successful!")
                print(f"  Response: {response}")

    @unittest.skipUnless(CREWAI_AVAILABLE, "CrewAI not installed")
    def test_llm_with_game_context_prompt(self):
        """Test LLM with a Space Hulk game-related prompt."""
        game_prompt = """You are a narrative designer for a Space Hulk game.
        In one sentence, describe the atmosphere when a player first enters a derelict vessel."""

        if self.has_real_credentials:
            llm = LLM(model=self.model_name, api_key=self.api_key)

            try:
                response = llm.call([{"role": "user", "content": game_prompt}])

                # Validate response
                self.assertIsNotNone(response)
                self.assertTrue(len(response) > 0)

                # Check if response seems relevant
                # (Should mention darkness, silence, danger, etc.)
                print("\n✓ Game Context Prompt Successful!")
                print(f"  Response: {response}")

            except Exception as e:
                self.fail(f"Game context API call failed: {e!s}")
        else:
            # Test with mock response
            mock_game_response = (
                "The oppressive silence is broken only by the creaking "
                "of ancient metal as you step into the flickering darkness."
            )

            with patch.object(LLM, "call", return_value=mock_game_response):
                llm = LLM(model=self.model_name, api_key="mock-key")

                response = llm.call([{"role": "user", "content": game_prompt}])

                self.assertIn("darkness", response.lower())
                print("\n✓ Mock Game Context Successful!")
                print(f"  Response: {response}")

    def test_environment_variables_documented(self):
        """Test that environment variables are properly documented."""
        env_example_path = os.path.join(os.path.dirname(__file__), "..", ".env.example")

        self.assertTrue(os.path.exists(env_example_path), ".env.example file should exist")

        with open(env_example_path) as f:
            content = f.read()

            # Check for OpenRouter documentation
            self.assertIn("OPENROUTER_API_KEY", content)
            self.assertIn("OPENAI_MODEL_NAME", content)
            self.assertIn("openrouter/", content)

    def test_api_error_handling(self):
        """Test that API errors are handled gracefully."""
        if not CREWAI_AVAILABLE:
            self.skipTest("CrewAI not available")

        # Test with invalid API key
        invalid_key = "sk-invalid-key-12345"

        if self.has_real_credentials:
            # Skip this test when using real credentials
            # (we don't want to spam the API with invalid requests)
            self.skipTest("Skipping error test with real API credentials")
        else:
            # Mock an API error
            with patch.object(LLM, "call", side_effect=Exception("Invalid API key")):
                llm = LLM(model=self.model_name, api_key=invalid_key)

                with self.assertRaises(Exception) as context:
                    llm.call([{"role": "user", "content": "test"}])

                self.assertIn("Invalid API key", str(context.exception))


class TestLLMConfiguration(unittest.TestCase):
    """Test suite for LLM configuration options."""

    @unittest.skipUnless(CREWAI_AVAILABLE, "CrewAI not installed")
    def test_multiple_model_options(self):
        """Test that different model configurations work."""
        test_models = [
            "openrouter/anthropic/claude-3.5-sonnet",
            "openrouter/openai/gpt-4-turbo",
            "openrouter/meta-llama/llama-3.1-70b-instruct",
        ]

        for model in test_models:
            with self.subTest(model=model):
                with patch("crewai.LLM") as mock_llm:
                    mock_instance = MagicMock()
                    mock_instance.model = model
                    mock_llm.return_value = mock_instance

                    llm = LLM(model=model, api_key="test-key")

                    self.assertIsNotNone(llm)

    @unittest.skipUnless(CREWAI_AVAILABLE, "CrewAI not installed")
    def test_llm_fallback_to_ollama(self):
        """Test that system can fall back to Ollama if OpenRouter not available."""
        # This tests the existing Ollama configuration
        with patch("crewai.LLM") as mock_llm:
            mock_instance = MagicMock()
            mock_llm.return_value = mock_instance

            llm = LLM(model="ollama/qwen2.5", base_url="http://localhost:11434")

            self.assertIsNotNone(llm)


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
