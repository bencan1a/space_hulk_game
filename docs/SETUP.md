# Setup Guide

This guide provides detailed instructions for setting up the Space Hulk Game development environment on different platforms.

## Table of Contents

- [Quick Start](#quick-start)
- [Prerequisites](#prerequisites)
- [Automated Setup](#automated-setup)
- [Manual Setup](#manual-setup)
- [Troubleshooting](#troubleshooting)
- [Environment Configuration](#environment-configuration)
- [Verifying Installation](#verifying-installation)

## Quick Start

### Linux/macOS

```bash
# Clone the repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Run the automated setup script
./setup.sh

# Activate the virtual environment
source .venv/bin/activate
```

### Windows

```powershell
# Clone the repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Run the automated setup script
.\setup.ps1

# Activate the virtual environment
.venv\Scripts\activate
```

## Prerequisites

### Required Software

1. **Python 3.10, 3.11, or 3.12**
   - Download from [python.org](https://www.python.org/downloads/)
   - Verify installation: `python --version` or `python3 --version`

2. **Git** (for cloning the repository)
   - Download from [git-scm.com](https://git-scm.com/)
   - Verify installation: `git --version`

### Optional Software

- **Ollama** (for local LLM support - optional)
  - Only needed if you want to use a local LLM instead of cloud services
  - Can be installed with setup script flags (see below)
  - Linux/macOS: Use `./setup.sh --with-ollama --with-model`
  - Windows: Download from [ollama.com/download/windows](https://ollama.com/download/windows)

## Automated Setup

The automated setup scripts handle all dependency installation and configuration. **By default, the scripts do NOT install Ollama** - they are configured for cloud LLM services like Anthropic Claude, OpenRouter, or OpenAI.

### Linux/macOS Setup Script

The `setup.sh` script provides the following options:

```bash
# Standard installation (cloud LLM services, no Ollama)
./setup.sh

# Install with Ollama for local LLM
./setup.sh --with-ollama --with-model

# Install development dependencies
./setup.sh --dev

# Combine flags
./setup.sh --with-ollama --with-model --dev
```

**What the script does:**

1. ✓ Checks Python version compatibility
2. ✓ Installs UV package manager
3. ✓ Creates `.venv` virtual environment
4. ✓ Installs Python dependencies in the virtual environment
5. ✓ Creates `.env` configuration file
6. ✓ Verifies installation
7. ✓ Optionally installs Ollama (with `--with-ollama` flag)
8. ✓ Optionally downloads qwen2.5 model (with `--with-model` flag)

### Windows Setup Script

The `setup.ps1` script provides the following options:

```powershell
# Standard installation (cloud LLM services, no Ollama)
.\setup.ps1

# Install with Ollama for local LLM
.\setup.ps1 -WithOllama -WithModel

# Install development dependencies
.\setup.ps1 -Dev

# Combine flags
.\setup.ps1 -WithOllama -WithModel -Dev
```

**Note for Windows users:** You may need to allow script execution:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Manual Setup

If you prefer to install dependencies manually or the automated script fails, follow these steps:

### 1. Install UV Package Manager

UV is a fast Python package installer and resolver.

**Linux/macOS:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Alternative (using pip):**

```bash
pip install uv
```

### 2. Install Ollama (Optional)

Ollama provides local LLM support. You can skip this if you plan to use OpenAI API.

**Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**macOS:**

```bash
# Download from https://ollama.com/download
# Or use Homebrew:
brew install ollama
```

**Windows:**

- Download installer from [ollama.com/download/windows](https://ollama.com/download/windows)

### 3. Download Qwen2.5 Model (Optional)

If you installed Ollama:

```bash
# Start Ollama service (if not already running)
ollama serve

# In a new terminal, pull the model
ollama pull qwen2.5
```

### 4. Create Virtual Environment

Create a virtual environment to isolate project dependencies:

```bash
# Create virtual environment
python -m venv .venv

# Activate the virtual environment
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
```

### 5. Install Python Dependencies

Using UV (recommended):

```bash
# Standard installation
uv pip install -e .

# With development dependencies
uv pip install -e ".[dev]"
```

Using pip:

```bash
# Standard installation
pip install -e .

# With development dependencies
pip install -e ".[dev]"
```

Using crewai CLI:

```bash
crewai install
```

### 6. Create Environment Configuration

Create a `.env` file in the project root:

```bash
# Linux/macOS
cp .env.example .env

# Or create manually
cat > .env << 'EOF'
# Space Hulk Game Environment Configuration

# OpenAI API Key (optional, for using OpenAI models instead of Ollama)
# OPENAI_API_KEY=your_openai_api_key_here

# Mem0 API Key (optional, for cloud-based memory)
# MEM0_API_KEY=your_mem0_api_key_here

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434

# Model Configuration
OPENAI_MODEL_NAME=ollama/qwen2.5

# Logging Level
LOG_LEVEL=INFO
EOF
```

## Environment Configuration

The `.env` file controls various aspects of the application. Here are the key configuration options:

### LLM Configuration

The project supports multiple LLM providers through [litellm](https://docs.litellm.ai/docs/providers). Configure your preferred provider in the `.env` file:

**Option 1: Use Anthropic Claude (Recommended)**

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_MODEL_NAME=claude-3-5-sonnet-20241022
```

Available models:

- `claude-3-5-sonnet-20241022` - Recommended, most capable
- `claude-3-opus-20240229` - Most powerful, higher cost
- `claude-3-sonnet-20240229` - Balanced performance and cost
- `claude-3-haiku-20240307` - Fastest and cheapest

Get your API key from: [console.anthropic.com](https://console.anthropic.com/)

**Option 2: Use OpenRouter (Access to Multiple Providers)**

```bash
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENAI_MODEL_NAME=openrouter/anthropic/claude-3.5-sonnet
# or
OPENAI_MODEL_NAME=openrouter/openai/gpt-4-turbo
# or
OPENAI_MODEL_NAME=openrouter/meta-llama/llama-3.1-70b-instruct
```

**Option 3: Use OpenAI API**

```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-4
# or
OPENAI_MODEL_NAME=gpt-3.5-turbo  # Cheaper alternative
```

Get your API key from: [platform.openai.com/api-keys](https://platform.openai.com/api-keys)

**Option 4: Use Ollama (Local, Optional)**

```bash
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_MODEL_NAME=ollama/qwen2.5
```

Best for: Privacy, offline work, no API costs. Requires local installation using `./setup.sh --with-ollama --with-model`.

OpenRouter provides unified access to models from Anthropic, OpenAI, Meta, Google, and more. See all available models at: [openrouter.ai/models](https://openrouter.ai/models)

Get your API key from: [openrouter.ai/keys](https://openrouter.ai/keys)

**Option 5: Use Azure OpenAI (Enterprise)**

```bash
AZURE_API_KEY=your-azure-key-here
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-02-15-preview
OPENAI_MODEL_NAME=azure/your-deployment-name
```

**Other Supported Providers:**

Litellm supports many other providers including:

- Cohere
- Hugging Face
- Replicate
- Vertex AI (Google)
- Bedrock (AWS)
- And more

See the full list at: [docs.litellm.ai/docs/providers](https://docs.litellm.ai/docs/providers)

### Using Environment Secrets (CI/CD and Test Environments)

For automated testing, CI/CD pipelines, or containerized deployments, you can set API keys as environment variables instead of using a `.env` file. The application will automatically use environment variables if they're set.

**GitHub Actions Example:**

```yaml
name: Test with LLM
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          OPENAI_MODEL_NAME: claude-3-5-sonnet-20241022
        run: |
          ./setup.sh
          python -m unittest discover -s tests
```

**Docker/Docker Compose Example:**

```bash
# Docker run
docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
           -e OPENAI_MODEL_NAME=claude-3-5-sonnet-20241022 \
           space-hulk-game

# Docker Compose
# docker-compose.yml
services:
  app:
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - OPENAI_MODEL_NAME=claude-3-5-sonnet-20241022
```

**Setting Secrets in GitHub:**

1. Go to your repository → Settings → Secrets and variables → Actions
2. Click "New repository secret"
3. Add secrets like:
   - `OPENAI_API_KEY`
   - `ANTHROPIC_API_KEY`
   - `OPENROUTER_API_KEY`
   - `MEM0_API_KEY`

**Environment Variable Priority:**

The application checks for configuration in this order:

1. Environment variables (highest priority)
2. `.env` file in the project root
3. Default values (for optional settings)

### Memory Configuration

**Option 1: Local Memory (Default)**

No configuration needed. The application uses local memory by default.

**Option 2: Mem0 Cloud Memory**

```bash
MEM0_API_KEY=your-mem0-api-key-here
```

To get a Mem0 API key, visit [mem0.ai](https://mem0.ai/).

### Logging Configuration

```bash
# Set logging level: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
```

## Verifying Installation

### 1. Activate Virtual Environment

The setup script creates a `.venv` virtual environment. You must activate it before running commands:

```bash
# Linux/macOS/WSL
source .venv/bin/activate

# Windows
.venv\Scripts\activate

# You should see (.venv) prefix in your terminal prompt
```

**Note:** VS Code will automatically detect and use the `.venv` virtual environment after you reload the window.

### 2. Check Python Environment

```bash
# Check Python version (should be from .venv)
python --version

# Should output: Python 3.10.x, 3.11.x, or 3.12.x
```

### 3. Check UV Installation

```bash
uv --version
```

### 4. Check Ollama Installation (if applicable)

```bash
# Check if Ollama is installed
ollama --version

# Check if Ollama service is running
ollama list

# Should show qwen2.5 model if downloaded
```

### 5. Verify Python Dependencies

```bash
# Ensure virtual environment is activated first!
# Check if crewai is installed
python -c "import crewai; print(crewai.__version__)"

# Check if other dependencies are installed
python -c "import mem0; import yaml; import litellm; print('All dependencies OK')"
```

### 6. Run Tests

```bash
# Ensure virtual environment is activated first!
# Run the test suite
python -m unittest discover -s tests -v

# All tests should pass
```

### 7. Run the Application

```bash
# Ensure virtual environment is activated first!

# If using Ollama, ensure it's running first
ollama serve  # In a separate terminal

# Run the game
crewai run

# Or use the Python entry point
python -m space_hulk_game.main
```

## Troubleshooting

### Common Issues

#### Issue: Python version incompatible

**Error:** `Error: Python version must be >=3.10 and <3.13`

**Solution:**

- Install Python 3.10, 3.11, or 3.12
- Use `python3.10`, `python3.11`, or `python3.12` explicitly if you have multiple versions

#### Issue: UV not found after installation

**Error:** `command not found: uv`

**Solution:**

```bash
# Add UV to PATH
export PATH="$HOME/.cargo/bin:$PATH"  # Linux/macOS

# Or restart your terminal
```

#### Issue: Ollama connection refused

**Error:** `Connection refused to http://localhost:11434`

**Solution:**

```bash
# Start Ollama service
ollama serve

# Or check if it's already running
pgrep -x ollama  # Linux/macOS
tasklist | findstr ollama  # Windows
```

#### Issue: Model not found

**Error:** `Model 'qwen2.5' not found`

**Solution:**

```bash
# Pull the model
ollama pull qwen2.5
```

#### Issue: Import errors for dependencies

**Error:** `ModuleNotFoundError: No module named 'crewai'`

**Solution:**

```bash
# First, make sure virtual environment is activated
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Then reinstall dependencies
uv pip install -e .

# Or use pip
pip install -e .
```

**Common Cause:** The virtual environment is not activated. Always activate `.venv` before running commands.

#### Issue: Permission denied on Linux/macOS

**Error:** `Permission denied: ./setup.sh`

**Solution:**

```bash
# Make the script executable
chmod +x setup.sh

# Then run it
./setup.sh
```

#### Issue: PowerShell execution policy on Windows

**Error:** `running scripts is disabled on this system`

**Solution:**

```powershell
# Allow script execution for current user
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then run the script
.\setup.ps1
```

### Getting Help

If you encounter issues not covered here:

1. Check the [GitHub Issues](https://github.com/bencan1a/space_hulk_game/issues)
2. Review the [CONTRIBUTING.md](CONTRIBUTING.md) guide
3. Check the [DEBUGGING_GUIDE.md](DEBUGGING_GUIDE.md)
4. Visit the [crewAI documentation](https://docs.crewai.com)
5. Join the [crewAI Discord](https://discord.com/invite/X4JWnZnxPb)

## Development Setup

For contributors and developers, install the development dependencies:

```bash
# Using setup script
./setup.sh --dev  # Linux/macOS
.\setup.ps1 -Dev  # Windows

# Or manually (with venv activated)
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows
uv pip install -e ".[dev]"
```

This installs additional tools:

- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **black**: Code formatter
- **flake8**: Linter
- **mypy**: Type checker

### Development Workflow

```bash
# Ensure virtual environment is activated
source .venv/bin/activate      # Linux/macOS
.venv\Scripts\activate         # Windows

# Format code
black src/ tests/

# Run linter
flake8 src/ tests/

# Run type checker
mypy src/

# Run tests with coverage
pytest --cov=space_hulk_game tests/
```

## Next Steps

After successful installation:

1. Review the [README.md](README.md) for project overview
2. Check the [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines
3. Explore the `docs/` directory for documentation and `project-plans/` for architectural context
4. Run `crewai run` to start the game

---

**Happy coding!** 🎮
