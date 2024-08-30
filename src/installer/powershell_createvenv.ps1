#https://stackoverflow.com/questions/47110728/powershell-download-and-run-exe-file
$FileUri = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
$Destination = "C:/temp/pythonInstaller.exe"
$DownloadsLocation = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
$installername = "pythonInstaller.exe"
$Destination = "$($DownloadsLocation)\$($installername)"

Write-Output $Destination

Write-Host -NoNewLine 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
Write-Host -NoNewLine 'Create and activate python virtual environment to run labcontrol in.';
py -m venv v3
v3\Scripts\activate
Write-Host -NoNewLine 'downloading and installing Python packages.';
py -m pip install --upgrade pip
pip install --upgrade setuptools

pip install wheel

Write-Host -NoNewLine 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
