@echo off
REM LabControl Installation Script for Windows

echo ========================================
echo   LabControl Installation
echo ========================================

REM Check if we're in the right directory
if not exist "src\requirements.txt" (
    echo Error: Run this script from the labcontrol root directory
    exit /b 1
)

REM Create virtual environment
echo.
echo [1/3] Creating virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install requirements
echo.
echo [2/3] Installing dependencies...
pip install -r src\requirements.txt

REM Install Hantek6022API from submodule
echo.
echo [3/3] Installing Hantek6022 driver...
pip install -e src\devices\Hantek6022API

echo.
echo ========================================
echo   Installation complete!
echo ========================================
echo.
echo To start LabControl:
echo   venv\Scripts\activate.bat
echo   cd src ^&^& python launch_gui.py   # GUI
echo   cd src ^&^& python launch_tui.py   # TUI
echo.
