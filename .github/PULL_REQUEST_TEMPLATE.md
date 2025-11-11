## Description

<!-- Provide a clear and concise description of your changes -->

## Type of Change

<!-- Check all that apply -->

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that causes existing functionality to change)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Refactoring (no functional changes)
- [ ] Tests (adding or updating tests)
- [ ] CI/CD (changes to workflows or automation)
- [ ] CrewAI agent/task configuration
- [ ] Game mechanics or narrative content

## Related Issues

<!-- Link to related issues using #issue_number -->

Fixes #
Related to #

## Changes Made

<!-- List the specific changes made in this PR -->

-
-
-

## Testing

### Test Coverage
- [ ] New unit tests added for new functionality
- [ ] Existing unit tests updated as needed
- [ ] All tests pass locally (`python -m unittest discover -s tests -v`)
- [ ] Integration tests pass (if applicable)
- [ ] Manual testing completed

### Code Quality Checks
- [ ] Code follows project style guide (PEP 8)
- [ ] Linting passes (`ruff check .`)
- [ ] Formatting is correct (`black --check src/`)
- [ ] Type checking passes (`mypy src/`)
- [ ] No debug code or console logs left in
- [ ] Pre-commit hooks pass (if installed)

### CrewAI Specific (if applicable)
- [ ] Agent/task YAML configurations validated
- [ ] Method names match YAML keys exactly (case-sensitive)
- [ ] Crew executes without hanging (sequential mode tested)
- [ ] Output files generated correctly (game-config/*.yaml)
- [ ] LLM integration tested (mock or real API)
- [ ] Configuration templates are properly formatted

### Test Cases Covered
- [ ] CrewAI agent functionality
- [ ] Game narrative generation
- [ ] Puzzle creation and validation
- [ ] Configuration file parsing
- [ ] Memory system integration
- [ ] Error handling
- [ ] Edge cases

### Manual Testing
<!-- Describe manual testing performed -->

```bash
# Commands run to test changes

```

**Test Results:**
-

## Documentation
- [ ] Code includes appropriate docstrings (Google/NumPy style)
- [ ] AGENTS.md updated (if development patterns changed)
- [ ] CLAUDE.md updated (if technical details changed)
- [ ] README.md updated (if user-facing changes)
- [ ] Type hints added for new functions and parameters
- [ ] Complex logic documented with inline comments
- [ ] YAML configurations include helpful comments

## Additional Checklist

<!-- Ensure all items are completed before submitting -->

- [ ] My code follows the project's code style (PEP 8)
- [ ] My changes are minimal and focused
- [ ] I have reviewed my own code before submitting
- [ ] I have checked for backward compatibility issues
- [ ] Branch is up-to-date with base branch
- [ ] Commits are properly formatted and descriptive
- [ ] No merge conflicts
- [ ] Game content follows Warhammer 40K theme (if applicable)

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
