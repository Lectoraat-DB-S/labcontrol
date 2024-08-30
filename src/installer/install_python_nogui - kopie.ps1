#https://stackoverflow.com/questions/47110728/powershell-download-and-run-exe-file
$FileUri = "https://www.python.org/ftp/python/3.12.5/python-3.12.5-amd64.exe"
$DownloadsLocation = (New-Object -ComObject Shell.Application).NameSpace('shell:Downloads').Self.Path
$installername = "pythonInstaller.exe"
$Destination = "$($DownloadsLocation)\$($installername)"

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

$exeArgs = '/passive /quiet /simple'

Start-Process -Wait $Destination -ArgumentList $exeArgs
