#!/bin/bash

###############################################################################
# Space Hulk Game - Setup Script
# 
# This script automates the installation of all dependencies required to run
# the Space Hulk Game project, including:
# - UV package manager
# - Ollama (local LLM runtime)
# - Qwen2.5 model for Ollama
# - Python dependencies
# - Environment configuration
#
# Usage: ./setup.sh [--skip-ollama] [--skip-model]
#   --skip-ollama: Skip Ollama installation
#   --skip-model: Skip model download
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
SKIP_OLLAMA=false
SKIP_MODEL=false
INSTALL_DEV=false

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --skip-ollama)
            SKIP_OLLAMA=true
            shift
            ;;
        --skip-model)
            SKIP_MODEL=true
            shift
            ;;
        --dev)
            INSTALL_DEV=true
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Usage: $0 [--skip-ollama] [--skip-model] [--dev]"
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
        
        # Add UV to PATH for current session
        export PATH="$HOME/.cargo/bin:$PATH"
        
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
    if [ "$SKIP_OLLAMA" = true ]; then
        print_message "$YELLOW" "Skipping Ollama installation (--skip-ollama flag set)"
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
    if [ "$SKIP_MODEL" = true ]; then
        print_message "$YELLOW" "Skipping model download (--skip-model flag set)"
        return
    fi
    
    print_header "Downloading Qwen2.5 Model"
    
    if ! command_exists ollama; then
        print_message "$YELLOW" "Ollama not found, skipping model download"
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

# Install Python dependencies
install_python_deps() {
    print_header "Installing Python Dependencies"
    
    if [ "$INSTALL_DEV" = true ]; then
        print_message "$YELLOW" "Installing project dependencies (including dev dependencies)..."
        uv pip install -e ".[dev]"
    else
        print_message "$YELLOW" "Installing project dependencies..."
        uv pip install -e .
    fi
    
    print_message "$GREEN" "✓ Python dependencies installed successfully"
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
    
    # Check Ollama (if not skipped)
    if [ "$SKIP_OLLAMA" = false ]; then
        if command_exists ollama; then
            print_message "$GREEN" "✓ Ollama installed"
            
            # Check if model is available (if not skipped)
            if [ "$SKIP_MODEL" = false ]; then
                if ollama list | grep -q "qwen2.5"; then
                    print_message "$GREEN" "✓ Qwen2.5 model available"
                else
                    print_message "$YELLOW" "⚠ Qwen2.5 model not found"
                fi
            fi
        else
            print_message "$YELLOW" "⚠ Ollama not found (skipped or not installed)"
        fi
    fi
    
    # Check .env file
    if [ -f .env ]; then
        print_message "$GREEN" "✓ .env file exists"
    else
        print_message "$YELLOW" "⚠ .env file not found"
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
    echo "  1. Review and edit .env file if needed"
    echo "  2. Run the game with: crewai run"
    echo "  3. Run tests with: python -m unittest discover -s tests"
    echo ""
    print_message "$BLUE" "For more information, see:"
    echo "  - README.md: Project overview and usage"
    echo "  - SETUP.md: Detailed setup documentation"
    echo "  - CONTRIBUTING.md: Development guidelines"
    echo ""
}

# Main execution
main() {
    print_header "Space Hulk Game - Setup Script"
    print_message "$YELLOW" "This script will install all required dependencies"
    echo ""
    
    check_python
    install_uv
    install_ollama
    pull_model
    install_python_deps
    setup_env
    verify_installation
    print_completion
}

# Run main function
main
