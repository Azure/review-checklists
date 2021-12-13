param managedIdentityName string
//param roleDefinitionId string = 'b24988ac-6180-42a0-ab88-20f7382dd24c'
param roleNameGuid string = newGuid()
@allowed([
  'Owner'
  'Contributor'
  'Reader'
])
@description('Built-in role to assign')
param builtInRoleType string = 'Reader'

var role = {
  Owner: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635'
  Contributor: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/b24988ac-6180-42a0-ab88-20f7382dd24c'
  Reader: '/subscriptions/${subscription().subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7'
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2018-11-30' = {
  name: managedIdentityName
  location: resourceGroup().location
}

resource roleassignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  //name: guid(roleDefinitionId, resourceGroup().id)
  name: roleNameGuid
  scope: tenant()
  properties: {
    principalType: 'ServicePrincipal'
    //roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', roleDefinitionId)
    roleDefinitionId: role[builtInRoleType]
    principalId: managedIdentity.properties.principalId
  }
}

output managedIdentityID string = managedIdentity.id
output managedIdentityName string = managedIdentity.name
