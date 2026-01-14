@echo off
REM LabControl TUI Launcher for Windows
cd /d "%~dp0"
call venv\Scripts\activate.bat
cd src
python launch_tui.py %*
