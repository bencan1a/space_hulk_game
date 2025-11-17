# Pre-Checkin Checklist

This document outlines the required checks that **MUST** be run before committing any code changes to ensure code quality and prevent CI failures.

## Required Command

Before committing any code, **ALWAYS** run:

```bash
make check
```

This command runs **all** quality checks:

- **Auto-fix** - Ruff linting and formatting (auto-fixes issues)
- **Prettier** - Frontend code formatting check (TypeScript, CSS)
- **YAML Validation** - yamllint
- **Markdown Linting** - markdownlint (auto-fixes issues)
- **Type Checking** - MyPy type validation
- **Security Scanning** - Bandit security scan
- **Tests** - Full test suite

## Why This Matters

Running `make check` before committing:

- ✅ Auto-fixes linting and formatting issues
- ✅ Catches type safety issues early
- ✅ Validates configuration files (YAML)
- ✅ Ensures documentation quality (Markdown)
- ✅ Identifies security vulnerabilities
- ✅ Verifies tests pass
- ✅ Prevents CI pipeline failures
- ✅ Maintains code quality standards

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

**🚨 CRITICAL: Pre-commit Hook Policy**

- Pre-commit hooks run automatically on every `git commit`
- If hooks fail, **FIX THE ISSUES** - do NOT bypass hooks
- **NEVER use `git commit --no-verify` or `git commit -n`**
- Bypassing hooks violates code quality standards and will cause CI failures
- If hooks fail repeatedly, run `make check` to identify and fix the root cause

## Quick Reference

| Command                      | Purpose                                                                                                        |
| ---------------------------- | -------------------------------------------------------------------------------------------------------------- |
| `make check`                 | **Required before commit** - Run all quality checks (auto-fix, prettier, yaml, markdown, type, security, test) |
| `make fix`                   | Auto-fix linting and formatting issues only (without running checks)                                           |
| `make lint`                  | Check code with Ruff linter                                                                                    |
| `make format`                | Auto-format code                                                                                               |
| `make format-frontend`       | Format frontend code with Prettier                                                                             |
| `make format-check-frontend` | Check frontend formatting with Prettier                                                                        |
| `make type-check`            | Run MyPy type validation                                                                                       |
| `make security`              | Run Bandit security scan                                                                                       |
| `make check-yaml`            | Validate YAML files                                                                                            |
| `make check-markdown`        | Validate and auto-fix Markdown files                                                                           |
| `make test`                  | Run test suite                                                                                                 |

## For AI Agents

**IMPORTANT**: When making code changes, always:

1. Run `make check` before committing
2. Fix any errors reported by the checks
3. Re-run `make check` to verify all issues are resolved
4. Only then commit the changes

**Never commit code without running `make check` first.**
