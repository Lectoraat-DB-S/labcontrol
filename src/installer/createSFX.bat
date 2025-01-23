:: TODO: enhancement to this .bat file
:: download WinPython SFX from projectsite.
::  site: https://sourceforge.net/projects/winpython/files/latest/download OR
:: https://github.com/winpython/winpython/releases/download/11.2.20241228final/Winpython64-3.12.8.0slim.exe
::  use curl?
:: run SFX to extract it in a temperary directory
:: rename the created directory (WPYxx-xxxxx) to labcontrol
:: then proceed with script below.

set targetdir=C:\WPy64-31241\notebooks\labcontrol\
set drivertargetdir=C:\WPy64-31241\VISAdrv\
set driversourcedir=..\..\firmware\
set notebookSourceDir= ..\notebooks
set notebookTargetDir= C:\WPy64-31241\notebooks

xcopy %notebookSourceDir%\getStarted.ipynb %notebookTargetDir%

xcopy  ..\main.py %targetdir%
xcopy  ..\devices\*.py %targetdir% /s

xcopy %driversourcedir%ni-visa_24.8_online.exe  %drivertargetdir%

set currentdirname=C:\WPy64-31241
set renameddirname=labcontrol
set dir2compress=C:\labcontrol
RENAME "%currentdirname%" "%renameddirname%"
del labcontrol.exe
start C:\PROGRA~1\7-Zip\7z.exe a -sfx labcontrol.exe %dir2compress%