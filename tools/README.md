# Utility Tools

This directory contains utility scripts for development, testing, and automation.

## Available Tools

### validate_api.py (to be moved here in Wave 2)
Validates LLM API connectivity and configuration.

**Usage:**
```bash
python tools/validate_api.py
```

### test_connectivity.py (to be moved here in Wave 2)
Tests network connectivity to various services.

**Usage:**
```bash
python tools/test_connectivity.py
```

### kloc_report.py (to be moved here in Wave 2)
Generates lines-of-code reports for the project.

**Usage:**
```bash
python tools/kloc_report.py
```

### configure_mem0.py (to be moved here in Wave 2)
Configures Mem0 memory system for CrewAI agents.

**Usage:**
```bash
python tools/configure_mem0.py
```

## Adding New Tools

When adding new utility scripts:
1. Place in this `tools/` directory
2. Add appropriate shebang (`#!/usr/bin/env python3`)
3. Include comprehensive docstring
4. Update this README
5. Add to `pyproject.toml` [tool.pyright] include list
6. Consider adding Makefile shortcut
