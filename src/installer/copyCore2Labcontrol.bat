
set targetdir=C:\labcontrol
set notebookSourceDir= ..\notebooks
set notebookTargetDir= C:\labcontrol\notebooks\

: first delete the old stuff.
del /S /Q %notebookTargetDir%

xcopy %notebookSourceDir%\getStarted.ipynb %notebookTargetDir%
xcopy %notebookSourceDir%\helloWorld.ipynb %notebookTargetDir%
xcopy %notebookSourceDir%\LabcontrolsComp.ipynb %notebookTargetDir%
xcopy %notebookSourceDir%\bjtCurveMeter.ipynb %notebookTargetDir%
xcopy %notebookSourceDir%\images\meting_HFE.png %notebookTargetDir%\images
xcopy %notebookSourceDir%\images\HFE_meetschema_compleet.png %notebookTargetDir%\images

xcopy %notebookSourceDir%\image.png %notebookTargetDir%

xcopy  ..\labcontrol.py %notebookTargetDir%
xcopy  ..\devices\*.py %notebookTargetDir%\devices\ /s
xcopy  ..\examples\*.py %notebookTargetDir%\examples\ /s
xcopy  ..\tests\*.py %notebookTargetDir%\tests\ /s
