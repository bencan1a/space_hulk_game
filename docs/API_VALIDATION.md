# API Validation Instructions

This document provides step-by-step instructions for validating that the OpenRouter API is properly configured and accessible.

## Prerequisites

1. OpenRouter API key (from https://openrouter.ai/keys)
2. Python dependencies installed (`pip install -e .`)

## Quick Validation

The fastest way to validate your API setup is using the validation script:

```bash
# Set your API key
export OPENROUTER_API_KEY=sk-or-v1-your-key-here

# Optional: Choose a specific model
export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet

# Run validation
python validate_api.py
```

**Expected Output (Success):**
```
======================================================================
OpenRouter API Validation
======================================================================

✓ Found OPENROUTER_API_KEY (length: 48)
✓ Using model: openrouter/anthropic/claude-3.5-sonnet

Checking dependencies...
✓ CrewAI installed

Testing API connection...
✓ LLM instance created successfully

Making test API call...
✓ API call successful!

Response:
----------------------------------------------------------------------
API validation successful
----------------------------------------------------------------------

======================================================================
✅ API VALIDATION SUCCESSFUL

You can now run the Space Hulk Game with OpenRouter:
  crewai run

Or run integration tests:
  RUN_REAL_API_TESTS=1 python -m unittest tests.test_integration_sequential
======================================================================
```

**Expected Output (Failure - No API Key):**
```
======================================================================
OpenRouter API Validation
======================================================================

❌ ERROR: OPENROUTER_API_KEY environment variable not set

To fix this:
  1. Get an API key from: https://openrouter.ai/keys
  2. Set the environment variable:
     export OPENROUTER_API_KEY=sk-or-v1-your-key-here
  3. Optionally set the model:
     export OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet

======================================================================
❌ API VALIDATION FAILED

Please fix the issues above and try again.
======================================================================
```

## Running Tests with Real API

### 1. API Validation Tests

These tests validate basic API connectivity:

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
python -m unittest tests.test_api_validation -v
```

**Expected Output:**
```
test_api_error_handling ... ok
test_environment_variables_documented ... ok
test_llm_initialization_with_openrouter ... ok
test_llm_with_game_context_prompt ... ok
test_simple_llm_call ... ok
test_llm_fallback_to_ollama ... ok
test_multiple_model_options ... ok

----------------------------------------------------------------------
Ran 7 tests in 2.451s

OK

✓ Found OPENROUTER_API_KEY - running tests against real API
  Using model: openrouter/anthropic/claude-3.5-sonnet

✓ API Call Successful!
  Response length: 156 characters
  Sample: API validation successful...

✓ Game Context Prompt Successful!
  Response: The oppressive silence is broken only by the creaking...
```

### 2. Integration Tests

These tests validate the full sequential agent system:

```bash
export OPENROUTER_API_KEY=sk-or-v1-your-key-here
export RUN_REAL_API_TESTS=1
python -m unittest tests.test_integration_sequential -v
```

**Note:** Integration tests with real API are disabled by default to avoid unnecessary API costs. Enable with `RUN_REAL_API_TESTS=1`.

## Troubleshooting

### Error: "Invalid API key"

**Possible causes:**
1. API key is incorrect or expired
2. API key doesn't have sufficient permissions
3. Network connectivity issues

**Solutions:**
- Verify your API key at https://openrouter.ai/
- Check API key format (should start with `sk-or-v1-`)
- Ensure you have API credits available
- Test network connectivity: `curl https://openrouter.ai/api/v1/models`

### Error: "Model not available"

**Possible causes:**
1. Model name is incorrect
2. Model requires additional permissions
3. Model is temporarily unavailable

**Solutions:**
- Check available models at https://openrouter.ai/models
- Use full model path: `openrouter/provider/model-name`
- Try a different model (e.g., `openrouter/anthropic/claude-3.5-sonnet`)

### Error: "Rate limit exceeded"

**Possible causes:**
1. Too many API requests in short time
2. Account rate limits

**Solutions:**
- Wait a few seconds and try again
- Check your rate limits at https://openrouter.ai/
- Consider upgrading your account tier

### Tests are slow

**Normal behavior:**
- Real API tests make actual network requests
- Response times vary by model and server load
- Expect 1-5 seconds per test with real API

**To speed up:**
- Use mock mode (default, no API key needed)
- Set `SKIP_SLOW_TESTS=1` to skip optional tests
- Only run specific test files you need

## Running in CI/CD

### GitHub Actions (with secrets)

```yaml
name: API Validation Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install -e .

      - name: Run API validation
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
          OPENAI_MODEL_NAME: ${{ vars.OPENAI_MODEL_NAME }}
        run: |
          python validate_api.py
          python -m unittest tests.test_api_validation -v
```

### Without Secrets (Mock Mode)

```yaml
- name: Run tests (mock mode)
  run: |
    pip install -e .
    python -m unittest discover -s tests -v
  # No secrets needed - tests will use mocks
```

## Next Steps

Once API validation is successful:

1. **Run the full crew:**
   ```bash
   crewai run
   ```

2. **Test with custom prompts:**
   ```bash
   crewai run --input '{"prompt": "Your custom game scenario"}'
   ```

3. **Run integration tests:**
   ```bash
   export RUN_REAL_API_TESTS=1
   python -m unittest tests.test_integration_sequential -v
   ```

4. **Monitor API usage:**
   - Check usage at https://openrouter.ai/activity
   - Set up billing alerts
   - Monitor costs per request

## Cost Considerations

**Real API Testing:**
- Each test makes 1-2 API calls
- Cost depends on model choice
- Example: Claude 3.5 Sonnet ~$0.003 per test
- Full test suite: ~$0.05-0.10

**Recommendations:**
- Use mock mode for development (free)
- Run real API tests before releases only
- Monitor API usage dashboard
- Set up budget alerts

## Support

If you continue to have issues:

1. Check the [tests/README.md](tests/README.md) for detailed testing documentation
2. Review the [.env.example](.env.example) file for configuration options
3. Visit https://openrouter.ai/docs for API documentation
4. Check GitHub issues for known problems

## Summary Checklist

- [ ] API key obtained from OpenRouter
- [ ] Environment variable set (`OPENROUTER_API_KEY`)
- [ ] Dependencies installed (`pip install -e .`)
- [ ] Validation script passes (`python validate_api.py`)
- [ ] API tests pass (`python -m unittest tests.test_api_validation -v`)
- [ ] (Optional) Integration tests pass with `RUN_REAL_API_TESTS=1`

Once all checks pass, your OpenRouter API is properly configured and ready to use!
