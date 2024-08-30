#https://stackoverflow.com/questions/47110728/powershell-download-and-run-exe-file
$FileUri = "https://update.code.visualstudio.com/latest/win32-x64-user/stable"
$Destination = "C:/temp/vscodeInstaller.exe"

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
