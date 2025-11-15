# Pre-Checkin Checklist

This document outlines the required checks that **MUST** be run before committing any code changes to ensure code quality and prevent CI failures.

## Required Command

Before committing any code, **ALWAYS** run:

```bash
make check
```

This command runs the core quality checks:
- **Linting** (`make lint`) - Runs Ruff linter with auto-fix
- **Type Checking** (`make type-check`) - Runs MyPy type validation
- **Tests** (`make test`) - Runs the test suite

## Why This Matters

Running `make check` before committing:
- ✅ Catches linting errors early
- ✅ Ensures type safety
- ✅ Verifies tests pass
- ✅ Prevents CI pipeline failures
- ✅ Maintains code quality standards

## Full Check Suite

For comprehensive validation (recommended before creating a PR), run:

```bash
make check-all
```

This runs all checks including:
- Code formatting
- Security scanning
- YAML validation
- Frontend checks (if applicable)

## Auto-Fix Issues

To automatically fix linting and formatting issues:

```bash
make fix
```

This will:
- Fix linting issues with Ruff
- Auto-format code with Ruff
- Format frontend code (if npm is available)

## Pre-Commit Hooks

The repository uses pre-commit hooks that automatically run these checks on staged files.

To install pre-commit hooks:

```bash
make install-dev
```

## Quick Reference

| Command | Purpose |
|---------|---------|
| `make check` | **Required before commit** - Run core checks |
| `make fix` | Auto-fix linting and formatting issues |
| `make check-all` | Run all quality checks |
| `make lint` | Check code with Ruff linter |
| `make format` | Auto-format code |
| `make type-check` | Run MyPy type validation |
| `make test` | Run test suite |

## For AI Agents

**IMPORTANT**: When making code changes, always:

1. Run `make check` before committing
2. Fix any errors reported by the checks
3. Re-run `make check` to verify all issues are resolved
4. Only then commit the changes

**Never commit code without running `make check` first.**
