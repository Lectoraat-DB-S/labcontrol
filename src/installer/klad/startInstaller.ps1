Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope LocalMachine

Get-ExecutionPolicy

# result must be RemoteSigned


#.\Start-ActivityTracker.ps1 : File .\Start-ActivityTracker.ps1 cannot be loaded.
#The file .\Start-ActivityTracker.ps1 is not digitally signed.
#The script will not execute on the system.
#For more information, see about_Execution_Policies at https://go.microsoft.com/fwlink/?LinkID=135170.
#At line:1 char:1
#+ .\Start-ActivityTracker.ps1
#+ ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#+ CategoryInfo          : NotSpecified: (:) [], PSSecurityException
#+ FullyQualifiedErrorId : UnauthorizedAccess

Unblock-File -Path .\installerLabcontrol.ps1

Get-ExecutionPolicy

#RemoteSigned

.\installerLabcontrol.ps1