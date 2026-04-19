# Labcontrol interactive shell launcher (Windows PowerShell)
# Activates venv, prints banner, leaves you in PowerShell with venv active.

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -LiteralPath $ScriptDir

$activate = Join-Path $ScriptDir "venv\Scripts\Activate.ps1"
if (-not (Test-Path -LiteralPath $activate)) {
    Write-Host "venv not found at $activate" -ForegroundColor Red
    Write-Host 'Run: python -m venv venv; venv\Scripts\Activate.ps1; pip install -e ".[dev]"'
    exit 1
}

. $activate

python -c "from labcontrol.banner import print_banner; print_banner()"
Write-Host ""
