.PHONY: help install install-dev dev test test-real-api coverage lint format format-check format-frontend format-check-frontend type-check type-check-pre-commit security security-report check-yaml check-markdown check fix lint-files format-files format-frontend-files type-check-files security-files check-yaml-files check-markdown-files fix-files run-crew validate-api validate-config clean

help:
	@echo "Space Hulk Game - Development Commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make install         - Install package in editable mode"
	@echo "  make install-dev     - Install with dev dependencies and pre-commit hooks"
	@echo "  make dev             - Complete development environment setup"
	@echo ""
	@echo "Testing:"
	@echo "  make test            - Run tests (mock mode, no API required)"
	@echo "  make test-real-api   - Run tests with real API (requires API key)"
	@echo "  make coverage        - Generate coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint                 - Check code with Ruff linter"
	@echo "  make format               - Auto-format code using Ruff"
	@echo "  make format-check         - Verify formatting without modifications"
	@echo "  make format-frontend      - Format frontend code with Prettier"
	@echo "  make format-check-frontend- Check frontend formatting with Prettier"
	@echo "  make type-check           - Run MyPy type validation"
	@echo "  make security             - Execute Bandit security scanning"
	@echo "  make security-report      - Generate JSON security report (for CI)"
	@echo "  make check-yaml           - Validate YAML files with yamllint"
	@echo "  make check-markdown       - Validate and auto-fix Markdown files"
	@echo "  make check                - Run all quality checks (auto-fix, lint, type, security, yaml, markdown, test)"
	@echo "  make fix                  - Auto-fix linting issues and reformat code"
	@echo ""
	@echo "CrewAI Specific:"
	@echo "  make run-crew        - Run CrewAI crew"
	@echo "  make validate-api    - Validate API connectivity"
	@echo "  make validate-config - Validate CrewAI configuration"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean           - Remove cache files and old temp files"
	@echo ""
	@echo "NOTE: Ensure tools are available in PATH (activate venv or install system-wide)"
	@echo "  source .venv/bin/activate  (Linux/macOS/WSL)"
	@echo "  .venv\\Scripts\\activate     (Windows)"

# Setup & Installation
install:
	uv pip install -e .

install-dev:
	uv pip install -e ".[dev]"
	@command -v pre-commit >/dev/null 2>&1 && pre-commit install || echo "pre-commit not available yet"

dev: install-dev
	@echo "Development environment ready!"
	@echo "Remember to activate: source .venv/bin/activate"

# Testing
test:
	python -m unittest discover -b -q -s tests

test-real-api:
	RUN_REAL_API_TESTS=1 python -m unittest discover -s tests -v

coverage:
	coverage run -m unittest discover -s tests
	coverage html
	coverage report
	@echo "Coverage report generated in htmlcov/index.html"

# Code Quality
lint:
	ruff check . --fix

format:
	ruff format .

format-check:
	ruff format --check .

format-frontend:
	cd frontend && npm run format

format-check-frontend:
	@if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then \
		cd frontend && npx prettier --check "src/**/*.{ts,tsx,css}" 2>/dev/null || echo "⚠️  Skipping frontend format check (dependencies not installed)"; \
	else \
		echo "⚠️  Skipping frontend format check (frontend not available)"; \
	fi

type-check:
	mypy src/space_hulk_game tests tools *.py

type-check-pre-commit:
	mypy --cache-dir=/dev/null src/space_hulk_game tests tools *.py

security:
	bandit -r src/ -c pyproject.toml

security-report:
	bandit -r src/ -c pyproject.toml -f json -o bandit-report.json

check-yaml:
	yamllint .

check-markdown:
	@command -v markdownlint >/dev/null 2>&1 && markdownlint --fix "**/*.md" --ignore "**/node_modules/**" --ignore "**/.venv/**" --ignore ".venv/**" || echo "⚠️  Skipping markdown check (markdownlint not installed)"

check: fix format-check-frontend check-yaml check-markdown type-check security test
	@echo "✅ All checks passed! (format, lint, prettier, type-check, security, yaml, markdown, test)"

fix:
	ruff check --fix .
	ruff format .
	@if [ -d "frontend" ] && command -v npm >/dev/null 2>&1; then \
		cd frontend && npm run format 2>/dev/null || echo "⚠️  Skipping frontend format (dependencies not installed)"; \
	else \
		echo "⚠️  Skipping frontend format (frontend dir or npm not available)"; \
	fi
	@echo "✅ Code fixed and formatted!"

# Code Quality - File-specific targets (for pre-commit hooks)
# Usage: make lint-files FILES="file1.py file2.py"
lint-files:
	@if [ -n "$(FILES)" ]; then \
		ruff check --fix $(FILES); \
	else \
		ruff check --fix .; \
	fi

format-files:
	@if [ -n "$(FILES)" ]; then \
		ruff format $(FILES); \
	else \
		ruff format .; \
	fi

format-frontend-files:
	@if [ -n "$(FILES)" ]; then \
		cd frontend && npx prettier --write $(FILES); \
	else \
		cd frontend && npm run format; \
	fi

type-check-files:
	@if [ -n "$(FILES)" ]; then \
		mypy --cache-dir=/dev/null --exclude '(backend/)' $(FILES); \
	else \
		mypy --cache-dir=/dev/null --exclude '(backend/)' src/space_hulk_game tests tools *.py; \
	fi

security-files:
	@if [ -n "$(FILES)" ]; then \
		bandit -c pyproject.toml $(FILES); \
	else \
		bandit -r src/ -c pyproject.toml; \
	fi

check-yaml-files:
	@if [ -n "$(FILES)" ]; then \
		yamllint $(FILES); \
	else \
		yamllint .; \
	fi

check-markdown-files:
	@if [ -n "$(FILES)" ]; then \
		command -v markdownlint >/dev/null 2>&1 && markdownlint --fix $(FILES) || echo "⚠️  Skipping markdown check (markdownlint not installed)"; \
	else \
		command -v markdownlint >/dev/null 2>&1 && markdownlint --fix "**/*.md" --ignore "**/node_modules/**" --ignore "**/.venv/**" --ignore ".venv/**" || echo "⚠️  Skipping markdown check (markdownlint not installed)"; \
	fi

fix-files:
	@if [ -n "$(FILES)" ]; then \
		ruff check --fix $(FILES); \
		ruff format $(FILES); \
	else \
		ruff check --fix .; \
		ruff format .; \
	fi
	@echo "✅ Code fixed and formatted!"

# CrewAI Specific
run-crew:
	crewai run

validate-api:
	python tools/validate_api.py

validate-config:
	python -m space_hulk_game.main test 1 test-model

# Maintenance
clean:
	@echo "Cleaning cache files..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@rm -rf build/ dist/ .coverage htmlcov/ .pytest_cache/ .mypy_cache/ .ruff_cache/ .hypothesis/ 2>/dev/null || true
	@echo "Cleaning old agent-tmp files (>7 days)..."
	@find agent-tmp/ -type f -mtime +7 -delete 2>/dev/null || true
	@echo "✅ Cleanup complete!"
