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

$WinPyTargetPath = "c:\Labcontrol"
$GitExePath = "Git-2.51.0.2-64-bit.exe"


$GitInstallAvPath = Join-Path -Path $dest -ChildPath $GitExePath
$GitInstallAvPathExists = Test-Path -Path $GitInstallAvPath

$7ZipExePath = "7z2501-x64.exe"
$7ZipInstallAvPath = Join-Path -Path $dest -ChildPath $7ZipExePath
$7ZipInstallAvPathExists = Test-Path -Path $7ZipInstallAvPath

$WinPyExePath = "WinPython64-3.13.8.0slimb1.exe"
$WinPyInstallAvPath = Join-Path -Path $dest -ChildPath $WinPyExePath
$WinPyInstallAvPathExists = Test-Path -Path $WinPyInstallAvPath

$skipDownload = 0

Function dump2ScrnAndFile {
	Param ( [string]$tekst2dump)
	$tekst2dump | Tee-Object -Append -FilePath "C:\temp\labcontrollog.txt"
}

Function deleteDir {
	Param([string]$dirName)
	dump2ScrnAndFile 'Verwijderen van alle bestanden in: ' $dirName;
	Remove-Item $dirName"\*.*"
	dump2ScrnAndFile 'Verwijderen van map: ' $dirName;
	Remove-Item $dirName
}


Function readFromInput {
	$inputCommand = Read-Host
	return $inputCommand
}
Function deleteAllFiles {
	Param ( [string]$path2DeleteFiles)
	Remove-Item * $path2DeleteFiles
}
Function progExists {
	Param( [string]$ProgName)
	$appList = winget list
	# vind een string in een string:
	$result = $appList | Select-String -Pattern $ProgName -SimpleMatch
	if ($result) {
		dump2ScrnAndFile "$ProgName  staat al op uw systeem";
		return 1 
	}
	else {
		dump2ScrnAndFile "$ProgName staat niet op uw systeem.";
		return 0 
	}
}
Function downloadProg {
	Param( [string]$ProgName, [string]$SourceUrl, [string]$dest )
	dump2ScrnAndFile "Start Downloading  $ProgName";
	# Download Winpython
	try { 
		Start-BitsTransfer -Source $SourceUrl -Destination $dest 
		return 1 #download gelukt
	}
	catch {
		dump2ScrnAndFile "Fout tijdens downloaden van $ProgName"
		dump2ScrnAndFile $_
		return 0 #download mislukt.
	}
}

Function folderExists {
	Param( [string]$folderPath)
	dump2ScrnAndFile "Controleren aanwezigheid map: $($folderPath)"
	$result = Test-Path -Path $folderPath
	# if the target folder of Labcontrol already exists, delete it to install a fresh version.
	if ($result) {
		dump2ScrnAndFile "$($folderPath) bestaat al."
		return 1
	}
	else {
		dump2ScrnAndFile "$($folderPath) bestaat niet."
		return 0	
	}
}
Function removeDir {
	Param( [string]$folderPath)
	dump2ScrnAndFile 'Verwijderen van alle bestanden in: ' $folderPath;
	Remove-Item -Recurse $folderPath"\*.*"
	dump2ScrnAndFile 'Verwijderen van map: ' $folderPath;
	Remove-Item -Recurse $folderPath
	dump2ScrnAndFile  "$($folderPath) verwijderd."
}

Function createDir {
	Param( [string]$dirPath)
	New-Item -Path $dirPath -Type Directory
	dump2ScrnAndFile  "$($dirPath) aangemaakt."
}
Function allInstallersAvailable {
	if ($GitInstallAvPathExists -and $7ZipInstallAvPathExists -and $WinPyInstallAvPathExists) {
		return 1
	}
	else {
		return 0
	}
}

Function prepareTempDir {
	Param( [string]$tempPath, [Int16]$keepFiles)
	if (folderExists $tempPath) {
		if ($keepFiles) {
			if (allInstallersAvailable) {
				dump2ScrnAndFile "Alle installers al beschikbaar. Download onnodig."
				return 1
			}
		}
		dump2ScrnAndFile  "$($tempPath) leeggemaakt."
		deleteAllFiles $tempPath
		return 0
	} 
	else {
		createDir $tempPath
		return 0
	}
}
Function installGitScm {
	dump2ScrnAndFile "Opstarten proces voor installatie van git-scm."
	$process = Start-Process -FilePath "c:\temp\Git-2.51.0.2-64-bit.exe" -ArgumentList "/SP- /SILENT" -PassThru
	#opmerking: het lijkt erop of WinPython extractor niet kijkt naar de outputswitch.

	# Do something in between
	dump2ScrnAndFile "Proces $($process.Id) is gestart."

	# Wait untill process is finished
	Wait-Process -Id $process.Id
	dump2ScrnAndFile "Proces $($process.Id) is voltooid."
	dump2ScrnAndFile "installatie git afgerond."
}
Function install7Zip {
	dump2ScrnAndFile "Opstarten proces voor installatie van 7zip."
	#cmd /c c:\temp\7z2501-x64.exe /S
	$process = Start-Process -FilePath "c:\temp\7z2501-x64.exe" -ArgumentList "/S" -PassThru
	#opmerking: het lijkt erop of WinPython extractor niet kijkt naar de outputswitch.

	# Do something in between
	dump2ScrnAndFile "Proces $($process.Id) is gestart."

	# Wait untill process is finished
	Wait-Process -Id $process.Id
	dump2ScrnAndFile "Proces $($process.Id) is voltooid."
	dump2ScrnAndFile "installatie 7zip afgerond."
}
Function installWinPyton {
	dump2ScrnAndFile "Opstarten uitpakken WinPython via  proces met id $($process.Id)."
	$process = Start-Process -FilePath "c:\temp\WinPython64-3.13.8.0slimb1.exe" -ArgumentList "x -oc:\ -y" -PassThru
	#opmerking: het lijkt erop of WinPython extractor niet kijkt naar de outputswitch.

	# Do something in between
	dump2ScrnAndFile "Proces $($process.Id) is gestart."

	# Wait untill process is finished
	Wait-Process -Id $process.Id
	dump2ScrnAndFile "Proces $($process.Id) is voltooid."
	dump2ScrnAndFile "uitpakken WinPython afgerond."
}

Function runAllInstallers {
	Param( [string]$runGitInstall, [string]$run7Zipinstall)
	if ($runGitInstall) {
		installGitScm
	}
	if ($run7Zipinstall) {
		install7Zip
	}
	installWinPyton
}

Function cloneRepo {
	#clonen van de github Labcontrol repo
	dump2ScrnAndFile 'Starten van klonen van de Labcontrol repository (Github).\n';
	Set-Location c:\Labcontrol\notebooks
	$cloneCommand = "git clone https://github.com/Lectoraat-DB-S/labcontrol.git"
	#$process = Start-Process PowerShell -ArgumentList "-file c:\Labcontrol\gitclone.ps1" -PassThru #dit lijkt te werken.
	$process = Start-Process PowerShell -Command { Invoke-Command $cloneCommand }
	dump2ScrnAndFile "Kloonrocess met id: $($process.Id) loopt."

	# Wait untill process is finished
	Wait-Process -Id $process.Id
	dump2ScrnAndFile "Kloonproces voltooid. Labcontrol scripts staan in c:\Labcontrol\notebooks"
	#TODO: op deze manier wordt het pad naar de scripts te lang. Moet een keer worden aangepast.
}

Function installRSVISA {
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

}

Function doInstall {
	# Als c:\labcontrol dir bestaat, verwijder deze directory.
	# Het verwijderen van c:\labcontrol is nodig, want na afloop WinPython installatie, wordt de installatiemap
	# hernoemd naar c:\labcontrol.  
	if (folderExists $WinPyTargetPath) {
		removeDir $WinPyTargetPath
	}
	
	#controleer aanwezigheid van git en 7-zip.
	$installGit = !(progExists "git")
	$install7Zip = !(progExists "7-Zip")
	#controleer of c:\temp bestaat, zo ja: controleer of alle installers al in c:\temp staan -> $skipDownload = 1
	#Wanneer c:\temp niet bestaat, wordt c:\temp aangemaakt.
	$skipDownload = prepareTempDir
	if ($skipDownload) {
		#blijkbaar zijn alle installers aanwezig=> installeren maar.
		#runAllInstallers voert installatie uit. De twee meegegeven parameters bepalen uitvoering van installers
		#van git-scm of 7-Zip. De installer van WinPython wordt altijd uitgevoerd.
		runAllInstallers $installGit $install7Zip
		Rename-Item -Path "C:\WPy64-31380" -NewName $WinPyTargetPath
	}
	else {
		#blijkbaar zijn er geen installers aanwezig => download van de benodigde installer
		deleteAllFiles $dest # alle bestanden verwijderen, zodat er geen conflicten kunnen ontstaan.
		$gitDownloaded = downloadProg -ProgName "git-scm" -SourceUrl $git_scm_url -dest $dest
		$7ZipDownloaded = downloadProg -ProgName "7-zip" -SourceUrl $sevenZip_dwl_url -dest $dest
		$WinPythonDownloaded = downloadProg -ProgName "WinPython" -SourceUrl $WinPython_url -dest $dest

		if ($gitDownloaded -and $7ZipDownloaded -and $WinPythonDownloaded) {
			runAllInstallers 1 1
			Rename-Item -Path "C:\WPy64-31380" -NewName $WinPyTargetPath
		}
		else {
			#probleem. stoppen
			dump2ScrnAndFile "ERROR: download installers mislukt => exit!"
			return -1
		}
	}

	# Winpyhton, git en 7-zip staan op doelcomputer.
	# Kopieren van labcontrol python scripts door klonen van de repo.
	cloneRepo
	# Labcontrol heeft VISA nodig voor de instrument drivers
	installRSVISA
}

doInstall

#$runIt = 1
#$commando = readFromInput
#while ($runIt) {
#	switch ($commando) {
#		0 { dump2ScrnAndFile "nul gekozen" }
#		Default { dump2ScrnAndFile "onbekende optie"; $runIt = 0 }
#	}
#	
#}
