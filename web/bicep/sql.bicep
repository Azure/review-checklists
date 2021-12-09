
@description('Server Name for Azure database for MySQL')
param serverName string

@description('MySQL server administrator login name')
@minLength(1)
param administratorLogin string

@description('MySQL server administrator password')
@minLength(8)
@secure()
param administratorLoginPassword string

@description('Location for all resources.')
param location string = resourceGroup().location

var skuName = 'B_Gen5_1'
var skuFamily = 'Gen5'
var skuCapacity = 1
var skuTier = 'Basic'
var skuSizeMB = 5120
var mySqlVersion = '5.7'
var backupRetentionDays = 7
var geoRedundantBackup = 'Disabled'
var sslEnforcement = 'Disabled'
var firewallrules = [
  {
    Name: 'permitAll'
    StartIpAddress: '0.0.0.0'
    EndIpAddress: '255.255.255.255'
  }
]

resource serverName_resource 'Microsoft.DBforMySQL/servers@2017-12-01' = {
  name: serverName
  location: location
  sku: {
    name: skuName
    tier: skuTier
    capacity: skuCapacity
    size: 'skuSizeMB'
    family: skuFamily
  }
  properties: {
    createMode: 'Default'
    version: mySqlVersion
    administratorLogin: administratorLogin
    administratorLoginPassword: administratorLoginPassword
    sslEnforcement: sslEnforcement
    storageProfile: {
      storageMB: skuSizeMB
      backupRetentionDays: backupRetentionDays
      geoRedundantBackup: geoRedundantBackup
    }
  }
}

@batchSize(1)
resource serverName_firewallrules_Name 'Microsoft.DBforMySQL/servers/firewallRules@2017-12-01' = [for item in firewallrules: {
  name: '${serverName}/${item.Name}'
  properties: {
    startIpAddress: item.StartIpAddress
    endIpAddress: item.EndIpAddress
  }
  dependsOn: [
    serverName_resource
  ]
}]

output mysql_fqdn string = serverName_resource.properties.fullyQualifiedDomainName
