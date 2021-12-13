## Update Variables a you need to
$rgName = "flkelly-checklist"
$rgLocation = "westeurope"

## Test to see if Resource Group exists
Write-Host "Checking if $rgname Resource Group Exists" -nonewline 
$test = Get-AzResourceGroup -Name $rgName -Location $rgLocation -ErrorAction SilentlyContinue
if ($null -eq $test) {
    Write-Host -ForegroundColor red " [NO]"
    Write-Host "$rgname Resource Group not found - creating it"
    New-AzResourceGroup -Name $rgName -Location $rgLocation
} else {
    Write-Host -ForegroundColor green " [YES]"
}

$deploymentFile = ".\main.bicep"

try {
    $deploymentName = (($deploymentFile).Substring(2)).Replace("\","-") + "-" +(get-date -Format ddMMyyyy-hhmmss) + "-deployment"
    New-AzResourceGroupDeployment -TemplateFile $deploymentFile -Name $deploymentName -ResourceGroupName $rgName
}
catch {
    write-host "Failure - $_"
}
