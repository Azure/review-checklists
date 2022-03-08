param containerName string //= 'go-app1'
param location string = 'westeurope'
param imageName string = 'erjosito/checklist-filldb:1.0'
param cpuCores int = 1
param memoryInGb int = 1
param checklistTech string
param mysql_fqdn string
@description('MySQL server administrator login name')
@minLength(1)
param administratorLogin string

@description('MySQL server administrator password')
@minLength(8)
@secure()
param administratorLoginPassword string

resource containerGroup 'Microsoft.ContainerInstance/containerGroups@2019-12-01' = {
  name: containerName
  location: location
  properties: {
    containers: [
      {
        name: containerName
        properties: {
          environmentVariables: [
            {
              name: 'CHECKLIST_TECHNOLOGY'
              value: checklistTech 
            }
            {
              name: 'MYSQL_USER'
              value: administratorLogin 
            }
            {
              name: 'MYSQL_PASSWORD'
              secureValue: administratorLoginPassword 
            }
            {
              name: 'MYSQL_FQDN'
              value: mysql_fqdn 
            }

          ]
          image: imageName
          resources: {
            requests: {
              cpu: cpuCores
              memoryInGB: memoryInGb
            }
          }
        }
      }
    ]
    restartPolicy: 'OnFailure'
    osType: 'Linux'
  }
}
