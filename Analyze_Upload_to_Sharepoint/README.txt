

Problem Statement: Analyze weekly report and Transfer weekly statistics csv and image files to SharePoint  and e-mail to domain groups.

Pre-requisites:
            - SharePoint Online Management PowerShell Module.
            - PowerShell version 5.0
            - MSOIDCLIL.dll installed or copied in the respective folder.
	    - Anaconda installed.
	    - tqdm module installed.

Input: Weekly vulnerability excel file.
Output: Weekly statistics csv and image file  and emailed and upload to sharepoint portal.

Folder Names//:
inputfolder: input file directory.
outputfolder: weeklystatistics image  and csv file before transfer to sharepoint.
codebase: Powershell code to connect and upload files.
manipulate.py: Analyse weekly report.

How to run:
1. Run the Manipulate.py file.
2. Run Connect.CMD and Upload.CMD

For examples:
	python manipulate.py "C:\\taks\\sharepointAutomation\\Upload_to_Sharepoint\\inputfolder\\Tickets 23rd July 2018.xlsx"

	python manipulate.py ./inputfolder/Tickets23rdJuly2018.xlsx

Note*:
	- Make sure Pulse Secure is active. If the scripts are running outside the office.
	- Don't run the script inside the OneDrive.

