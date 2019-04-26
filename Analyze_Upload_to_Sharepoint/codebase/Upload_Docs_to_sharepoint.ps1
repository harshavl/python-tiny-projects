
[string]$Folder = $NULL
[string]$SiteURL = $NULL

$popup = 0;

$p_StorePath = [environment]::GetFolderPath("mydocuments") + "\Credentials"
$user_filename = dir "$p_StorePath\*.username"
$User = get-content -path $user_filename

$configFile = "$PSScriptRoot\config.txt"

if(test-path Filesystem::$configFile)
{



    foreach($line in Get-Content $configFile) 
    {
        if ($line -like "*:\*")

        {
            $Folder = $line;
        }
        elseif ($line -like "http*")
        {
            $SiteURL = $line;
        }
    }
 }
 else

 {

[void][Reflection.Assembly]::LoadWithPartialName('Microsoft.VisualBasic')

$title = 'Upload Folder Path'
$msg   = 'Please enter the Upload Folder Path:        Example - C:\upload'

$Folder = [Microsoft.VisualBasic.Interaction]::InputBox($msg, $title)

$title = 'DXC Sharepoint URL'
$msg   = 'Please enter the DXC Sharepoint URL:        Example - https://dxcportal.sharepoint.com/sites/goc-SS-Test'

$SiteURL = [Microsoft.VisualBasic.Interaction]::InputBox($msg, $title)


$Folder | out-file filesystem::$configFile
$SiteURL | out-file filesystem::$configFile -Append

$popup = 1;
}

If (($Folder -ne $NULL) -and ($SiteURL -ne $NULL))
{
    $DocLibName = "Documents"

    Import-Module "$PSScriptRoot\CredentialManager.psm1"
    #Add references to SharePoint client assemblies and authenticate to Office 365 site - required for CSOM
    Add-Type -Path "C:\Program Files\Common Files\Microsoft Shared\Web Server Extensions\15\ISAPI\Microsoft.SharePoint.Client.dll"
    Add-Type -Path "C:\Program Files\Common Files\Microsoft Shared\Web Server Extensions\15\ISAPI\Microsoft.SharePoint.Client.Runtime.dll"
	

    #Bind to site collection
    $Context = New-Object Microsoft.SharePoint.Client.ClientContext($SiteURL)
    $SecureCred = Get-StoredCredential -Name DXCSharepointOnline
    $Creds = New-Object Microsoft.SharePoint.Client.SharePointOnlineCredentials($SecureCred.UserName,$SecureCred.Password)

    $Context.Credentials = $Creds

    #Retrieve list
    $List = $Context.Web.Lists.GetByTitle($DocLibName)
    $Context.Load($List)
    $Context.ExecuteQuery()

    $Filecount = 0;

    #Upload file
    Foreach ($File in (dir $Folder))
    {

    $FileStream = New-Object IO.FileStream($File.FullName,[System.IO.FileMode]::Open)
    $FileCreationInfo = New-Object Microsoft.SharePoint.Client.FileCreationInformation
    $FileCreationInfo.Overwrite = $true
    $FileCreationInfo.ContentStream = $FileStream
    $FileCreationInfo.URL = $File
    $Upload = $List.RootFolder.Files.Add($FileCreationInfo)
    $Context.Load($Upload)
    $Context.ExecuteQuery()
    $Filecount++;
    }
}

if($popup -eq 1)

{

$wshell = New-Object -ComObject Wscript.Shell
$wshell.Popup("Successfully uploaded $Filecount files",0,"Done",0x0)

}
