#https://7-zip.opensource.jp/chm/cmdline/switches/index.htm
#https://web.mit.edu/outland/arch/i386_rhel4/build/p7zip-current/DOCS/MANUAL/commands/index.htm
#https://7-zip.opensource.jp/chm/cmdline/syntax.htm
#silently install: sfx.exe -y -gm2 -InstallPath="C:\\your\\target\\path"
#bron voor silently install: https://stackoverflow.com/questions/17687390/how-do-i-silently-install-a-7-zip-self-extracting-archive-to-a-specific-director
# Rename directory in powershell:
#Rename-Item -Path "project.txt" -NewName "D:\archive\old-project.txt"
#bron voor powershell app starten ± https://github.com/jonmchan/windows-app-cmdline-launcher

#Start-Process PowerShell -Verb runAs -ArgumentList "-file c:\Labcontrol\gitclone.ps1" # dit werkt: het start een powershell die een gitclone doet.

# URL and Destination
#$url = "https://sourceforge.net/projects/winpython/files/latest/download/Winpython64-3.12.4.1.exe"
$url = "https://github.com/winpython/winpython/releases/download/17.2.20251012/WinPython64-3.13.8.0slimb1.exe" 
$dest = "c:\temp"
$git_scm_url = "https://github.com/git-for-windows/git/releases/download/v2.51.0.windows.2/Git-2.51.0.2-64-bit.exe"
$git_scm_dest = "Downloads"
$sevenZip_dwl_url = "https://www.7-zip.org/a/7z2501-x64.exe"
$downloadOnly = 1

Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine
Get-ExecutionPolicy -List

if (Test-Path -Path $dest) {
	Write-Host "Doelmap c:\temp bestaat al! Probeer nu alle bestanden in c:\temp te verwijderen."
	Remove-Item C:\temp\*.*
}
else {
	Write-Host "Doelmap c:\temp bestaat niet. Probeer doelmap nu aan te maken."
	New-Item -Path $dest -Type Directory
}


#controle of git al op deze computer staat:
$appList = winget list
# vind een string in een string:
$result = $appList | Select-String -Pattern 'git' -SimpleMatch
if ($result) {
	Write-Host 'Git staat al op uw systeem';
}
else {
	Write-Host 'Git staat niet op uw systeem. Er wordt gepoogd Git te downloaden & te installeren.\n';
	Write-Host 'Eerst wodt git-scm gedownload......\n';
	#download git-scm
	Start-BitsTransfer -Source $git_scm_url  -Destination $dest
	Write-Host 'Git-scm is gedownload, installatie wordt nu gestart. A.u.b. toestemming verlenen als daar om gevraagd wordt.\n';
	
	#install git-scm
	#Start-Process -FilePath "c:\temp\Git-2.51.0.2-64-bit.exe"
	#bovenstaande start de installer op, maar dan moet je wel als user toestemming geven, daar heb ik niet zo veel zin in.
	# het kan ook sitlently, maar dan via chocolately.
	#choco install git -params '"/GitOnlyOnPath"'
	# maar je kunt de commandline opties ook zien via: c:\temp\Git-2.51.0.2-64-bit.exe /?, dat levert volgende instructie op:
	if (!$downloadOnly) {
		c:\temp\Git-2.51.0.2-64-bit.exe /SP- /SILENT #dit lijkt te werken, de vraag of ik wel wil doorgaan komt wel, ondanks de SP-switch.
		# ik krijg geen vraag waar ik de boel wil hebben
	}
}

#controleer of 7z of 7-zip op de computer staan.
$result = $appList | Select-String -Pattern '7-Zip' -SimpleMatch
if ($result) {
	Write-Host '7-Zip staat al op uw systeem';
}
else {
	Write-Host '7-Zip staat niet op uw systeem. Probeer te installeren';
	#downloaden van 7zip
	Write-Host "Dowloaden en (stil) installeren van 7-zip."
	Start-BitsTransfer -Source $sevenZip_dwl_url -Destination $dest
	#...en installeren
	if (!$downloadOnly) {
		cmd /c .\7z2501-x64.exe /S
	}
}


Write-Host 'Downloading & installing WinPython.';
# Download Winpython
Start-BitsTransfer -Source $url -Destination $dest 
# uitpakken van winpython
if (!$downloadOnly) {
	c:\temp\WinPython64-3.13.8.0slimb1.exe  e -o "c:\temp" -y #dit werkt
	# voor uitpakken op de achtergrond, zonder gui
	#c:\temp\WinPython64-3.13.8.0slimb1.exe -y -gm2 -InstallPath="C:\\temp"

	#als Winpython is uitgepakt, de directory hernoemen naar labcontrol
	Rename-Item -Path "C:\WPy64-31241" -NewName "C:\Labcontrol" #dit werkt
	#Opstarten van Winpython command line + aanroepen van git clone labcontrol
}
cd c:\Labcontrol\notebooks	

Start-Process PowerShell -ArgumentList "-file c:\Labcontrol\gitclone.ps1" #dit lijkt te werken.

#VISA R&S (C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz\RS_VISA_Setup_Win_7_2_5.7z uitpakken naar c:\temp
cd C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz
C:\PROGRA~1\7-Zip\7z e .\RS_VISA_Setup_Win_7_2_5.7z
#VISA installer opstarten en install VISA
if (!$downloadOnly) {
	C:\Labcontrol\notebooks\labcontrol\firmware\RhodeSchwartz\RS_VISA_Setup_Win_7_2_5.exe /S
}
#VISA installatiebestand deleten


#copy van alle benodigde python scripts vanuit de clone + requirements.txt
#Keuze 1.eventueel python in labcontrol opstarten en requirements installeren, als dat dezelfde omgeving is als de notebook
#Keuze 2. opstarten van jupyternotebook in labcontrol + openen van de juiste pagina die alle requirements.txt installeert.