# Unattended Install of Visual Studio Code

$channel = 'stable'
$platform = 'win32-x64-user' 
$SourceURL = "https://code.visualstudio.com/sha/download?build=stable&os=win32-x64";
$Installer = $env:TEMP + "\vscode.exe"; 
Invoke-WebRequest $SourceURL -OutFile $Installer;
Start-Process -FilePath $Installer -Args "/verysilent /tasks=addcontextmenufiles,addcontextmenufolders,addtopath" -Wait; 
Remove-Item $Installer;
Stop-Process -Name Explorer