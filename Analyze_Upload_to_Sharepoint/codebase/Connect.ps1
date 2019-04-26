
write-host $PSScriptRoot
Import-Module "$PSScriptRoot\CredentialManager.psm1"
Get-StoredCredential -Name DXCSharepointOnline

