::remove old stuff
@echo off
del labcontrol.exe
del winpython.exe
del /s /q C:\WPy64-31241
rd C:\WPy64-31241

::download the winpython installer
curl -L https://sourceforge.net/projects/winpython/files/latest/download > winpython.exe
::run the installer
winpython.exe -oc:\ -y

set targetdir=C:\WPy64-31241\notebooks\
set drivertargetdir=C:\WPy64-31241\VISAdrv\
set driversourcedir=..\..\firmware\
set notebookSourceDir= ..\notebooks
set notebookTargetDir= C:\WPy64-31241\notebooks

xcopy %notebookSourceDir%\getStarted.ipynb %notebookTargetDir%

xcopy  ..\labcontrol.py %targetdir%
xcopy  ..\devices\*.py %targetdir%\devices\ /s
xcopy  ..\examples\*.py %targetdir%\examples\ /s
xcopy  ..\tests\*.py %targetdir\tests /s

xcopy %driversourcedir%ni-488.2_25.0_online.exe  %drivertargetdir%

set currentdirname=C:\WPy64-31241
set renameddirname=labcontrol
set dir2compress=C:\labcontrol
RENAME "%currentdirname%" "%renameddirname%"
start C:\PROGRA~1\7-Zip\7z.exe a -sfx labcontrol.exe %dir2compress%