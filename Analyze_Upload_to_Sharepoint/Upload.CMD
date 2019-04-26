@echo off
setlocal enabledelayedexpansion
setlocal enableextensions enabledelayedexpansion


set spath=%~dp0
echo %spath%
REM powershell.exe Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy Unrestricted -Force
powershell.exe -File "%spath%\codebase\Upload_Docs_to_sharepoint.ps1"



