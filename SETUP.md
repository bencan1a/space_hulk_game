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
```

### Windows

```powershell
# Clone the repository
git clone https://github.com/bencan1a/space_hulk_game.git
cd space_hulk_game

# Run the automated setup script
.\setup.ps1
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

- **Ollama** (for local LLM support)
  - Linux/macOS: Installed automatically by setup script
  - Windows: Download from [ollama.com/download/windows](https://ollama.com/download/windows)

## Automated Setup

The automated setup scripts handle all dependency installation and configuration.

### Linux/macOS Setup Script

The `setup.sh` script provides the following options:

```bash
# Standard installation
./setup.sh

# Skip Ollama installation (if you'll use OpenAI API instead)
./setup.sh --skip-ollama

# Skip model download (download later manually)
./setup.sh --skip-model

# Install development dependencies
./setup.sh --dev

# Combine flags
./setup.sh --skip-ollama --dev
```

**What the script does:**

1. ✓ Checks Python version compatibility
2. ✓ Installs UV package manager
3. ✓ Installs Ollama (optional)
4. ✓ Downloads qwen2.5 model (optional)
5. ✓ Installs Python dependencies
6. ✓ Creates `.env` configuration file
7. ✓ Verifies installation

### Windows Setup Script

The `setup.ps1` script provides the following options:

```powershell
# Standard installation
.\setup.ps1

# Skip Ollama installation
.\setup.ps1 -SkipOllama

# Skip model download
.\setup.ps1 -SkipModel

# Install development dependencies
.\setup.ps1 -Dev

# Combine flags
.\setup.ps1 -SkipOllama -Dev
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

### 4. Install Python Dependencies

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

### 5. Create Environment Configuration

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

**Option 1: Use Ollama (Local, Free)**

```bash
OLLAMA_BASE_URL=http://localhost:11434
OPENAI_MODEL_NAME=ollama/qwen2.5
```

**Option 2: Use OpenAI API**

```bash
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_MODEL_NAME=gpt-4
```

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

### 1. Check Python Environment

```bash
# Check Python version
python --version  # or python3 --version

# Should output: Python 3.10.x, 3.11.x, or 3.12.x
```

### 2. Check UV Installation

```bash
uv --version
```

### 3. Check Ollama Installation (if applicable)

```bash
# Check if Ollama is installed
ollama --version

# Check if Ollama service is running
ollama list

# Should show qwen2.5 model if downloaded
```

### 4. Verify Python Dependencies

```bash
# Check if crewai is installed
python -c "import crewai; print(crewai.__version__)"

# Check if other dependencies are installed
python -c "import mem0; import yaml; import litellm; print('All dependencies OK')"
```

### 5. Run Tests

```bash
# Run the test suite
python -m unittest discover -s tests -v

# All tests should pass
```

### 6. Run the Application

```bash
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
# Reinstall dependencies
uv pip install -e .

# Or use pip
pip install -e .
```

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

# Or manually
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
3. Explore the `memory-bank/` directory for project documentation
4. Run `crewai run` to start the game

---

**Happy coding!** 🎮
