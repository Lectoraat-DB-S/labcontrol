Write-Host 'Clonen van de Labcontrol repository vanaf Github.';
cd c:\Labcontrol\notebooks
$cloneCommand = "git clone https://github.com/Lectoraat-DB-S/labcontrol.git"
#$process = Start-Process PowerShell -ArgumentList "-file c:\Labcontrol\gitclone.ps1" -PassThru #dit lijkt te werken.
Invoke-Expression $cloneCommand

Write-Output "clonen labcontrol repository voltooid"

#Write-Host 'Copiëren van R&S VISA installer naar c:\temp.\n';
#VISA R&S (C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz\RS_VISA_Setup_Win_7_2_5.7z uitpakken naar c:\temp

Write-Host 'Uitpakken van R&S VISA installer met behulp van 7-zip.';
cd C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz
C:\PROGRA~1\7-Zip\7z e .\RS_VISA_Setup_Win_7_2_5.7z
#VISA installer opstarten en install VISA
Write-Host 'Starten van R&S VISA installer.';

C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz\RS_VISA_Setup_Win_7_2_5.exe 
Write-Host 'R&S VISA instal voltooid';

#copy van alle benodigde python scripts vanuit de clone + requirements.txt
#Keuze 1.eventueel python in labcontrol opstarten en requirements installeren, als dat dezelfde omgeving is als de notebook
#Keuze 2. opstarten van jupyternotebook in labcontrol + openen van de juiste pagina die alle requirements.txt installeert.