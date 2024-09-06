#https://stackoverflow.com/questions/47110728/powershell-download-and-run-exe-file
#https://stackoverflow.com/questions/73814620/how-do-i-get-my-own-powershell-script-to-run-keep-getting-an-error
$FileUri = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe"
$DownloadsLocation = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
$installername = "pythonInstaller.exe"
$Destination = "$($DownloadsLocation)\$($installername)"
Write-Host -NoNewLine 'Press any key to start download of Python installer...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
Write-Host -NoNewLine 'Downloading Python .... ';
$bitsJobObj = Start-BitsTransfer $FileUri -Destination $Destination

switch ($bitsJobObj.JobState) {

    'Transferred' {
        Complete-BitsTransfer -BitsJob $bitsJobObj
        break
    }

    'Error' {
        throw 'Error downloading'
    }
}

$exeArgs = '/passive /quiet /simple AppendPath=1 InstallAllUsers=1'
Write-Host -NoNewLine 'Installing Python .... ';
Start-Process -Wait $Destination -ArgumentList $exeArgs

Write-Host -NoNewLine 'Create and activate python virtual environment to run labcontrol in.';
py -m venv v3
v3\Scripts\activate
Write-Host -NoNewLine 'downloading and installing Python packages.';
py -m pip install --upgrade pip
pip install --upgrade setuptools

pip install wheel

pip install -r requirements.txt 

Write-Host -NoNewLine 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');
