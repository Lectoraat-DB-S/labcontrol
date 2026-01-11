@echo off
ECHO !!!!!!!!!!!!!!!!!!WELKOM BIJ DE LABCONTROL INSTALLER!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
ECHO DIT BATCH BESTAND VOERT DE VOLGENDE TAKEN UIT:
ECHO 1. DOWNLOAD SELF EXTRACTOR WINPYTHON NAAR DE MAP C:\LABTEMP.
ECHO 2. STARTEN VAN DE SELF EXTRACTOR. WINPYTHON WORDT IN EEN C:\WPy64-XXXX MAP GEZET.
ECHO 3. DOWNLOADEN VAN JUPYTER NOTEBOOK VOOR AFRONDEN INSTALLATIE.
ECHO NA EINDIGEN INSTALLER, MOET U ZELF JUPYTER NOTEBOOK OPSTARTEN. 
ECHO DUBBELKLIK DAARVOOR OP DE JUISTE .EXE FILE IN DE WINPYTHON INSTALL MAP.
ECHO EN OPEN  install.ipynb IN DE JUPYTER NOTEBOOK OMGEVING. 
ECHO VOER ALLE CODEBLOKKEN VAN DIT NOTEBOOK VAN BOVEN NAAR BENEDEN, IN VOLGORDE, UIT.
ECHO !!!!!!!!!!!!!!!!!!!!!VEEL PLEZIER MET LABCONTROL!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! 
pause
::mkdir C:\WPy64-313110
:: download installer winpython
mkdir c:\labtemp
start /wait Powershell.exe -ExecutionPolicy ByPass Start-BitsTransfer https://github.com/winpython/winpython/releases/download/17.2.20251214/WinPython64-3.13.11.0slimb4.exe c:\labtemp
::extract it
ECHO WINPYTHON SELFEXTRACTOR WORDT GESTART. EVEN GEDULD AUB .....
start /wait C:\labtemp\WinPython64-3.13.11.0slimb4.exe -y -oc:\
::start /wait C:\temp\WinPython64-3.13.11.0slimb4.exe -y -oc:\ | ECHO > nul
ECHO INSTALL.IPYNB DOWNLOADEN
start /wait Powershell.exe Start-BitsTransfer https://raw.githubusercontent.com/Lectoraat-DB-S/labcontrol/refs/heads/main/src/notebooks/install.ipynb C:\WPy64-313110\notebooks
ECHO INSTALL.BAT VOLTOOID
ECHO DRUK EEN TOETS OM INSTALL.BAT AF TE SLUITEN.
pause