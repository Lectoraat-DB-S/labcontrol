#https://stackoverflow.com/questions/47110728/powershell-download-and-run-exe-file
$FileUri = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-amd64.exe"
$Destination = "C:/temp/pythonInstaller.exe"

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

$exeArgs = '/verysilent /tasks=addcontextmenufiles,addcontextmenufolders,addtopath'

Start-Process -Wait $Destination -ArgumentList $exeArgs
