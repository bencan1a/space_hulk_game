###############################################################################
# Space Hulk Game - Virtual Environment Activation Helper (PowerShell)
#
# This script provides a convenient way to activate the virtual environment.
# It checks if the virtual environment exists and activates it.
#
# Usage: .\activate.ps1
#        (Note: May require running: Set-ExecutionPolicy -Scope CurrentUser RemoteSigned)
###############################################################################

# Check if .venv exists
if (-not (Test-Path ".venv")) {
    Write-Host "Error: Virtual environment not found at .venv\" -ForegroundColor Red
    Write-Host "Please run .\setup.ps1 first to create the virtual environment." -ForegroundColor Yellow
    exit 1
}

# Check if we're already in a virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "Note: Already in a virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Yellow
    Write-Host "Deactivating current environment first..." -ForegroundColor Yellow
    deactivate
}

# Activate the virtual environment
& ".\.venv\Scripts\Activate.ps1"

# Verify activation
if ($env:VIRTUAL_ENV) {
    Write-Host "✓ Virtual environment activated successfully!" -ForegroundColor Green
    Write-Host "  Location: $env:VIRTUAL_ENV" -ForegroundColor Green
    Write-Host "  Python: $(Get-Command python | Select-Object -ExpandProperty Source)" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can now run:"
    Write-Host "  crewai run              " -ForegroundColor Yellow -NoNewline
    Write-Host "- Run the game"
    Write-Host "  python -m unittest discover " -ForegroundColor Yellow -NoNewline
    Write-Host "- Run tests"
    Write-Host "  deactivate             " -ForegroundColor Yellow -NoNewline
    Write-Host "- Exit the virtual environment"
    Write-Host ""
} else {
    Write-Host "Error: Failed to activate virtual environment" -ForegroundColor Red
    exit 1
}
