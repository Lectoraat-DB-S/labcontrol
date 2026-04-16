
set targetdir=C:\github\ElabControl
set notebookSourceDir= ..\..\notebooks
set notebookTargetDir= C:\github\ElabControl\labcontrol\notebooks\

: first delete the old stuff.
del /S /Q %notebookTargetDir%

xcopy %notebookSourceDir%\getStarted.ipynb %targetdir%
xcopy %notebookSourceDir%\helloWorld.ipynb %targetdir%
xcopy %notebookSourceDir%\LabcontrolsComp.ipynb %targetdir%
xcopy %notebookSourceDir%\bjtCurveMeter.ipynb %targetdir%
xcopy /S %notebookSourceDir%\images\ %targetdir%\images\


xcopy  ..\..\labcontrol.py %targetdir%
xcopy  /S ..\..\devices\*.py %targetdir%\devices\ 

