#!/bin/bash

###############################################################################
# Space Hulk Game - Setup Script
#
# This script automates the installation of dependencies required to run
# the Space Hulk Game project, including:
# - UV package manager
# - Python dependencies
# - Environment configuration
#
# Optional: Ollama local LLM runtime (use --with-ollama flag)
#
# Usage: ./setup.sh [--with-ollama] [--with-model] [--dev]
#   --with-ollama: Install Ollama (optional, for local LLM)
#   --with-model: Download qwen2.5 model (requires --with-ollama)
#   --dev: Install development dependencies
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Flags
INSTALL_OLLAMA=false
INSTALL_MODEL=false
INSTALL_DEV=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --with-ollama)
            INSTALL_OLLAMA=true
            shift
            ;;
        --with-model)
            INSTALL_MODEL=true
            shift
            ;;
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--with-ollama] [--with-model] [--dev]"
            exit 1
            ;;
    esac
done

# Print colored message
print_message() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Print section header
print_header() {
    echo ""
    print_message "$BLUE" "=================================================="
    print_message "$BLUE" "$1"
    print_message "$BLUE" "=================================================="
}

# Install system dependencies
install_system_dependencies() {
    print_header "Installing System Dependencies"
    local os
    os=$(detect_os)

    if [[ "$os" == "linux" ]]; then
        print_message "$YELLOW" "Detected Linux. Installing 'make' using apt-get..."
        if ! command_exists make; then
            sudo apt-get update
            sudo apt-get install -y make
            print_message "$GREEN" "✓ 'make' installed successfully."
        else
            print_message "$GREEN" "✓ 'make' is already installed."
        fi
    elif [[ "$os" == "macos" ]]; then
        print_message "$YELLOW" "Detected macOS. Checking for Homebrew..."
        if ! command_exists brew; then
            print_message "$RED" "Error: Homebrew is not installed."
            print_message "$YELLOW" "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
        print_message "$GREEN" "✓ Homebrew detected."
        print_message "$YELLOW" "Installing 'make' using Homebrew..."
        if ! command_exists make; then
            brew install make
            print_message "$GREEN" "✓ 'make' installed successfully."
        else
            print_message "$GREEN" "✓ 'make' is already installed."
        fi
    else
        print_message "$YELLOW" "Warning: Unsupported OS detected. Please install 'make' manually."
    fi
}

# Install Node.js and npm
install_nodejs() {
    print_header "Installing Node.js and npm"
    if command_exists node && command_exists npm; then
        print_message "$GREEN" "✓ Node.js and npm are already installed."
        return
    fi

    local os
    os=$(detect_os)

    if [[ "$os" == "linux" ]]; then
        print_message "$YELLOW" "Detected Linux. Installing Node.js and npm..."
        # Add NodeSource repository for Node.js 20.x (LTS)
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs
        print_message "$GREEN" "✓ Node.js and npm installed successfully."
    elif [[ "$os" == "macos" ]]; then
        print_message "$YELLOW" "Detected macOS. Installing Node.js using Homebrew..."
        if ! command_exists brew; then
            print_message "$RED" "Error: Homebrew is not installed."
            print_message "$YELLOW" "Please install Homebrew first: https://brew.sh/"
            exit 1
        fi
        brew install node
        print_message "$GREEN" "✓ Node.js and npm installed successfully."
    else
        print_message "$YELLOW" "Warning: Unsupported OS detected. Please install Node.js and npm manually."
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Detect OS
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        echo "macos"
    else
        echo "unknown"
    fi
}

# Check Python version
check_python() {
    print_header "Checking Python Installation"

    if ! command_exists python3; then
        print_message "$RED" "Error: Python 3 is not installed."
        print_message "$YELLOW" "Please install Python 3.10, 3.11, or 3.12 first."
        exit 1
    fi

    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_message "$GREEN" "✓ Python $PYTHON_VERSION detected"

    # Check if version is in supported range
    if python3 -c 'import sys; exit(0 if (3, 10) <= sys.version_info[:2] < (3, 13) else 1)'; then
        print_message "$GREEN" "✓ Python version is compatible (>=3.10, <3.13)"
    else
        print_message "$RED" "Error: Python version must be >=3.10 and <3.13"
        print_message "$YELLOW" "Current version: $PYTHON_VERSION"
        exit 1
    fi
}

# Install UV package manager
install_uv() {
    print_header "Installing UV Package Manager"

    if command_exists uv; then
        print_message "$GREEN" "✓ UV is already installed"
        uv --version
    else
        print_message "$YELLOW" "Installing UV package manager..."
        curl -LsSf https://astral.sh/uv/install.sh | sh

        # Add UV to PATH for current session (check both possible locations)
        if [ -f "$HOME/.local/bin/uv" ]; then
            export PATH="$HOME/.local/bin:$PATH"
        elif [ -f "$HOME/.cargo/bin/uv" ]; then
            export PATH="$HOME/.cargo/bin:$PATH"
        fi

        if command_exists uv; then
            print_message "$GREEN" "✓ UV installed successfully"
            uv --version
        else
            print_message "$RED" "Error: UV installation failed"
            print_message "$YELLOW" "Please install manually from: https://docs.astral.sh/uv/"
            exit 1
        fi
    fi
}

# Install Ollama
install_ollama() {
    if [ "$INSTALL_OLLAMA" = false ]; then
        print_message "$YELLOW" "Skipping Ollama installation (use --with-ollama to install)"
        return
    fi


    print_header "Installing Ollama"

    if command_exists ollama; then
        print_message "$GREEN" "✓ Ollama is already installed"
        ollama --version
    else
        print_message "$YELLOW" "Installing Ollama..."

        OS=$(detect_os)
        if [ "$OS" = "linux" ]; then
            curl -fsSL https://ollama.com/install.sh | sh
        elif [ "$OS" = "macos" ]; then
            print_message "$YELLOW" "For macOS, please install Ollama manually:"
            print_message "$YELLOW" "  1. Download from: https://ollama.com/download"
            print_message "$YELLOW" "  2. Or use: brew install ollama"
            print_message "$YELLOW" ""
            read -p "Have you installed Ollama? (y/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                print_message "$RED" "Please install Ollama and run this script again."
                exit 1
            fi
        else
            print_message "$RED" "Unsupported OS for automatic Ollama installation"
            print_message "$YELLOW" "Please install manually from: https://ollama.com/download"
            exit 1
        fi

        if command_exists ollama; then
            print_message "$GREEN" "✓ Ollama installed successfully"
        else
            print_message "$RED" "Error: Ollama installation failed"
            exit 1
        fi
    fi

    # Start Ollama service if not running
    if ! pgrep -x "ollama" > /dev/null; then
        print_message "$YELLOW" "Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
        print_message "$GREEN" "✓ Ollama service started"
    else
        print_message "$GREEN" "✓ Ollama service is already running"
    fi
}

# Pull Ollama model
pull_model() {
    if [ "$INSTALL_MODEL" = false ]; then
        print_message "$YELLOW" "Skipping model download (use --with-model to download)"
        return
    fi


    print_header "Downloading Qwen2.5 Model"


    if ! command_exists ollama; then
        print_message "$YELLOW" "Ollama not found, skipping model download"
        print_message "$YELLOW" "(use --with-ollama to install)"
        return
    fi

    print_message "$YELLOW" "This may take a while depending on your internet connection..."

    if ollama list | grep -q "qwen2.5"; then
        print_message "$GREEN" "✓ Qwen2.5 model is already available"
    else
        print_message "$YELLOW" "Pulling qwen2.5 model..."
        ollama pull qwen2.5
        print_message "$GREEN" "✓ Qwen2.5 model downloaded successfully"
    fi
}

# Install Python dependencies with virtual environment
install_python_deps() {
    print_header "Installing Python Dependencies with Virtual Environment"

    if [ "$INSTALL_DEV" = true ]; then
        print_message "$YELLOW" "Creating virtual environment and installing with dev dependencies..."
        uv sync --dev --extra web-backend
    else
        print_message "$YELLOW" "Creating virtual environment and installing dependencies..."
        uv sync --extra web-backend
    fi

    print_message "$GREEN" "✓ Virtual environment created at .venv/"
    print_message "$GREEN" "✓ Dependencies installed from lock file"
    print_message "$GREEN" "✓ Web backend dependencies installed"
    print_message "$YELLOW" "📝 Activate the environment with: source .venv/bin/activate"
}

# Install frontend dependencies
install_frontend_deps() {
    print_header "Installing Frontend Dependencies"

    if [ ! -d "frontend" ]; then
        print_message "$YELLOW" "Frontend directory not found, skipping npm install"
        return
    fi

    cd frontend

    if [ ! -f "package.json" ]; then
        print_message "$YELLOW" "package.json not found, skipping npm install"
        cd ..
        return
    fi

    print_message "$YELLOW" "Installing frontend npm packages..."
    npm install

    print_message "$GREEN" "✓ Frontend dependencies installed"
    cd ..
}

# Setup environment file
setup_env() {
    print_header "Setting Up Environment Configuration"

    if [ -f .env ]; then
        print_message "$GREEN" "✓ .env file already exists"
    else
        print_message "$YELLOW" "Creating .env file from template..."
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
        print_message "$GREEN" "✓ .env file created"
        print_message "$YELLOW" "Note: Edit .env file to configure API keys if needed"
    fi
}

# Setup VS Code configuration
setup_vscode() {
    print_header "Setting Up VS Code Configuration"

    mkdir -p .vscode

    if [ -f .vscode/settings.json ]; then
        print_message "$GREEN" "✓ VS Code settings already exist"
    else
        print_message "$YELLOW" "Creating VS Code settings..."
        cat > .vscode/settings.json << 'EOF'
{
    "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
    "python.terminal.activateEnvironment": true,
    "python.terminal.activateEnvInCurrentTerminal": true,
    "python.testing.pytestEnabled": false,
    "python.testing.unittestEnabled": true,
    "python.testing.unittestArgs": [
        "-v",
        "-s",
        "./tests",
        "-p",
        "test_*.py"
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
        print_message "$GREEN" "✓ VS Code settings created"
    fi
}

# Verify installation
verify_installation() {
    print_header "Verifying Installation"

    local all_good=true

    # Check Python
    if command_exists python3; then
        print_message "$GREEN" "✓ Python 3 installed"
    else
        print_message "$RED" "✗ Python 3 not found"
        all_good=false
    fi

    # Check UV
    if command_exists uv; then
        print_message "$GREEN" "✓ UV package manager installed"
    else
        print_message "$RED" "✗ UV not found"
        all_good=false
    fi

    # Check virtual environment
    if [ -d .venv ]; then
        print_message "$GREEN" "✓ Virtual environment created (.venv/)"

        # Test if we can import key packages
        if .venv/bin/python -c "import crewai" 2>/dev/null; then
            print_message "$GREEN" "✓ Python packages installed correctly"
        else
            print_message "$YELLOW" "⚠ Python packages may not be fully installed"
        fi
    else
        print_message "$RED" "✗ Virtual environment not found"
        all_good=false
    fi

    # Check Ollama (if requested)
    if [ "$INSTALL_OLLAMA" = true ]; then
        if command_exists ollama; then
            print_message "$GREEN" "✓ Ollama installed"

            # Check if model is available (if requested)
            if [ "$INSTALL_MODEL" = true ]; then
                if ollama list | grep -q "qwen2.5"; then
                    print_message "$GREEN" "✓ Qwen2.5 model available"
                else
                    print_message "$YELLOW" "⚠ Qwen2.5 model not found"
                fi
            fi
        else
            print_message "$YELLOW" "⚠ Ollama installation failed or not completed"
        fi
    else
        print_message "$GREEN" "✓ Ollama not requested (using cloud LLM services)"
    fi

    # Check .env file
    if [ -f .env ]; then
        print_message "$GREEN" "✓ .env file exists"
    else
        print_message "$YELLOW" "⚠ .env file not found"
    fi

    # Check VS Code settings
    if [ -f .vscode/settings.json ]; then
        print_message "$GREEN" "✓ VS Code settings configured"
    else
        print_message "$YELLOW" "⚠ VS Code settings not found"
    fi

    if [ "$all_good" = true ]; then
        print_message "$GREEN" "✓ All core components verified successfully"
    else
        print_message "$YELLOW" "⚠ Some components are missing"
    fi
}

# Print completion message
print_completion() {
    print_header "Setup Complete!"

    echo ""
    print_message "$GREEN" "The Space Hulk Game environment is ready!"
    echo ""
    print_message "$BLUE" "Next steps:"
    echo "  1. Activate the virtual environment:"
    print_message "$YELLOW" "     source .venv/bin/activate"
    echo ""
    echo "  2. Review and edit .env file if needed"
    echo ""
    echo "  3. Run the game with:"
    echo "     crewai run"
    echo ""
    echo "  4. Run tests with:"
    echo "     python -m unittest discover -s tests"
    echo ""
    print_message "$BLUE" "For more information, see:"
    echo "  - README.md: Project overview and usage"
    echo "  - docs/SETUP.md: Detailed setup documentation"
    echo "  - docs/CONTRIBUTING.md: Development guidelines"
    echo ""
    print_message "$YELLOW" "💡 Tip: If using VS Code, reload the window to pick up the Python interpreter"
    echo ""
}

# Main execution
main() {
    print_header "Space Hulk Game - Setup Script"
    print_message "$YELLOW" "This script will install all required dependencies"
    echo ""

    install_system_dependencies
    install_nodejs
    check_python
    install_uv
    install_ollama
    pull_model
    install_python_deps
    install_frontend_deps
    setup_env
    setup_vscode
    verify_installation
    print_completion
}

# Run main function
main
