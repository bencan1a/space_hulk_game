## Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Mark the relevant option with an 'x' -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Test improvement
- [ ] Performance improvement
- [ ] Code refactoring
- [ ] Other (please describe):

## Related Issues

<!-- Link to related issues using #issue_number -->

Fixes #
Related to #

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Testing Performed

<!-- Describe the testing you performed to verify your changes -->

### Test Coverage
- [ ] Added unit tests
- [ ] Added integration tests
- [ ] Added e2e tests
- [ ] Existing tests pass
- [ ] Coverage maintained or improved

### Manual Testing
<!-- Describe manual testing performed -->

```bash
# Commands run to test changes

```

**Test Results:**
-

### Test Cases Covered
- [ ] CrewAI agent functionality
- [ ] Game narrative generation
- [ ] Puzzle creation and validation
- [ ] Configuration file parsing
- [ ] Memory system integration
- [ ] Error handling
- [ ] Edge cases

## Checklist

<!-- Ensure all items are completed before submitting -->

- [ ] My code follows the project's code style (black, ruff)
- [ ] I have run `uv run black src/` to format my code
- [ ] I have run `uv run ruff check --fix src/` to fix linting issues
- [ ] I have run `uv run mypy src/` to check types
- [ ] I have added tests that prove my fix/feature works
- [ ] All tests pass locally (`uv run pytest`)
- [ ] I have updated relevant documentation (README.md, AGENTS.md, etc.)
- [ ] I have added docstrings to new functions (Google/NumPy style)
- [ ] My changes are minimal and focused
- [ ] I have reviewed my own code before submitting
- [ ] I have checked for backward compatibility issues
- [ ] I have updated YAML configurations if needed
- [ ] I have validated CrewAI agent configurations

## Breaking Changes

<!-- If this is a breaking change, describe the impact and migration path -->

**Impact:**

**Migration Guide:**

## Performance Impact

<!-- Describe any performance implications of your changes -->

- [ ] No performance impact
- [ ] Performance improvement (describe below)
- [ ] Potential performance impact (describe below and provide benchmarks)

## Documentation Updates

<!-- List documentation files updated -->

- [ ] README.md
- [ ] docs/AGENTS.md
- [ ] .github/copilot-instructions.md
- [ ] docs/CONTRIBUTING.md
- [ ] YAML configuration files (agents.yaml, tasks.yaml, etc.)
- [ ] Code comments/docstrings
- [ ] Other:

## Screenshots (if applicable)

<!-- Add screenshots for UI or output changes -->

## Additional Notes

<!-- Any additional information that reviewers should know -->

## Reviewer Checklist

<!-- For maintainers reviewing this PR -->

- [ ] Code follows project conventions
- [ ] Tests are comprehensive
- [ ] Documentation is complete
- [ ] No security vulnerabilities introduced
- [ ] Backward compatibility maintained (or breaking change justified)
- [ ] Performance impact acceptable
- [ ] CI/CD checks pass
