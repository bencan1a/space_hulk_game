# Space Hulk Game Tests

This directory contains tests for the Space Hulk Game implementation.

## Running the Tests

To run all tests, execute the following command from the project root:

```bash
python -m unittest discover -s tests
```

To run a specific test file:

```bash
python -m unittest tests.test_space_hulk_game
```

## Test Coverage

The tests cover the following areas:

1. **Input Preparation**: Tests for the prepare_inputs method.
2. **Error Handling**: Tests for the handle_task_failure method.
3. **Output Processing**: Tests for the process_output method.

## Adding New Tests

When adding new features, please add corresponding tests to maintain code quality. Note that tests for AI-generated outputs should focus on structure rather than deterministic content validation.