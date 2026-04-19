@echo off
REM Labcontrol launcher (Windows). Double-clickable; keeps PowerShell open.
powershell.exe -NoExit -ExecutionPolicy Bypass -File "%~dp0labcontrol-shell.ps1"
