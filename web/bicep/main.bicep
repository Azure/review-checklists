@description('Options available for the checklist')
@allowed([
  'lz'
  'aks'
  'avd'
  'security'
])
param checklistTech string = 'lz'
@description('Server Name for Azure database for MySQL')
param serverName string = 'sql${uniqueString(resourceGroup().id)}'
@description('MySQL server administrator login name')
@minLength(1)
param administratorLogin string
@description('MySQL server administrator password')
@minLength(8)
@secure()
param administratorLoginPassword string
param managedIdentityName string = 'mi${uniqueString(resourceGroup().id)}'
param filldbGrphContainerName string = 'filldbgraph${uniqueString(resourceGroup().id)}'
param filldbContainerName string = 'filldb${uniqueString(resourceGroup().id)}'
param flaskContainerName string = 'flask${uniqueString(resourceGroup().id)}'
//param resourceGroupName string = resourceGroup().name
//param subscriptionId string

//var fullManagedIdentityID = '/subscriptions/${subscriptionId}/resourceGroups/${resourceGroupName}/providers/Microsoft.ManagedIdentity/userAssignedIdentities/${managedIdentityName}'


module mi 'mi.bicep' = {
  name: 'deploy-managedIdentity'
  params: {
    managedIdentityName: managedIdentityName
  }
}

module sql 'sql.bicep' = {
  name: 'deploy-sql'
  params: {
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    serverName: serverName
  }
}

module filldbContainer 'filldb.bicep' = {
  name: 'deploy-filldb'
  params: {
    mysql_fqdn: sql.outputs.mysql_fqdn
    containerName: filldbContainerName
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    checklistTech: checklistTech
  }
}

module filldbGraphContainer 'filldbgraph.bicep' = {
  name: 'deploy-filldbgraph'
  params: {
    mysql_fqdn: sql.outputs.mysql_fqdn
    containerName: filldbGrphContainerName
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    fullManagedIdentityID: mi.outputs.managedIdentityID
  }
}

module flask 'flask.bicep' = {
  name: 'deploy-flask'
  params: {
    mysql_fqdn: sql.outputs.mysql_fqdn
    containerName: flaskContainerName
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
  }
}

output miID string = mi.outputs.managedIdentityID
