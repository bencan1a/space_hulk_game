# Space Hulk Game - Windows Setup Script
#
# This script automates the installation of all dependencies required to run
# the Space Hulk Game project on Windows, including:
# - UV package manager
# - Ollama (local LLM runtime)
# - Qwen2.5 model for Ollama
# - Python dependencies
# - Environment configuration
#
# Usage: .\setup.ps1 [-SkipOllama] [-SkipModel] [-Dev]
#   -SkipOllama: Skip Ollama installation
#   -SkipModel: Skip model download
#   -Dev: Install development dependencies

param(
    [switch]$SkipOllama,
    [switch]$SkipModel,
    [switch]$Dev
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Color functions
function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Write-Header {
    param([string]$Message)
    Write-Host ""
    Write-ColorOutput "==================================================" "Blue"
    Write-ColorOutput $Message "Blue"
    Write-ColorOutput "==================================================" "Blue"
}

function Test-CommandExists {
    param([string]$Command)
    $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
}

# Check Python installation
function Test-Python {
    Write-Header "Checking Python Installation"
    
    if (-not (Test-CommandExists "python")) {
        Write-ColorOutput "Error: Python 3 is not installed." "Red"
        Write-ColorOutput "Please install Python 3.10, 3.11, or 3.12 from https://www.python.org/" "Yellow"
        exit 1
    }
    
    $pythonVersion = python --version 2>&1
    Write-ColorOutput "✓ $pythonVersion detected" "Green"
    
    # Check version compatibility
    $versionOutput = python -c "import sys; exit(0 if (3, 10) <= sys.version_info[:2] < (3, 13) else 1)" 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✓ Python version is compatible (>=3.10, <3.13)" "Green"
    } else {
        Write-ColorOutput "Error: Python version must be >=3.10 and <3.13" "Red"
        exit 1
    }
}

# Install UV package manager
function Install-UV {
    Write-Header "Installing UV Package Manager"
    
    if (Test-CommandExists "uv") {
        Write-ColorOutput "✓ UV is already installed" "Green"
        uv --version
    } else {
        Write-ColorOutput "Installing UV package manager..." "Yellow"
        
        # Download and install UV for Windows
        powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
        
        # Refresh environment variables
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (Test-CommandExists "uv") {
            Write-ColorOutput "✓ UV installed successfully" "Green"
            uv --version
        } else {
            Write-ColorOutput "Error: UV installation failed" "Red"
            Write-ColorOutput "Please install manually from: https://docs.astral.sh/uv/" "Yellow"
            Write-ColorOutput "You may need to restart your terminal for UV to be available." "Yellow"
            exit 1
        }
    }
}

# Install Ollama
function Install-Ollama {
    if ($SkipOllama) {
        Write-ColorOutput "Skipping Ollama installation (-SkipOllama flag set)" "Yellow"
        return
    }
    
    Write-Header "Installing Ollama"
    
    if (Test-CommandExists "ollama") {
        Write-ColorOutput "✓ Ollama is already installed" "Green"
        ollama --version
    } else {
        Write-ColorOutput "Ollama needs to be installed manually on Windows." "Yellow"
        Write-ColorOutput "" "White"
        Write-ColorOutput "Please follow these steps:" "Yellow"
        Write-ColorOutput "  1. Visit: https://ollama.com/download/windows" "White"
        Write-ColorOutput "  2. Download and run the installer" "White"
        Write-ColorOutput "  3. Follow the installation wizard" "White"
        Write-ColorOutput "" "White"
        
        $response = Read-Host "Have you installed Ollama? (y/n)"
        if ($response -notmatch "^[Yy]$") {
            Write-ColorOutput "Please install Ollama and run this script again." "Red"
            exit 1
        }
        
        # Refresh environment
        $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
        
        if (-not (Test-CommandExists "ollama")) {
            Write-ColorOutput "Ollama command not found. You may need to restart your terminal." "Yellow"
            Write-ColorOutput "After restarting, run: ollama pull qwen2.5" "Yellow"
        }
    }
}

# Pull Ollama model
function Install-Model {
    if ($SkipModel) {
        Write-ColorOutput "Skipping model download (-SkipModel flag set)" "Yellow"
        return
    }
    
    Write-Header "Downloading Qwen2.5 Model"
    
    if (-not (Test-CommandExists "ollama")) {
        Write-ColorOutput "Ollama not found, skipping model download" "Yellow"
        return
    }
    
    Write-ColorOutput "This may take a while depending on your internet connection..." "Yellow"
    
    $models = ollama list 2>&1
    if ($models -match "qwen2.5") {
        Write-ColorOutput "✓ Qwen2.5 model is already available" "Green"
    } else {
        Write-ColorOutput "Pulling qwen2.5 model..." "Yellow"
        ollama pull qwen2.5
        if ($LASTEXITCODE -eq 0) {
            Write-ColorOutput "✓ Qwen2.5 model downloaded successfully" "Green"
        } else {
            Write-ColorOutput "Error downloading model. Please try manually: ollama pull qwen2.5" "Yellow"
        }
    }
}

# Install Python dependencies
function Install-PythonDeps {
    Write-Header "Installing Python Dependencies"
    
    if ($Dev) {
        Write-ColorOutput "Installing project dependencies (including dev dependencies)..." "Yellow"
        uv pip install -e ".[dev]"
    } else {
        Write-ColorOutput "Installing project dependencies..." "Yellow"
        uv pip install -e .
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-ColorOutput "✓ Python dependencies installed successfully" "Green"
    } else {
        Write-ColorOutput "Error installing dependencies" "Red"
        exit 1
    }
}

# Setup environment file
function Setup-Environment {
    Write-Header "Setting Up Environment Configuration"
    
    if (Test-Path .env) {
        Write-ColorOutput "✓ .env file already exists" "Green"
    } else {
        Write-ColorOutput "Creating .env file from template..." "Yellow"
        
        $envContent = @"
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
"@
        
        Set-Content -Path .env -Value $envContent
        Write-ColorOutput "✓ .env file created" "Green"
        Write-ColorOutput "Note: Edit .env file to configure API keys if needed" "Yellow"
    }
}

# Verify installation
function Test-Installation {
    Write-Header "Verifying Installation"
    
    $allGood = $true
    
    # Check Python
    if (Test-CommandExists "python") {
        Write-ColorOutput "✓ Python installed" "Green"
    } else {
        Write-ColorOutput "✗ Python not found" "Red"
        $allGood = $false
    }
    
    # Check UV
    if (Test-CommandExists "uv") {
        Write-ColorOutput "✓ UV package manager installed" "Green"
    } else {
        Write-ColorOutput "✗ UV not found" "Red"
        $allGood = $false
    }
    
    # Check Ollama (if not skipped)
    if (-not $SkipOllama) {
        if (Test-CommandExists "ollama") {
            Write-ColorOutput "✓ Ollama installed" "Green"
            
            # Check if model is available (if not skipped)
            if (-not $SkipModel) {
                $models = ollama list 2>&1
                if ($models -match "qwen2.5") {
                    Write-ColorOutput "✓ Qwen2.5 model available" "Green"
                } else {
                    Write-ColorOutput "⚠ Qwen2.5 model not found" "Yellow"
                }
            }
        } else {
            Write-ColorOutput "⚠ Ollama not found (skipped or not installed)" "Yellow"
        }
    }
    
    # Check .env file
    if (Test-Path .env) {
        Write-ColorOutput "✓ .env file exists" "Green"
    } else {
        Write-ColorOutput "⚠ .env file not found" "Yellow"
    }
    
    if ($allGood) {
        Write-ColorOutput "✓ All core components verified successfully" "Green"
    } else {
        Write-ColorOutput "⚠ Some components are missing" "Yellow"
    }
}

# Print completion message
function Show-Completion {
    Write-Header "Setup Complete!"
    
    Write-Host ""
    Write-ColorOutput "The Space Hulk Game environment is ready!" "Green"
    Write-Host ""
    Write-ColorOutput "Next steps:" "Blue"
    Write-Host "  1. Review and edit .env file if needed"
    Write-Host "  2. Run the game with: crewai run"
    Write-Host "  3. Run tests with: python -m unittest discover -s tests"
    Write-Host ""
    Write-ColorOutput "For more information, see:" "Blue"
    Write-Host "  - README.md: Project overview and usage"
    Write-Host "  - SETUP.md: Detailed setup documentation"
    Write-Host "  - CONTRIBUTING.md: Development guidelines"
    Write-Host ""
}

# Main execution
function Main {
    Write-Header "Space Hulk Game - Windows Setup Script"
    Write-ColorOutput "This script will install all required dependencies" "Yellow"
    Write-Host ""
    
    Test-Python
    Install-UV
    Install-Ollama
    Install-Model
    Install-PythonDeps
    Setup-Environment
    Test-Installation
    Show-Completion
}

# Run main function
try {
    Main
} catch {
    Write-ColorOutput "An error occurred during setup: $_" "Red"
    exit 1
}
