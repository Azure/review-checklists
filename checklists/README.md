# Azure Review Checklists

This directory contains Azure review checklists for various Azure services and technologies. These checklists help architects and engineers review Azure implementations against best practices and the [Azure Well-Architected Framework](https://docs.microsoft.com/azure/architecture/framework/).

## What's in this directory

This directory contains:

- **English checklist files** (`*.en.json`): The master versions of all checklists
- **Localized checklist files** (`*.es.json`, `*.ja.json`, etc.): Automatically translated versions
- **Template file** (`template.json`): Template for creating new checklists
- **Schema file** (`checklist.schema.json`): JSON schema that defines the checklist structure

### File naming convention

All checklist files follow this naming pattern:
- **English (master)**: `<service>_checklist.en.json` (e.g., `aks_checklist.en.json`)
- **Localized**: `<service>_checklist.<language>.json` (e.g., `aks_checklist.es.json`)

### Available checklists

The repository includes checklists for various Azure services including:
- **AKS** (Azure Kubernetes Service)
- **App Service** (Azure App Service)
- **SQL Database** (Azure SQL Database)
- **Key Vault** (Azure Key Vault)
- **Storage** (Azure Storage)
- **Landing Zone** (Azure Landing Zone)
- And many more...

Each checklist has different maturity states:
- **GA** (Generally Available): Battle-tested and production-ready
- **Preview**: New checklists undergoing review and testing

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
       "waf": "Security",
       "guid": "12345678-1234-1234-1234-123456789abc",
       "id": "01.01.01",
       "service": "YourService",
       "severity": "High",
       "link": "https://docs.microsoft.com/azure/..."
   }
   ```

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
   - Verify all GUIDs are unique
   - Check that all required fields are populated

7. **Submit a pull request**:
   - Commit your changes
   - Create a pull request against the main branch
   - Add appropriate reviewers (see [CODEOWNERS](../CODEOWNERS))

### Schema requirements

Your checklist must conform to the JSON schema defined in `checklist.schema.json`. Key requirements:

- **Required sections**: `items`, `categories`, `status`, `severities`, `metadata`
- **Item properties**: Each recommendation must have `category`, `text`, `guid`, `id`
- **Unique GUIDs**: All recommendation GUIDs must be globally unique
- **Valid links**: All URLs should be accessible and relevant

## How to modify existing checklists

### Option 1: Direct JSON modification

1. **Edit the English version only**: Modify the relevant `*.en.json` file
2. **Don't touch translations**: Never modify non-English versions (they are auto-generated)
3. **Add unique GUIDs**: For new recommendations, generate new GUIDs
4. **Follow the schema**: Ensure your changes conform to `checklist.schema.json`
5. **Submit a pull request**: PRs are reviewed by checklist owners (see [CODEOWNERS](../CODEOWNERS))

### Option 2: Using the Excel spreadsheet

1. Download the [Excel spreadsheet](../spreadsheet/review_checklist.xlsm)
2. Load your checklist and make changes
3. Export to JSON using the "Export checklist to JSON" button
4. Replace the relevant `.en.json` file with your exported JSON
5. Submit a pull request

## Localization

**Important**: This repository uses automated translation via [Azure Translator](https://azure.microsoft.com/services/cognitive-services/translator/).

- ✅ **DO**: Modify English versions (`*.en.json`) only
- ❌ **DON'T**: Modify translated versions (`*.es.json`, `*.ja.json`, etc.)
- **Why**: Translations are automatically regenerated and will overwrite manual changes

## Getting help

### Documentation and guidelines

- 📋 **General contributing**: See [CONTRIBUTING.md](../CONTRIBUTING.md)
- 🏗️ **Checklist creation**: Detailed steps in [CONTRIBUTING.md - Adding a new Checklist](../CONTRIBUTING.md#4-adding-a-new-checklist)
- 📊 **Excel usage**: See [spreadsheet/README.md](../spreadsheet/README.md)
- 📏 **Code owners**: Check [CODEOWNERS](../CODEOWNERS) for reviewers

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

All contributions are automatically validated:

- **JSON validation**: Syntax and schema compliance
- **GUID uniqueness**: Ensures no duplicate recommendation IDs
- **Link checking**: Validates that URLs are accessible
- **Translation**: Automatic generation of localized versions

For questions about validation failures, check the [GitHub Actions](../.github/workflows/) logs or create an issue.