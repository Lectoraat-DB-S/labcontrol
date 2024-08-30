# Unattended Install of python
Set-ExecutionPolicy -Scope CurrentUser
Set-ExecutionPolicy RemoteSigned
$channel = 'stable'
$platform = 'win32-x64-user' 
$SourceURL = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe";
$Installer = $env:TEMP + "\python310.exe"; 
Invoke-WebRequest $SourceURL -OutFile $Installer;
Start-Process -FilePath $Installer -Args "/verysilent /tasks=addcontextmenufiles,addcontextmenufolders,addtopath" -Wait; 
Remove-Item $Installer;
Stop-Process -Name Explorer