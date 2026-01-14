@echo off
REM LabControl GUI Launcher for Windows
cd /d "%~dp0"
call venv\Scripts\activate.bat
cd src
python launch_gui.py %*
