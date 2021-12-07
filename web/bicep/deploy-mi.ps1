$rgName = "flkelly-checklist"
$rgLocation = "westeurope"

New-AzResourceGroup -Name $rgName -Location $rgLocation

$deploymentFile = ".\main.bicep"
$deploymentName = (($deploymentFile).Substring(2)).Replace("\","-") + "-" +(get-date -Format ddMMyyyy-hhmmss) + "-deployment"
New-AzResourceGroupDeployment -TemplateFile $deploymentFile -Name $deploymentName -ResourceGroupName $rgName
