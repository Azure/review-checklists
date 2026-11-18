# Azure Review Checklists

This directory contains Azure review checklists for various Azure services and technologies. These checklists help architects and engineers review Azure implementations against best practices and the [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/).

## What's in this directory

This directory contains:

- **English checklist files** (`*.en.json`): The master versions of all checklists (50+ services)
- **Localized checklist files** (`*.es.json`, `*.ja.json`, `*.ko.json`, `*.pt.json`, `*.zh-Hant.json`): Automatically translated versions
- **Master checklist** (`checklist.en.master.json`): Consolidated checklist containing all individual checklists
- **Template file** (`template.json`): Template for creating new checklists
- **Schema file** (`checklist.schema.json`): JSON schema that defines the checklist structure

### File naming convention

All checklist files follow this naming pattern:
- **English (master)**: `<service>_checklist.en.json` (e.g., `aks_checklist.en.json`)
- **Localized**: `<service>_checklist.<language>.json` (e.g., `aks_checklist.es.json`)

### Available checklists

The repository includes **50+ checklists** for Azure services and scenarios:

**Infrastructure & Compute**
- AKS (Azure Kubernetes Service), ARO (Azure Red Hat OpenShift), Container Apps
- App Service, Azure Functions, Azure Spring Apps
- AVD (Azure Virtual Desktop), Virtual Machines
- AVS (Azure VMware Solution)

**Data & Analytics**
- Azure SQL Database, MySQL, PostgreSQL, CosmosDB
- Azure Synapse, Databricks, Stream Analytics
- Azure Data Factory, Data Explorer (ADX)

**Networking**
- Azure Front Door, Application Gateway, Azure Firewall
- Application Delivery Networking, ExpressRoute
- DNS

**Security & Identity**
- Key Vault, Azure Arc
- Security, Identity, Data Security

**Management & Governance**
- Azure Landing Zone (ALZ), AI Landing Zone
- Cost Optimization, Multitenancy
- Azure DevOps

**Storage & Backup**
- Azure Storage, Blob Storage, Azure Files
- Recovery Services Vault

**Integration & IoT**
- API Management, Service Bus, Event Hubs
- Logic Apps, IoT Hub, Device Provisioning Service
- Azure Bot Service

**AI & Machine Learning**
- Azure Machine Learning, Azure OpenAI

**Other Services**
- Azure Container Registry (ACR), Redis Cache
- Azure Purview, Stack HCI (HCI), SAP

For the complete list with owners and status, see the [main README](../README.md#checklists).

### Checklist maturity states

- **GA** (Generally Available): Battle-tested, production-ready, actively maintained
- **Preview**: New checklists undergoing review and testing
- **Deprecated**: Older checklists being phased out

## How to create a new checklist

### Prerequisites

1. Fork this repository
2. Create a new branch for your checklist
3. Ensure you have a unique service identifier

### Step-by-step guide

1. **Copy the template**:
   ```bash
   cp template.json <service>_checklist.en.json
   ```
   Replace `<service>` with your service identifier (e.g., `cosmosdb`, `functions`, `servicebus`)

2. **Update the metadata**:
   ```json
   "metadata": {
       "name": "Azure <Service Name> Review",
       "state": "Preview",
       "waf": "all",
       "timestamp": "December 01, 2024"
   }
   ```

3. **Add your recommendations**:
   Each recommendation item should include:
   ```json
   {
       "category": "Security",
       "subcategory": "Identity and Access",
       "text": "Enable Azure AD integration",
       "description": "Detailed description of the recommendation (optional)",
       "waf": "Security",
       "guid": "12345678-1234-1234-1234-123456789abc",
       "id": "01.01.01",
       "service": "YourService",
       "severity": "High",
       "link": "https://learn.microsoft.com/azure/...",
       "training": "https://learn.microsoft.com/training/...",
       "graph": "resources | where type=='microsoft.keyvault/vaults' | extend compliant=properties.enableRbacAuthorization==true | distinct id,compliant"
   }
   ```

   **Key fields explained:**
   - `category`: Main category (e.g., "Security", "Operations")
   - `subcategory`: More specific grouping (e.g., "Identity and Access")
   - `text`: Short, actionable recommendation (required)
   - `description`: Longer explanation (optional)
   - `waf`: Well-Architected Framework pillar (Security, Reliability, Performance, Cost, Operations)
   - `guid`: Globally unique identifier (required, must be unique)
   - `id`: Local ordering ID (e.g., "01.01.01")
   - `service`: Azure service name
   - `severity`: High, Medium, or Low
   - `link`: Documentation URL (required)
   - `training`: Microsoft Learn training URL (optional)
   - `graph`: Azure Resource Graph query to validate compliance (optional but highly recommended)

4. **Generate unique GUIDs**:
   Use a GUID generator like [https://guidgenerator.com/](https://guidgenerator.com/) for each recommendation

5. **Update categories**:
   Add appropriate categories that match your recommendations:
   ```json
   "categories": [
       { "name": "Security" },
       { "name": "Reliability" },
       { "name": "Performance" }
   ]
   ```

6. **Validate your checklist**:
   - Ensure it follows the schema in `checklist.schema.json`
   - Verify all GUIDs are unique across the entire repository
   - Check that all required fields are populated
   - Test any Azure Resource Graph queries you've added
   - Follow checklist item best practices:
     - **Actionable**: Use verifiable actions like "Enable X" or "Configure Y" (not "Consider X" or "Be aware of Y")
     - **Verifiable**: Items should be checkable via Azure portal, ARG query, or documentation
     - **Specific**: Be precise (e.g., "Assign at least a /22 network space" not "Plan sufficient network size")

7. **Submit a pull request**:
   - Commit your changes
   - Create a pull request against the main branch
   - Add appropriate reviewers (see [CODEOWNERS](../CODEOWNERS))

### Schema requirements

Your checklist must conform to the JSON schema defined in `checklist.schema.json`. Key requirements:

- **Required sections**: `items`, `categories`, `status`, `severities`, `metadata`
- **Required item properties**: `category`, `text`, `guid`, `id`, `link`, `severity`, `waf`
- **Optional item properties**: `description`, `training`, `graph`, `subcategory`, `service`
- **Unique GUIDs**: All recommendation GUIDs must be globally unique across the entire repository
- **Valid links**: All URLs should be accessible and point to official Microsoft documentation
- **Well-Architected Framework**: Use valid WAF pillars (Security, Reliability, Performance, Cost, Operations)

### Azure Resource Graph queries

Azure Resource Graph (ARG) queries are a powerful way to automatically validate compliance with checklist recommendations. When adding ARG queries:

- Use the `graph` field in your recommendation item
- The query **must** return two fields:
  - `id`: The ARM ID of the resource being evaluated
  - `compliant`: Boolean indicating compliance status (true/false)
- Use single quotes (`'`) inside the query string (double quotes break JSON syntax)
- Use case-insensitive comparison (`=~`) instead of case-sensitive (`==`) when possible

**Example ARG query:**
```json
"graph": "resources | where type=='microsoft.containerservice/managedclusters' | extend compliant=isnotnull(zones) | distinct id,compliant"
```

This query checks if AKS clusters use availability zones. For more details on ARG queries, see [CONTRIBUTING.md - Adding Resource Graph queries](../CONTRIBUTING.md#1-adding-or-modifying-resource-graph-queries).

## How to modify existing checklists

### Option 1: Direct JSON modification

1. **Edit the English version only**: Modify the relevant `*.en.json` file
2. **Don't touch translations**: Never modify non-English versions (they are auto-generated)
3. **Add unique GUIDs**: For new recommendations, generate new GUIDs using [guidgenerator.com](https://guidgenerator.com/)
4. **Follow the schema**: Ensure your changes conform to `checklist.schema.json`
5. **Add ARG queries**: If possible, include Azure Resource Graph queries for automated validation
6. **Follow best practices**: Make recommendations actionable, verifiable, and specific (see [CONTRIBUTING.md](../CONTRIBUTING.md#what-to-contribute))
7. **Submit a pull request**: PRs are reviewed by checklist owners (see [CODEOWNERS](../CODEOWNERS))

### Option 2: Using the Excel spreadsheet

1. Download the [Excel spreadsheet](../spreadsheet/review_checklist.xlsm)
2. Load your checklist and make changes
3. Export to JSON using the "Export checklist to JSON" button
4. Replace the relevant `.en.json` file with your exported JSON
5. Submit a pull request

## Localization

**Important**: This repository uses automated translation via [Azure Translator](https://azure.microsoft.com/services/cognitive-services/translator/).

- ✅ **DO**: Modify English versions (`*.en.json`) only
- ❌ **DON'T**: Modify translated versions (`*.es.json`, `*.ja.json`, `*.ko.json`, `*.pt.json`, `*.zh-Hant.json`)
- **Why**: Translations are automatically regenerated and will overwrite manual changes
- **Supported languages**: Spanish (es), Japanese (ja), Korean (ko), Portuguese (pt), Traditional Chinese (zh-Hant)

If you need to add a new language, you'll need to update the GitHub Actions workflows and Azure Translator configuration (see [CONTRIBUTING.md - Forking the Repository](../CONTRIBUTING.md#forking-the-repository)).

## Related directories

### Service Guide checklists (`checklists-ext/`)

The `checklists-ext` directory contains additional checklists that follow different patterns:

- **Service Guide checklists** (`*_sg_checklist.en.json`): Specialized checklists sourced from Azure Service Guides
  - Examples: Azure Kubernetes Service, Azure Front Door, Azure OpenAI, Virtual Machines, etc.
- **APRL checklist** (`aprl_checklist.en.json`): Azure Proactive Resiliency Library checklist
- **Full WAF checklist** (`fullwaf_checklist.en.json`): Comprehensive Well-Architected Framework checklist
- **The AKS checklist** (`theaks_checklist.en.json`): Alternative AKS checklist version

These checklists are also automatically translated and follow the same localization patterns as the main checklists.

## Getting help

### Documentation and guidelines

- 📋 **General contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
- 🏗️ **Checklist creation**: Detailed steps in [CONTRIBUTING.md - Adding a new Checklist](../CONTRIBUTING.md#4-adding-a-new-checklist)
- 📊 **Excel usage**: See [spreadsheet/README.md](../spreadsheet/README.md) for the macro-enabled Excel frontend
- 🔍 **Azure Resource Graph**: See [scripts/README.md](../scripts/README.md) for ARG query tools
- 📈 **Azure Monitor Workbooks**: See [workbooks/README.md](../workbooks/README.md) for automated workbook generation
- 📏 **Code owners**: Check [CODEOWNERS](../CODEOWNERS) for checklist-specific reviewers

### Using the checklists

There are three main ways to use these checklists:

1. **Excel spreadsheet**: Download the macro-enabled [Excel workbook](../spreadsheet/review_checklist.xlsm) for an interactive experience
2. **Web application**: Use the hosted web app at [https://aka.ms/ftaaas](https://aka.ms/ftaaas)
3. **Azure Resource Graph**: Run ARG queries directly against your Azure resources (see [scripts/README.md](../scripts/README.md))

### Support channels

- 🐛 **Report bugs**: [Create a bug report](https://github.com/Azure/review-checklists/issues/new?template=03--bug-report.yml)
- 💡 **Request features**: [Create a feature request](https://github.com/Azure/review-checklists/issues/new?template=02--feature-request.yml)
- 📝 **Content issues**: [Create a content request](https://github.com/Azure/review-checklists/issues/new?template=01--content-request.yml)
- 📚 **Documentation**: [Create a documentation issue](https://github.com/Azure/review-checklists/issues/new?template=04--documentation-issue.yml)

### Community guidelines

- Follow the [Code of Conduct](../CODE_OF_CONDUCT.md)
- Review the [Security Policy](../SECURITY.md)
- Check existing issues before creating new ones
- Provide clear descriptions and examples when reporting issues

## Quality assurance

All contributions are automatically validated through GitHub Actions workflows:

- **JSON validation**: Syntax checking and schema compliance
- **GUID uniqueness**: Ensures no duplicate recommendation IDs across all checklists
- **Link checking**: Validates that URLs are accessible
- **Translation**: Automatic generation of localized versions for all supported languages
- **Workbook generation**: Automatic creation of Azure Monitor Workbooks from ARG queries

For questions about validation failures, check the [GitHub Actions logs](../.github/workflows/) or create an issue.

## Additional resources

- **Main repository README**: [README.md](../README.md) - Overview and checklist status table
- **Contributing guide**: [CONTRIBUTING.md](../CONTRIBUTING.md) - Comprehensive contribution guidelines
- **Code of Conduct**: [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md)
- **Security Policy**: [SECURITY.md](../SECURITY.md)
- **Support**: [SUPPORT.md](../SUPPORT.md)