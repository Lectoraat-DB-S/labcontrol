@echo off
REM LabControl Windows Start Menu Installer
REM Creates Start Menu shortcuts for LabControl GUI and TUI

echo ========================================
echo   LabControl Start Menu Installer
echo ========================================

set "SCRIPT_DIR=%~dp0"
set "STARTMENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs\LabControl"

REM Create LabControl folder in Start Menu
if not exist "%STARTMENU%" mkdir "%STARTMENU%"

REM Create shortcuts using PowerShell
echo.
echo Creating Start Menu shortcuts...

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU%\LabControl GUI.lnk'); $s.TargetPath = '%SCRIPT_DIR%labcontrol-gui.bat'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'LabControl GUI - Lab Equipment Control'; $s.Save()"

powershell -Command "$ws = New-Object -ComObject WScript.Shell; $s = $ws.CreateShortcut('%STARTMENU%\LabControl TUI.lnk'); $s.TargetPath = 'cmd.exe'; $s.Arguments = '/k \"%SCRIPT_DIR%labcontrol-tui.bat\"'; $s.WorkingDirectory = '%SCRIPT_DIR%'; $s.Description = 'LabControl TUI - Terminal Interface'; $s.Save()"

echo.
echo ========================================
echo   Installation complete!
echo ========================================
echo.
echo Shortcuts created in Start Menu:
echo   - LabControl GUI
echo   - LabControl TUI
echo.
echo You can find them by searching "LabControl" in the Start Menu.
echo.
pause
