#!/bin/bash

# Space Hulk Game Development Container Setup Script
# This script runs after the devcontainer is created to set up the development environment

set -e

echo "🚀 Setting up Space Hulk Game development environment..."

# Update system packages
echo "📦 Updating system packages..."
sudo apt-get update
sudo apt-get install -y \
    curl \
    wget \
    git \
    jq \
    tree \
    htop \
    vim \
    nano

# Install Python dependencies using uv
echo "🐍 Installing Python dependencies with uv..."
if command -v uv &> /dev/null; then
    echo "✅ uv is already installed"
else
    echo "📦 Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Install project dependencies
echo "📚 Installing project dependencies..."
uv sync --dev

# Install pre-commit hooks (if available)
if [ -f ".pre-commit-config.yaml" ]; then
    echo "🪝 Installing pre-commit hooks..."
    uv run pre-commit install
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p tmp
mkdir -p logs
mkdir -p .vscode

# Set up environment variables
echo "🔧 Setting up environment variables..."
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "⚠️  Please update .env with your specific configuration"
    fi
fi

# Install Ollama (if not running externally)
echo "🤖 Setting up Ollama configuration..."
# Note: In devcontainer, we'll connect to host Ollama instance
# The OLLAMA_HOST environment variable is set in devcontainer.json

# Test Python environment
echo "🧪 Testing Python environment..."
uv run python --version
uv run python -c "import sys; print(f'Python path: {sys.executable}')"

# Test CrewAI installation
echo "🧪 Testing CrewAI installation..."
uv run python -c "import crewai; print(f'CrewAI version: {crewai.__version__}')" || echo "⚠️  CrewAI not yet available"

# Set up VS Code workspace settings
echo "⚙️  Setting up VS Code workspace..."
cat > .vscode/settings.json << EOF
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.testing.pytestEnabled": true,
    "python.testing.unittestEnabled": false,
    "python.testing.pytestArgs": [
        "tests"
    ],
    "files.associations": {
        "*.yaml": "yaml",
        "*.yml": "yaml"
    },
    "yaml.validate": true,
    "yaml.completion": true,
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": "explicit",
        "source.fixAll": "explicit"
    },
    "files.trimTrailingWhitespace": true,
    "files.insertFinalNewline": true
}
EOF

# Set up launch configuration for debugging
echo "🐛 Setting up debug configuration..."
mkdir -p .vscode
cat > .vscode/launch.json << EOF
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Run Space Hulk Game",
            "type": "python",
            "request": "launch",
            "program": "src/space_hulk_game/main.py",
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/src"
            }
        },
        {
            "name": "Run CrewAI",
            "type": "python",
            "request": "launch",
            "module": "crewai.cli.cli",
            "args": ["run"],
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/src"
            }
        },
        {
            "name": "Run Tests",
            "type": "python",
            "request": "launch",
            "module": "pytest",
            "args": ["tests/", "-v"],
            "console": "integratedTerminal",
            "cwd": "\${workspaceFolder}",
            "env": {
                "PYTHONPATH": "\${workspaceFolder}/src"
            }
        }
    ]
}
EOF

# Set up tasks for common operations
echo "⚡ Setting up VS Code tasks..."
mkdir -p .vscode
cat > .vscode/tasks.json << EOF
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Install Dependencies",
            "type": "shell",
            "command": "uv sync --dev",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Run Tests",
            "type": "shell",
            "command": "uv run pytest tests/ -v",
            "group": "test",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Format Code",
            "type": "shell",
            "command": "uv run black src/ tests/",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Lint Code",
            "type": "shell",
            "command": "uv run ruff check --fix src/ tests/",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Type Check",
            "type": "shell",
            "command": "uv run mypy src/",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        },
        {
            "label": "Run CrewAI",
            "type": "shell",
            "command": "uv run crewai run",
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "panel": "new"
            },
            "problemMatcher": []
        }
    ]
}
EOF

echo "✅ Space Hulk Game development environment setup complete!"
echo ""
echo "🎮 Available commands:"
echo "  uv run crewai run          - Run the CrewAI crew"
echo "  uv run pytest tests/ -v   - Run tests"
echo "  uv run black src/          - Format code"
echo "  uv run ruff check src/     - Lint code"
echo "  uv run mypy src/           - Type checking"
echo ""
echo "📚 Documentation:"
echo "  docs/QUICKSTART.md         - Quick start guide"
echo "  docs/AGENTS.md             - Agent documentation"
echo "  docs/SETUP.md              - Setup instructions"
echo ""
echo "🚀 Ready to develop the Space Hulk Game!"
