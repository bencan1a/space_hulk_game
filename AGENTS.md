# AGENTS.md - AI Agent Guidance

**CRITICAL: Always activate the virtual environment before running any commands!**

```bash
# Activate virtual environment (do this FIRST!)
source .venv/bin/activate      # Linux/macOS/WSL
.venv\Scripts\activate         # Windows

# You should see (.venv) prefix in your terminal prompt
```

This is the #1 cause of command failures. Never skip this step.

---

## Quick Reference

**File Organization:**

- `agent-tmp/` - Temporary debugging outputs (gitignored, auto-cleaned after 7 days)
- `agent-projects/` - Active project folders (committed, requires plan.md)
- `docs/` - Permanent documentation (committed)
- `tools/` - Utility scripts (committed)
- `src/` - Source code
- `tests/` - Test suite
- `game-config/` - Game design templates (DO NOT auto-format YAML!)

**Common Commands:**

```bash
# Setup (after activating venv)
./setup.sh              # Linux/macOS
.\setup.ps1             # Windows

# Testing
python -m unittest discover -s tests -v           # Mock mode (default)
RUN_REAL_API_TESTS=1 python -m unittest ...      # Real API mode

# Code Quality
ruff format .           # Auto-format
ruff check .            # Linting
mypy src/ tools/        # Type checking
bandit -r src/          # Security scanning

# CrewAI
crewai run              # Run the crew
python tools/validate_api.py    # Validate API setup
```

---

## Initial Setup Flow

1. **Clone repository** (if not already done)
2. **Run setup script:** `./setup.sh` (creates .venv, installs dependencies, configures .env)
3. **Activate virtual environment:** `source .venv/bin/activate`
4. **Verify setup:** `python tools/validate_api.py`
5. **Run tests:** `python -m unittest discover -s tests -v`

---

## File Organization Standards

### Where to Put Different Types of Content

**agent-tmp/** (Gitignored, Temporary)

- Debug scripts and analysis
- Work-in-progress experiments
- Temporary reports
- Files older than 7 days are auto-cleaned
- Use for: Quick exploration, debugging, throwaway code

**agent-projects/** (Committed, Active Work)

- Ongoing development initiatives
- Each project in its own subdirectory
- MUST have `plan.md` with YAML frontmatter
- Active plans (<21 days) included in CONTEXT.md
- Use for: Multi-day refactoring, feature development, structured projects

**docs/** (Committed, Permanent)

- User-facing documentation
- Architecture decisions
- API documentation (auto-generated)
- Setup guides, quickstarts
- Use for: Finalized, permanent documentation

**tools/** (Committed, Utilities)

- Development scripts
- Validation tools
- Build automation
- Use for: Reusable utility scripts

**Root Directory** (Committed, Configuration Only)

- Configuration files (pyproject.toml, .env, etc.)
- Top-level documentation (README.md, CLAUDE.md, this file)
- Setup scripts (setup.sh, setup.ps1)
- DO NOT put utility scripts here (use tools/ instead)

---

## Code Quality Checklist

Before committing code, ensure ALL of these pass:

- [ ] **Formatting:** `ruff format .` (auto-fixes)
- [ ] **Linting:** `ruff check .` (check for issues)
- [ ] **Type Checking:** `mypy src/ tools/`
- [ ] **Security:** `bandit -r src/`
- [ ] **Tests:** `python -m unittest discover -s tests -v`
- [ ] **Coverage:** >80% on new/changed code

**Handling Unavoidable Warnings:**

If a warning is unavoidable and justified, add explicit comments:

```python
# noqa: E501 - Long URL cannot be split
# type: ignore[attr-defined] - Dynamic attribute from CrewAI
# nosec B603 - Subprocess call to trusted script
```

Always include a brief justification for why the warning must be ignored.

---

## CrewAI Specific Patterns

### Agent Definition Pattern

```python
@agent
def agent_name(self) -> Agent:
    return Agent(
        config=self.agents_config["AgentName"],  # Key MUST match YAML exactly
        llm=self.llm,
        verbose=True
    )
```

### Task Definition Pattern

```python
@task
def task_name(self) -> Task:
    return Task(
        config=self.tasks_config["TaskName"]  # Key MUST match YAML exactly
    )
```

### CRITICAL YAML Configuration Rules

1. **Method names in crew.py must match YAML keys EXACTLY** (case-sensitive)
2. Use folded style (`>`) for multi-line strings in YAML
3. `dependencies:` controls execution order (blocks until complete)
4. `context:` provides data flow without blocking
5. Agent/task configs in `src/space_hulk_game/config/`

### Process Modes

**Sequential Mode (Default, Recommended):**

- All agents work as peers in defined order
- Simplest configuration, most reliable
- No manager delegation overhead
- Use this first to validate functionality

**Hierarchical Mode (Advanced, Use Carefully):**

- NarrativeDirectorAgent acts as manager
- Manager delegates to worker agents
- Can hang with complex dependencies
- Use `create_hierarchical_crew()` method
- Only use after validating sequential mode

**Best Practice:** Start with sequential mode. Only use hierarchical after basic functionality validated.

---

## Testing Methodology

### Mock Mode (Default)

- No API credentials required
- Fast execution, no API costs
- Suitable for CI/CD
- Validates structure and logic
- Run with: `python -m unittest discover -s tests -v`

### Real API Mode

- Requires API keys in .env
- Validates actual LLM behavior
- Use sparingly (costs money, slower)
- Run with: `RUN_REAL_API_TESTS=1 python -m unittest discover -s tests -v`

### Test Naming Convention

```python
def test_function_when_condition_then_expected(self):
    """Test that function does X when Y happens"""
    # Arrange
    # Act
    # Assert
```

### Testing Best Practices

- Establish baseline before writing new tests
- One assertion per test (or closely related assertions)
- Avoid conditional logic in tests
- Use meaningful test names
- Mock external dependencies (API calls, file I/O)

---

## Custom Agent Profiles

Specialized agents available in `.github/agents/`:

- **principal-engineer.md** - Architecture and design guidance
- **python-developer.md** - Python best practices
- **crewai-specialist.md** - CrewAI framework expertise
- **game-mechanics-specialist.md** - Game design patterns
- **testing-specialist.md** - Test strategy and implementation
- **yaml-expert.md** - YAML configuration guidance

Invoke via GitHub Copilot workspace commands or reference directly.

---

## Warhammer 40K / Space Hulk Theme

When working on game content, maintain these themes:

- **Gothic horror:** Dark, oppressive atmosphere
- **Grimdark:** No good choices, only survival
- **Body horror:** Mutations, corruption (Genestealer influence)
- **Military fiction:** Squad tactics, duty, sacrifice
- **Isolation:** Cut off from help, on your own
- **Ancient technology:** Failing systems, machine spirits

**IMPORTANT:** DO NOT apply code formatters to `game-config/*.yaml` files. These contain narrative text that must preserve its formatting.

---

## Common Pitfalls & Solutions

### Pitfall 1: Forgetting to Activate venv

**Symptom:** ModuleNotFoundError, command not found
**Solution:** `source .venv/bin/activate` (see top of this file)

### Pitfall 2: YAML Key Mismatch

**Symptom:** CrewAI can't find agent/task configuration
**Solution:** Ensure method name in crew.py matches key in YAML exactly (case-sensitive)

### Pitfall 3: Hierarchical Mode Hanging

**Symptom:** Crew execution hangs indefinitely
**Solution:** Use sequential mode first, simplify dependencies, disable memory/planning features

### Pitfall 4: Breaking game-config YAML

**Symptom:** Narrative text formatting corrupted
**Solution:** Exclude `game-config/*.yaml` from auto-formatting tools

### Pitfall 5: Missing API Keys

**Symptom:** Real API tests fail, crew can't run
**Solution:** Copy .env.example to .env, add your API keys, run `python tools/validate_api.py`

### Pitfall 6: Type Checking Errors on Third-party Libraries

**Symptom:** mypy complains about crewai, litellm, mem0
**Solution:** Already configured in pyproject.toml to ignore these, if you see errors run `mypy --ignore-missing-imports src/`

---

## LLM Configuration

The project supports multiple LLM providers via litellm. Configure in `.env`:

**Anthropic Claude (Recommended):**

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_MODEL_NAME=claude-3-5-sonnet-20241022
```

**OpenRouter (Access to multiple providers):**

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
```

**OpenAI:**

```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL_NAME=gpt-4
```

**Ollama (Local, Optional):**

```bash
OPENAI_MODEL_NAME=ollama/qwen2.5
OLLAMA_BASE_URL=http://localhost:11434
```

Designed for cloud LLM services by default. Ollama is optional.

---

## Project Structure Context

```
space_hulk_game/
├── .github/
│   ├── agents/              # Custom agent profiles
│   └── workflows/           # CI/CD automation
├── agent-tmp/               # Temporary outputs (gitignored)
├── agent-projects/          # Active projects (committed)
├── docs/                    # Documentation (committed)
├── game-config/             # Game templates (DO NOT auto-format!)
├── project-plans/           # Development plans
├── src/space_hulk_game/
│   ├── config/              # Agent/task YAML configs
│   ├── crew.py              # Main CrewAI implementation
│   ├── main.py              # Entry point
│   └── tools/               # Custom CrewAI tools
├── tests/                   # Test suite
├── tools/                   # Utility scripts
├── .env                     # API keys (gitignored)
├── AGENTS.md                # This file
├── CLAUDE.md                # Detailed project guidance
├── pyproject.toml           # Project configuration
└── setup.sh / setup.ps1     # Setup scripts
```

---

## Additional Resources

- **CLAUDE.md** - Comprehensive project documentation and technical details
- **docs/SETUP.md** - Detailed installation instructions
- **docs/QUICKSTART.md** - Quick reference guide
- **docs/CONTRIBUTING.md** - Development guidelines
- **docs/AGENTS.md** - Agent-specific documentation
- **project-plans/** - Development plans and architecture docs
- **.github/copilot-instructions.md** - GitHub Copilot context

---

## Getting Help

If you encounter issues:

1. Check this file for common pitfalls
2. Verify virtual environment is activated
3. Review CLAUDE.md for detailed guidance
4. Check relevant documentation in docs/
5. Run validation tools: `python tools/validate_api.py`
6. Review test logs for specific errors

---

_Last Updated: 2025-11-10_
_Part of python-template adoption (Phase 1)_
