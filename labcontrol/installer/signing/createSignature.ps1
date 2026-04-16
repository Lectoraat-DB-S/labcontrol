$cert = New-SelfSignedCertificate -Subject "mysetup.exe" -CertStoreLocation "cert:\LocalMachine\My" -type CodeSigning

$pwd = ConvertTo-SecureString -String "220172" -Force -AsPlainText

Export-PfxCertificate -cert $cert -FilePath myowncertje.pfx -Password $pwd

$env:path += ";C:\Program Files (x86)\Windows Kits\10\bin\10.0.26100.0\x64"

signtool.exe sign /t http://timestamp.digicert.com /fd SHA256 /f myowncertje.pfx /p 220172 mysetup.exe