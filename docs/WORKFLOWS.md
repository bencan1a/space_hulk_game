# GitHub Actions Workflows

This document describes the GitHub Actions workflows available in this repository.

## Overview

The Space Hulk Game project uses GitHub Actions to automate testing and agent execution. All workflows can be found in `.github/workflows/`.

## Available Workflows

### Run CrewAI Agents

**File**: `.github/workflows/run-crewai-agents.yml`  
**Trigger**: Manual (workflow_dispatch)  
**Purpose**: Execute the CrewAI agent crew and capture generated game content as artifacts

#### Description

This workflow runs the complete CrewAI agent system against OpenRouter (Claude 3.5 Sonnet) and Mem0 to generate game content. The generated files are saved as downloadable artifacts that persist across multiple runs.

#### When to Use

- Testing agent configurations
- Generating new game content for evaluation
- Validating changes to agent prompts or tasks
- Creating baseline outputs for comparison
- Debugging agent behavior in a clean environment

#### How to Run

1. **Navigate to Actions**:
   - Go to the repository on GitHub
   - Click the "Actions" tab
   - Select "Run CrewAI Agents" from the workflow list

2. **Trigger the Workflow**:
   - Click "Run workflow" button
   - Select the branch to run from (typically `main` or your feature branch)
   - (Optional) Specify a game scenario (defaults to `example4_space_hulk`)
   - Click "Run workflow" to start

3. **Monitor Execution**:
   - The workflow will appear in the workflow runs list
   - Click on the run to see real-time logs
   - Execution typically takes 5-15 minutes depending on the scenario complexity

4. **Download Artifacts**:
   - Once complete, scroll to the bottom of the workflow run page
   - Download the artifacts:
     - `game-config-YYYYMMDD_HHMMSS`: Generated YAML files
     - `execution-logs-YYYYMMDD_HHMMSS`: Detailed execution logs
     - `execution-summary-YYYYMMDD_HHMMSS`: Summary of the run

#### Configuration

The workflow requires the following repository secrets to be configured:

- **`OPENROUTER_API_KEY`**: Your OpenRouter API key for LLM access
- **`MEM0_API_KEY`**: Your Mem0 API key for memory management

**Optional repository variable:**

- **`OPENAI_MODEL_NAME`**: Model to use (defaults to `openrouter/anthropic/claude-3.5-sonnet` if not set)

**To set up secrets and variables**, see the detailed guide: **[SECRETS_SETUP.md](SECRETS_SETUP.md)**

Quick setup:
1. Go to repository Settings → Secrets and variables → Actions
2. Add secrets in the **Secrets** tab
3. Add variables in the **Variables** tab (optional)

#### Outputs

The workflow generates several artifacts:

##### 1. Game Configuration Files (`game-config-*`)
Contains all generated YAML files from the agent execution:
- `narrative_map.yaml`: Story structure and branching paths
- `plot_outline.yaml`: Main plot points and narrative arc
- `prd_document.yaml`: Product requirements for the game
- `puzzle_design.yaml`: Puzzle mechanics and solutions
- `scene_texts.yaml`: Detailed scene descriptions and dialogue

**Retention**: 90 days

##### 2. Execution Logs (`execution-logs-*`)
Contains detailed logs from the workflow execution:
- `crew_run_output.log`: Complete output from `crewai run`
- `run_log.txt`: Additional runtime logs (if generated)

**Retention**: 30 days

##### 3. Execution Summary (`execution-summary-*`)
A markdown file summarizing:
- Run timestamp and configuration
- List of generated files with sizes
- Links to other artifacts

**Retention**: 90 days

#### Environment Details

The workflow runs in a fresh Ubuntu environment with:
- Python 3.11
- UV package manager for fast dependency installation
- All project dependencies installed from `pyproject.toml`
- Environment variables configured from repository secrets

#### Customization

You can customize the workflow by:

1. **Changing the LLM Model**:
   Edit the `OPENAI_MODEL_NAME` in the workflow file:
   ```yaml
   OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
   ```
   
   Other options:
   - `openrouter/openai/gpt-4-turbo`
   - `openrouter/meta-llama/llama-3.1-70b-instruct`
   - See all models at: https://openrouter.ai/models

2. **Adjusting Artifact Retention**:
   Modify the `retention-days` parameter:
   ```yaml
   retention-days: 90  # Change to desired number of days
   ```

3. **Adding Environment Variables**:
   Add variables to the "Configure environment variables" step:
   ```yaml
   DEBUG=true
   LITELLM_LOG=DEBUG
   ```

#### Troubleshooting

**Workflow fails with "secrets not found"**:
- Ensure `OPENROUTER_API_KEY` and `MEM0_API_KEY` are configured in repository secrets
- Check that you have the required permissions to access secrets

**No artifacts generated**:
- Check the workflow logs for errors during execution
- Verify that agents are writing to the `game-config/` directory
- Ensure the workflow completed (even with errors, artifacts should be uploaded with `if: always()`)

**Execution takes too long**:
- The default timeout is 6 hours
- For complex scenarios, consider breaking into smaller tasks
- Check OpenRouter rate limits and quotas

**Generated content differs from local runs**:
- The workflow uses a clean environment each time
- Mem0 memory may differ from your local state
- LLM responses can vary between runs due to non-deterministic nature

#### Cost Considerations

Running this workflow incurs costs from:
- **OpenRouter**: Charges per token based on model used
- **Mem0**: Charges based on memory operations
- **GitHub Actions**: Free for public repos, minutes counted for private repos

Estimated cost per run: $0.10 - $2.00 depending on scenario complexity and model choice.

#### Best Practices

1. **Test locally first**: Run `crewai run` locally before using the workflow
2. **Use descriptive branch names**: Makes it easier to track which runs belong to which feature
3. **Download artifacts promptly**: While they're retained for 90 days, download important results sooner
4. **Compare outputs**: Use diff tools to compare outputs between runs
5. **Version control**: Consider committing particularly good outputs to a `examples/` directory
6. **Clean up**: Delete old workflow runs and artifacts you no longer need to save storage

#### Example Use Cases

##### Scenario 1: Testing a New Agent Configuration
```
1. Create a branch: feature/new-puzzle-agent
2. Modify agents.yaml and tasks.yaml
3. Run workflow from the feature branch
4. Download and review generated puzzle_design.yaml
5. Iterate on configuration based on results
```

##### Scenario 2: Generating Content for Review
```
1. Run workflow with default settings
2. Download game-config artifact
3. Review narrative_map.yaml and scene_texts.yaml
4. Provide feedback or use in game development
```

##### Scenario 3: Comparing Model Performance
```
1. Run workflow with Claude 3.5 Sonnet
2. Edit workflow to use GPT-4 Turbo
3. Run workflow again
4. Compare outputs from both artifacts
5. Choose best model for your needs
```

## Future Workflows

Planned workflows for future development:

- **Run Tests**: Automated testing on pull requests
- **Deploy Documentation**: Publish docs to GitHub Pages
- **Release Build**: Create game releases with artifacts
- **Scheduled Content Generation**: Weekly automated content runs

## Contributing

When adding new workflows:

1. Place workflow files in `.github/workflows/`
2. Use descriptive names (kebab-case.yml)
3. Add comprehensive comments
4. Document in this file
5. Test thoroughly before merging
6. Consider cost and runtime impacts

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax Reference](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [OpenRouter Documentation](https://openrouter.ai/docs)
- [Mem0 Documentation](https://docs.mem0.ai/)
- [CrewAI Documentation](https://docs.crewai.com/)
