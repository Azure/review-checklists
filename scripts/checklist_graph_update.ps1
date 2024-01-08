#################################################################################
#
# The current process before this script was:
# 1. Run checklist_graph.sh
# 2. Merge the resulting JSON into the Excel file with checklist_graph_update.ps1
#    This latest step needs to be performed in a Windows computer with the xlwings
#      Python module installed.
# This PowerShell script performs both steps in one go.
# 
# Last updated: January 2023
#
#################################################################################

# Take the Excel file as parameter
param (
  [string]$ExcelFilePath
)

# Variables
$SheetName = "Checklist"
$ChecklistNameRow = 6
$ChecklistNameCol = 1
$StartRow = 10
$TextCol = 6
$GraphCol = 14
$CommentCol = 10

# Verify that the Excel file path exists
if (-not (Test-Path $ExcelFilePath))
{
    Write-Host "ERROR: The Excel spreadsheet file path does not exist: $ExcelFilePath"
    exit
}
else
{
    Write-Host "DEBUG: Excel spreadsheet file found: $ExcelFilePath"
}

# Set variables
$Excel = New-Object -Com Excel.Application
$Excel.EnableEvents = $false        # So that the Workbook macros are not run
$Workbook = $Excel.Workbooks.Open($ExcelFilePath, $null, $false)
$Workbook.RefreshAll();
$Sheet = $Workbook.Sheets.Item($SheetName)

Write-Host "DEBUG: Processing spreadsheet with name $($Sheet.Cells.Item($ChecklistNameRow, $ChecklistNameCol).Value2)..."

# Go over the column in the Excel file containing the checklists
$Row = $StartRow
While ($($Sheet.Cells($Row, $TextCol).Value2).Length -gt 0)
{
    if ($($Sheet.Cells($Row, $GraphCol).Value2).Length -gt 0) {
        $GraphQuery = $Sheet.Cells($Row, $GraphCol).Value2
        Write-Host "DEBUG: Processing graph query: '$GraphQuery'..."
        # $Sheet.Cells($Row, $CommentCol).Value2 = "Test"
    }
    $Row += 1
}

# Close the Excel file
# $Workbook.Save()
$Workbook.Close($true)
$Excel.Quit()