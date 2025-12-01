# Space Hulk Game - AI Agent Context

Generated: 2025-12-01 03:35:31

---

## Project Overview

[![Backend CI](https://github.com/bencan1a/space_hulk_game/actions/workflows/backend-ci.yml/badge.svg)](https://github.com/bencan1a/space_hulk_game/actions/workflows/backend-ci.yml)
[![Frontend CI](https://github.com/bencan1a/space_hulk_game/actions/workflows/frontend-ci.yml/badge.svg)](https://github.com/bencan1a/space_hulk_game/actions/workflows/frontend-ci.yml)
[![Docker Build](https://github.com/bencan1a/space_hulk_game/actions/workflows/docker-build.yml/badge.svg)](https://github.com/bencan1a/space_hulk_game/actions/workflows/docker-build.yml)

A text-based adventure game set in the Warhammer 40K universe, powered by CrewAI multi-agent system.

## API Documentation

Detailed API documentation available in `docs/_generated/api/`

Key modules:
- `space_hulk_game.crew` - Main CrewAI implementation
- `space_hulk_game.engine` - Game engine components
- `space_hulk_game.quality` - Quality evaluation system

## Project Structure

```
space_hulk_game/
├── src/space_hulk_game/  # Source code
│   ├── config/           # Agent/task YAML configs
│   ├── engine/           # Game engine
│   ├── quality/          # Quality evaluators
│   └── crew.py           # Main CrewAI crew
├── tests/                # Test suite
├── tools/                # Utility scripts
├── docs/                 # Documentation
├── game-config/          # Game templates
├── agent-projects/       # Active projects
└── agent-tmp/            # Temporary files
```

## Key Documentation

- **AGENTS.md** - AI agent guidance (start here!)
- **CLAUDE.md** - Comprehensive project documentation
- **README.md** - Project overview and setup
- **docs/SETUP.md** - Detailed installation guide
- **docs/QUICKSTART.md** - Quick reference

