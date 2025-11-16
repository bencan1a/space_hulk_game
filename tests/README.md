# Space Hulk Game Tests

This directory contains comprehensive tests for the Space Hulk Game implementation, including API validation and end-to-end integration tests.

## Test Files

### Unit Tests

- **`test_space_hulk_game.py`**: Core functionality tests using mocks
- **`test_crew_improvements.py`**: Crew configuration, agents, and tasks tests
- **`test_setup_configuration.py`**: Project structure and setup validation

### Integration Tests

- **`test_api_validation.py`**: OpenRouter API connectivity and LLM validation tests
- **`test_integration_sequential.py`**: End-to-end sequential agent system tests

## Running Tests

### All Tests (Mock Mode - Default)

```bash
# Run all tests with mocked responses (fast, no API required)
python -m unittest discover -s tests -v
```

### API Validation Tests

```bash
# Run with mocked API (no credentials needed)
python -m unittest tests.test_api_validation -v

# Run with real API (requires OPENROUTER_API_KEY)
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
python -m unittest tests.test_api_validation -v
```

### Integration Tests

```bash
# Run with mocked responses (fast)
python -m unittest tests.test_integration_sequential -v

# Run with real API (slow, requires API key)
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
export RUN_REAL_API_TESTS=1
python -m unittest tests.test_integration_sequential -v
```

### Specific Test File

```bash
python -m unittest tests.test_space_hulk_game -v
```

## API Validation Script

A standalone script to quickly validate OpenRouter API connectivity:

```bash
python validate_api.py
```

This will check your API key and make a test call to verify everything is working.

## Environment Variables

| Variable | Purpose | Required | Example |
|----------|---------|----------|---------|
| `OPENROUTER_API_KEY` | OpenRouter API key | For real API tests | `sk-or-v1-...` |
| `OPENAI_MODEL_NAME` | Model to use | Optional | `openrouter/anthropic/claude-3.5-sonnet` |
| `RUN_REAL_API_TESTS` | Enable real API tests | Optional | `1` |
| `SKIP_SLOW_TESTS` | Skip slow integration tests | Optional | `1` |

## Test Modes

### Mock Mode (Default)

- ✅ No API credentials required
- ✅ Fast execution
- ✅ No API costs
- ✅ Suitable for CI/CD
- Uses mocked LLM responses

### Real API Mode

- ⚠️ Requires OPENROUTER_API_KEY
- ⚠️ Makes actual API calls
- ⚠️ Incurs API costs
- ⚠️ Slower execution
- Validates real LLM behavior

## Setting Up

### 1. Install Dependencies

```bash
pip install -e .
```

### 2. (Optional) Configure API Access

For testing with real API:

```bash
# Get an API key from https://openrouter.ai/keys
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Choose a model (optional, defaults to Claude 3.5 Sonnet)
export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
```

Or create a `.env` file:

```bash
cp .env.example .env
# Edit .env and add your API key
```

## Test Coverage

The test suite includes 54+ test cases covering:

1. **API Validation**
   - LLM initialization with OpenRouter
   - Simple API call validation
   - Game context prompt testing
   - Error handling
   - Multiple model configurations

2. **End-to-End Integration**
   - Full crew initialization
   - Input validation (prepare_inputs)
   - All 6 agent creation
   - All task creation
   - Crew configuration
   - Output processing and metadata
   - Error recovery mechanisms
   - Task dependencies

3. **Unit Tests**
   - Input preparation
   - Error handling
   - Output processing
   - Configuration validation
   - Project structure

## Continuous Integration

Tests automatically run in mock mode if no API key is provided, making them suitable for CI/CD:

```yaml
# Example GitHub Actions
- name: Run tests
  run: |
    pip install -e .
    python -m unittest discover -s tests -v
```

## Troubleshooting

**Tests fail with "CrewAI not installed":**

```bash
pip install -e .
```

**Tests fail with "Invalid API key":**

- Verify your API key at <https://openrouter.ai/>
- Run `python validate_api.py` to diagnose
- Ensure the key is properly exported

**Tests are slow:**

- Use mock mode (default) for faster tests
- Set `SKIP_SLOW_TESTS=1`
- Only use real API mode when necessary

**Import errors:**

```bash
# Run tests from project root
cd /path/to/space_hulk_game
python -m unittest discover -s tests -v
```

## Adding New Tests

When adding new features:

1. Add unit tests with mocks first
2. Add integration tests if needed
3. Document any new environment variables
4. Ensure all tests pass in mock mode
5. Optionally validate with real API

Note: Tests for AI-generated outputs should focus on structure rather than deterministic content validation.

## Resources

- [CrewAI Documentation](https://docs.crewai.com/)
- [OpenRouter API](https://openrouter.ai/)
- [Python unittest](https://docs.python.org/3/library/unittest.html)
- [Project README](../README.md)
