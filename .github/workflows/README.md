# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Space Hulk Game project.

## Available Workflows

### CI/CD Workflows

#### `backend-ci.yml`

Continuous integration for the FastAPI backend.

**Trigger**: Push or PR to `main`/`develop` (when backend files change)
**Jobs**:

- Linting (ruff)
- Type checking (mypy)
- Tests (pytest) on Python 3.10 & 3.11
- Code formatting check

**Duration**: ~2-3 minutes

---

#### `frontend-ci.yml`

Continuous integration for the React frontend.

**Trigger**: Push or PR to `main`/`develop` (when frontend files change)
**Jobs**:

- Linting (ESLint)
- Type checking (TypeScript)
- Code formatting (Prettier)
- Build verification
- Tests on Node 18 & 20

**Duration**: ~2-4 minutes

---

#### `docker-build.yml`

Docker image building and integration testing.

**Trigger**: Push or PR to `main`
**Jobs**:

- Build backend Docker image
- Build frontend Docker image
- Test docker-compose setup

**Duration**: ~3-5 minutes

---

### Manual Workflows

#### `run-crewai-agents.yml`

On-demand workflow to execute the CrewAI agent crew and capture generated game content as artifacts.

**Trigger**: Manual (workflow_dispatch)
**Documentation**: See [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md) for detailed information

## How to Use

1. Navigate to the **Actions** tab in the GitHub repository
2. Select the workflow you want to run
3. Click **Run workflow**
4. Download artifacts when complete

For detailed usage instructions, troubleshooting, and examples, see the [Workflows Documentation](../../docs/WORKFLOWS.md).

## Required Secrets and Variables

The workflows in this repository require the following repository secrets and variables:

**Secrets** (Settings → Secrets and variables → Actions → Secrets):

- `OPENROUTER_API_KEY`: OpenRouter API key for LLM access
- `MEM0_API_KEY`: Mem0 API key for memory management

**Variables** (Settings → Secrets and variables → Actions → Variables):

- `OPENAI_MODEL_NAME`: Model to use (e.g., `openrouter/anthropic/claude-3.5-sonnet`)
  - Optional: defaults to `openrouter/anthropic/claude-3.5-sonnet` if not set

**Setup Guide**: See [docs/SECRETS_SETUP.md](../../docs/SECRETS_SETUP.md) for detailed instructions

## CI/CD Best Practices

The CI/CD workflows follow GitHub Actions security best practices:

- **Explicit Permissions**: All jobs use `permissions: {contents: read}` (principle of least privilege)
- **Path Filtering**: Workflows only run when relevant files change
- **Caching**: Aggressive caching for pip, npm, and Docker layers
- **Matrix Testing**: Test across multiple Python and Node versions
- **Security Scanning**: CodeQL scans all workflow files

### Local Testing

Test workflows locally before pushing:

**Backend**:

```bash
cd backend
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
mypy .
pytest --cov=app
```

**Frontend**:

```bash
cd frontend
npm ci
npm run lint
npx tsc --noEmit
npm run build
```

**Docker**:

```bash
docker compose up -d
curl http://localhost:8000/health
docker compose down
```

## Status Badges

CI status badges are available in the main [README.md](../../README.md).

## Documentation

Full documentation: [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md)
