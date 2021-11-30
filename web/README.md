# Prototype for web-based checklist

This is a Minimum Viable Product (MVP) for an architecture for web-based checklist reviews. It consists of the following elements:

- A MySQL database
- An Azure Container Instance that will launch 3 containers:
    - filldb (init container): creates the required database and tables in the MySQL server, and fills in the data imported from the latest checklist
    - fillgraphdb (init container): executes any Azure Resource Graph queries stored in the checklist, and stores the results in the MySQL database
    - flask (main container): a flask-based web frontend that allows inspecting the MysQL checklist table, as well as updating the status and comments of each individual checklist item

The `fillgraphdb` container needs to authenticate to Azure to send the Azure Resource Graph queries. There are two options:

- With a [User-Managed Identity](https://docs.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview#how-can-i-use-managed-identities-for-azure-resources) with read access to the subscription(s). The `identityId` parameter of the ARM template needs to be provided.
- With Service Principal credentials

The [Azure CLI deployment script](./arm/deploy.azcli) shows how to create the user-managed identity and launch the ARM template to create the MySQL server and the Azure Container Instance. If you already have an user identity, you can deploy the ARM template graphically as well using the button below:

[![Deploy to Azure](https://aka.ms/deploytoazurebutton)](https://portal.azure.com/#create/Microsoft.Template/uri/https%3A%2F%2Fraw.githubusercontent.com%2FAzure%2Freview-checklists%2Fweb_jose%2Fweb%2Farm%2Ftemplate.json)

The web interface will be available in the public IP address of the ACI container group, on TCP port 5000.

## Further improvements

Since this is only a prototype, there are some aspects not being addressed for the sake of simplicity:

- No HTTPS (it could be easily achieved with an nginx side car in the ACI container group)
- No authentication (an authentication proxy such as Ambassador could be leveraged for this)
- The network firewall of the MySQL server is fully open (it could be closed down to the ACI egress IP address)
- The UI of the flask container is rather rudimentary, but it shows the basic principles and does live updates to the MySQL database without having to press any "Submit" button
- SSL Enforcement is disabled in the MySQL Server due to `flask-mysql` not using encryption

Contributions highly appreciated!
