# GitHub Actions Workflows

This directory contains GitHub Actions workflows for the Space Hulk Game project.

## Available Workflows

### `run-crewai-agents.yml`

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

## Documentation

Full documentation: [docs/WORKFLOWS.md](../../docs/WORKFLOWS.md)
