$MyChecklistPath = "./checklists/"

$enJson = Get-ChildItem -Path $MyChecklistPath -Filter *.*en.json | Where-Object {$_.name -ne "lz_checklist.en.json"}
$GUIDList = @()
foreach ($file in $enJson) {
    $Json = Get-Content $file.FullName | ConvertFrom-Json
    $Json.items | ForEach-Object {
        $Duplicates = '' | select GUID, File
        $Duplicates.file = $file.name
        $Duplicates.GUID = $_.guid
        $GUIDList += $Duplicates
    }
}
$duplicateGUIDs = $GUIDList | Group-Object -Property GUID | Where-Object { $_.Count -gt 1 }
# Print out the duplicate GUIDs
Write-Host "Duplicate GUIDs found: $($duplicateGUIDs.Count)"
foreach ($guid in $duplicateGUIDs) {
    Write-Host "GUID: $($guid.Group.GUID) - Files: $($guid.Group.file)"
}
