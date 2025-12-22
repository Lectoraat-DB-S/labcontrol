#Om een powershell script te openen als administrator, zie: https://learn.microsoft.com/nl-nl/archive/blogs/virtual_pc_guy/a-self-elevating-powershell-script
#Andere manier om iets te starten als administrator staat hier:  https://topwizprogramming.com/freecode_runandwait.html (gevonden 
# via: https://community.appeon.com/qna/q-a/open-administrator-command-prompt-from-script)
#Maar je kan ook een administrator shell starten via autoexec.bat, zie: https://superuser.com/questions/1110448/how-to-run-batch-file-command-with-elevated-permissions
#uit deze laatste link komt onderstaand commando:
#powershell -command "Start-Process cmd -ArgumentList '/c cd /d %CD% && elevated.bat' -Verb runas"
#https://7-zip.opensource.jp/chm/cmdline/switches/index.htm
#https://web.mit.edu/outland/arch/i386_rhel4/build/p7zip-current/DOCS/MANUAL/commands/index.htm
#https://7-zip.opensource.jp/chm/cmdline/syntax.htm
#silently install: sfx.exe -y -gm2 -InstallPath="C:\\your\\target\\path"
#bron voor silently install: https://stackoverflow.com/questions/17687390/how-do-i-silently-install-a-7-zip-self-extracting-archive-to-a-specific-director
# Rename directory in powershell:
#Rename-Item -Path "project.txt" -NewName "D:\archive\old-project.txt"
#bron voor powershell app starten ± https://github.com/jonmchan/windows-app-cmdline-launcher

#Start-Process PowerShell -Verb runAs -ArgumentList "-file c:\Labcontrol\gitclone.ps1" # dit werkt: het start een powershell die een gitclone doet.

#Deze is ook interessant, via onderstaande link een Powershell script om bestanden van een sharepoint af te halen:
#https://github.com/tuxramos/PowerShell/blob/main/downloadSharepointFolder.ps1

$WelcomeMsg = "Welkom bij de Labcontrol Powershell installer.

Deze installer doorloopt de volgende stappen:
1. Aanmaken van c:\temp. Dit is een tijdelijke werkmap waarin bestanden van Internet kunnen worden gedownload en 
    worden  uitgepakt.
2. Controleren of de computer voorzien is van git. Als dit niet het geval is wordt git-scm gedownload & geïnstalleerd.
3. Controle van de aanwezigheid van 7-Zip. Indien niet aanwezig, zal dit pakket, na download, geïnstalleerd worden.
4. Downloaden en installeren van WinPython. Nadat WinPython installatie, hernoemt deze installer de 
    WinPython map naar c:\Labcontrol.
Wat wilt u doen?"

$OptiesStringWithOffline = "1: Eerst c:\temp verwijderen. Dan alleen benodigde installers downloaden naar c:\temp, niets installeren.
2: Alleen missende installers downloaden. Er wordt niets geïnstalleerd.
3: Offline installeren. Vereist het vooraf gedownload hebben van alle installers.
4: Clean install. Eerst alles verwijderen, dan downloaden en installeren (vereist netwerkverbinding)
Ongeldige keuze = exit Powershell installer."

$OptiesStringNoOffline = "1: Eerst c:\temp verwijderen. Dan alleen benodigde installers downloaden naar c:\temp, niets installeren.
2: Alleen missende installers downloaden. Er wordt niets geïnstalleerd.
3: Clean install. Eerst alles verwijderen, dan downloaden en installeren (vereist netwerkverbinding)
Ongeldige keuze = exit Powershell installer."


$WinPython_url = "https://github.com/winpython/winpython/releases/download/17.2.20251012/WinPython64-3.13.8.0slimb1.exe" 
$dest = "c:\temp"
$git_scm_url = "https://github.com/git-for-windows/git/releases/download/v2.51.0.windows.2/Git-2.51.0.2-64-bit.exe"
$sevenZip_dwl_url = "https://www.7-zip.org/a/7z2501-x64.exe"

$installGit = 0 # standaard aanname dat git al aanwezig is op systeem
$install7Zip = 0
$gitDownloaded = 0
$7ZipDownloaded = 0
$WinPythonDownloaded = 0
$NoInstall = 0
$KeepTempContents = 0
$OffLineInstall = 0
$forceDownload = 0

$WinPyTargetPath = "c:\Labcontrol"
$WinPyTargetPathExists = Test-Path -Path $WinPyTargetPath 

$TempExists = Test-Path -Path $dest
$GitExePath = "Git-2.51.0.2-64-bit.exe"


$GitInstallAvPath = Join-Path -Path $dest -ChildPath $GitExePath
$GitInstallAvPathExists = Test-Path -Path $GitInstallAvPath

$7ZipExePath = "7z2501-x64.exe"
$7ZipInstallAvPath = Join-Path -Path $dest -ChildPath $7ZipExePath
$7ZipInstallAvPathExists = Test-Path -Path $7ZipInstallAvPath

$WinPyExePath = "WinPython64-3.13.8.0slimb1.exe"
$WinPyInstallAvPath = Join-Path -Path $dest -ChildPath $WinPyExePath
$WinPyInstallAvPathExists = Test-Path -Path $WinPyInstallAvPath

#Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
#Get-ExecutionPolicy -List

Function dump2ScrnAndFile {
	Param ( [string]$tekst2dump)
	$tekst2dump | Tee-Object -Append -FilePath "C:\temp\labcontrollog.txt"
}
Function progExists {
	Param( [string]$ProgName)
	$appList = winget list
	# vind een string in een string:
	$result = $appList | Select-String -Pattern $ProgName -SimpleMatch
	if ($result) {
		Write-Host $ProgName ' staat al op uw systeem';
		return 1 # bij de download sectie moet git NIET meegenomen worden.
	}
	else {
		Write-Host $ProgName ' staat niet op uw systeem.'
		return 0 # bij de download sectie moet git meegenomen worden.
	}
}

Function deleteDir {
	Param([string]$dirName)
	Write-Host 'Verwijderen van alle bestanden in: ' $dirName;
	Remove-Item $dirName"\*.*"
	Write-Host 'Verwijderen van map: ' $dirName;
	Remove-Item $dirName
}

Function deleteFilesDir {
	Param([string]$dirName)
	Write-Host 'Verwijderen van alle bestanden in: ' $dirName;
	Remove-Item $dirName"\*.*"
}

Function downloadProg {
	Param( [string]$ProgName, [string]$SourceUrl, [string]$dest )
	Write-Host 'Start Downloading ' $ProgName;
	# Download Winpython
	try { 
		Start-BitsTransfer -Source $SourceUrl -Destination $dest 
		return 1 #download gelukt
	}
	catch {
		Write-Host "An error occurred:"
		Write-Host $_
		return 0 #download mislukt.
	}
}
#print een welkom.
Write-Host $WelcomeMsg
if ($WinPyInstallAvPathExists -and $7ZipInstallAvPathExists -and $GitInstallAvPathExists) {
	Write-Host $OptiesStringWithOffline;
	
}
else {
	Write-Host $OptiesStringNoOffline
}

$keuze = Read-Host "Maak uw keuze"
switch ($keuze) {
	1 { "1: Temp dir deleten. Alles opnieuw downloaden. No install."; $NoInstall = 1; $forceDownload = 1; $KeepTempContents = 0 }
	2 { "2: Alleen download indien nodig. No install."; $NoInstall = 1; $KeepTempContents = 1 }
	3 {
		"3: Offline installeren. Voorwaarde: alle benodigde installers aanwezig."; 
		$OffLineInstall = 1; 
		$KeepTempContents = 1;
		$NoInstall = 0;
	}
	4 { "4: Clean install. Not implemented yet. Bye!"; return }
	default { "Ongeldige keuze. Verlaat installer. Bye Bye!"; return }
}


Write-Host "Controleren of c:\labcontrol al bestaat of niet"
# if the target folder of Labcontrol already exists, delete it to install a fresh version.
if ($WinPyTargetPathExists) {
	Write-Host "C:\Labcontrol bestaat al. Probeer nu om te verwijderen"
	deleteDir $WinPyTargetPath
	Write-Host "C:\Labcontrol verwijderd."

}

Write-Host "Controle of C:\temp bestaat. Indien niet wordt deze aangemaakt."

#New-Item -Path $WinPyTargetPath -Type Directory 
if ($TempExists) {
	if (!$KeepTempContents) {
		Write-Host "Doelmap c:\temp bestaat al! Probeer nu alle bestanden in c:\temp te verwijderen."
		deleteFilesDir $dest
		$GitInstallAvPathExists = 0
		$7ZipInstallAvPathExists = 0
		$WinPyInstallAvPathExists = 0
		#New-Item -Path $dest -Type Directory

	}
	elseif ($KeepTempContents -and $OffLineInstall) {
		if ($GitInstallAvPathExists -and $7ZipInstallAvPathExists -and
			$WinPyInstallAvPathExists) {
			Write-Host "Alle installers aanwezig. Start Offline installatie." 
			$OffLineInstall = 1
		}
		else {
			Write-Host "Offline installatie onmogelijk. Niet alle installers aanwezig."
			Write-Host "Labcontrol installer stopt nu."
			return;	
		}
	}
}
else {
	# c:\temp bestaat niet dus KeepTempContents kan niet.
	$KeepTempContents = 0
	Write-Host "Doelmap c:\temp bestaat niet. Probeer doelmap nu aan te maken."
	New-Item -Path $dest -Type Directory
	Write-Host "Doelmap c:\temp aangemaakt"
}

dump2ScrnAndFile "Probeer nu te detecteren of git al op uw computer staat."
#controle of git al op deze computer staat:
$installGit = !(progExists "git")

dump2ScrnAndFile "Probeer nu te dectecteren of 7-zip al op uw computer staat."
#controleer of 7z of 7-zip op de computer staan.
$install7Zip = !(progExists "7-Zip")


if (!$OffLineInstall) {
	####### DOWNLOAD SECTIE #######

	#Git downloaden
	if ($forceDownload -or ($installGit -and !$GitInstallAvPathExists)) {
		dump2ScrnAndFile "Probeer nu git-scm te downloaden naar c:\temp."
		$gitDownloaded = downloadProg -ProgName "git-scm" -SourceUrl $git_scm_url -dest $dest
		dump2ScrnAndFile "Git-scm is gedownload. Installatie wordt straks uitgevoerd."
	}

	#downloaden van 7zip
	if ($forceDownload -or !$7ZipInstallAvPathExists) {
		dump2ScrnAndFile "Probeer nu 7-zip te downloaden naar c:\temp."
		$7ZipDownloaded = downloadProg -ProgName "7-zip" -SourceUrl $sevenZip_dwl_url -dest $dest
		dump2ScrnAndFile "7-ZIP is gedownload. Installatie wordt straks uitgevoerd."
	}

	#downloaden van winpyton
	if ($forceDownload -or !$WinPyInstallAvPathExists) {
		dump2ScrnAndFile "Probeer nu WinPython installer te downloaden naar c:\temp."
		$WinPythonDownloaded = downloadProg -ProgName "WinPython" -SourceUrl $WinPython_url -dest $dest
		dump2ScrnAndFile "WinPyton installer is gedownload. Installer wordt straks uitgevoerd."
	}
}
if ($NoInstall) {
	dump2ScrnAndFile "Only Download selected. Quit now...."
	return -1
}
####### EINDE DOWNLOADSECTIE ##############


##### UITPAKKEN EN INSTALLEREN VAN SOFTWARE ####
if ($installGit -and ($gitDownloaded -or $GitInstallAvPathExists)) {
	dump2ScrnAndFile 'Installatie Git wordt  gestart. A.u.b. toestemming verlenen als daar om gevraagd wordt.\n';
	c:\temp\Git-2.51.0.2-64-bit.exe /SP- /SILENT 	# dit lijkt te werken, de vraag of ik wel wil doorgaan komt wel, ondanks de SP-switch.
	# maar ik krijg geen vraag waar ik de boel wil hebben
}

if ($install7Zip -and ($7ZipDownloaded -OR $7ZipInstallAvPathExists)) {
	dump2ScrnAndFile 'Installatie 7zip wordt gestart. Kies voor de default instelling en verleen toestemming als daar om gevraagd wordt.\n';
	cmd /c c:\temp\7z2501-x64.exe /S
}

# uitpakken van winpython
if ($WinPythonDownloaded -OR $WinPyInstallAvPathExists) {
	dump2ScrnAndFile 'Installatie WinPython wordt gestart. Kies voor de default instelling en verleen toestemming indien daar om gevraagd wordt.\n';
	#c:\temp\WinPython64-3.13.8.0slimb1.exe  e -o "c:\" -y #dit werkt, let op: de e switch betekent extractie in huidige dir!!
	# Start een powershell; process waarop de rest kan wachten
	# Onderstaande argumenten pakken winpython uit naar c:\WPy64-31380
	$process = Start-Process -FilePath "c:\temp\WinPython64-3.13.8.0slimb1.exe" -ArgumentList "x -oc:\ -y" -PassThru
	#opmerking: het lijkt erop of WinPython extractor niet kijkt naar de outputswitch.

	# Do something in between
	dump2ScrnAndFile "Process $($process.Id) is running."

	# Wait untill process is finished
	Wait-Process -Id $process.Id
	dump2ScrnAndFile "uitpakken WinPython gedaan"
	
	
	# voor uitpakken op de achtergrond, zonder gui
	#c:\temp\WinPython64-3.13.8.0slimb1.exe -y -gm2 -InstallPath="C:\\temp"
	#als Winpython is uitgepakt, de directory hernoemen naar labcontrol
	#Write-Host 'Hernoemen van installatiemap WinPython naar c:\Labcontrol.';
	#Onderstaande werkt, maar alleen als je niet in temp zelf zit
	Rename-Item -Path "C:\WPy64-31380" -NewName $WinPyTargetPath
}

#clonen van de github Labcontrol repo
dump2ScrnAndFile 'Clonen van de Labcontrol repository vanaf Github.\n';
Set-Location c:\Labcontrol\notebooks
$cloneCommand = "git clone https://github.com/Lectoraat-DB-S/labcontrol.git"
#$process = Start-Process PowerShell -ArgumentList "-file c:\Labcontrol\gitclone.ps1" -PassThru #dit lijkt te werken.
$process = Start-Process PowerShell -Command { Invoke-Command $cloneCommand }
dump2ScrnAndFile "Process $($process.Id) is running."

# Wait untill process is finished
Wait-Process -Id $process.Id
dump2ScrnAndFile "clonen labcontrol repository voltooid"

dump2ScrnAndFile "Copy van R&S visa installer naar temp dir"
#Write-Host 'Copiëren van R&S VISA installer naar c:\temp.\n';
#VISA R&S (C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz\RS_VISA_Setup_Win_7_2_5.7z uitpakken naar c:\temp
Copy-Item "CC:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz\RS_VISA_Setup_Win_7_2_5.7z" -Destination "C:\temp"

dump2ScrnAndFile 'Start uitpakken van R&S VISA installer met behulp van 7-zip.\n';
Set-Location C:\temp
C:\PROGRA~1\7-Zip\7z e .\RS_VISA_Setup_Win_7_2_5.7z
#VISA installer opstarten en install VISA
dump2ScrnAndFile 'Starten van R&S VISA installer.\n';

C:\temp\RS_VISA_Setup_Win_7_2_5.exe 


#copy van alle benodigde python scripts vanuit de clone + requirements.txt
#Keuze 1.eventueel python in labcontrol opstarten en requirements installeren, als dat dezelfde omgeving is als de notebook
#Keuze 2. opstarten van jupyternotebook in labcontrol + openen van de juiste pagina die alle requirements.txt installeert.