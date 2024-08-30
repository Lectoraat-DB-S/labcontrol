#https://stackoverflow.com/questions/47110728/powershell-download-and-run-exe-file
$FileUri = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
$Destination = "C:/temp/pythonInstaller.exe"
$DownloadsLocation = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
$installername = "pythonInstaller.exe"
$Destination = "$($DownloadsLocation)\$($installername)"

Write-Output $Destination

Write-Host -NoNewLine 'Press any key to continue...';
$null = $Host.UI.RawUI.ReadKey('NoEcho,IncludeKeyDown');

#$bitsJobObj = Start-BitsTransfer $FileUri -Destination $Destination

switch ($bitsJobObj.JobState) {

    'Transferred' {
        Complete-BitsTransfer -BitsJob $bitsJobObj
        break
    }

    'Error' {
        throw 'Error downloading'
    }
}

$exeArgs = '/passive /quiet /simple'


#Start-Process -Wait $Destination -ArgumentList $exeArgs
