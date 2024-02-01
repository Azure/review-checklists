# Contributing

If you wish to make a contribution, please create the proposed changes in a forked repository and open a Pull Request against the main branch. Microsoft engineers will verify the proposed change, and either accept it, suggest modifications, or decline it. The following sections cover changes to different objects in this repository:

1. Adding Resource Graph Queries
1. Modifying recommendations (modifying the JSON directly, or generating new JSON from the macro-enabled spreadsheet)
1. Modifying the spreadsheet assets

## 1. Adding or modifying Resource Graph queries

When adding Azure Resource Graph queries to existing recommendations the query is expected to return (at least) two fields:

* `id`: ARM ID of the resource being evaluated
* `compliant`: boolean value that indicates whether the resource is compliant or non-compliant with the recommendation

For example, take the recommendation in the AKS checklist "Use Availability Zones if supported in your Azure region". The following query creates the `compliant` column based on a boolean check, and returns both the `id` and the new `compliant` columns:

```
where type=='microsoft.containerservice/managedclusters' | extend compliant= isnotnull(zones) | distinct id,compliant
```

It is important for the query to return these two fields for the automation to work such as the bash script and automatic Azure Monitor Workbook generation.

### Microsoft approvers

Microsoft approvers should verify the correct operation of the proposed ARG query before approving the Pull Request:

- The query doesn't return either false positives or false negatives.
- The output fields are `id` and `compliant` (case is important).

## 2. Modifications to checklists recommendations

There are two ways in which you can modify the existing checklists:

### Option 2a: Modifying the JSON file directly

To make changes to existing checklists, modify the relevant `.en.json` file in the `checklists` directory, either in the Github portal or in your own clone using your favorite text editor, and then submit  a Pull Request to the main branch. Each checklist (LZ, AKS, AVD) has a predefined set of owners that will review the individual PRs (see [CODEOWNERS](./CODEOWNERS)).

> **Warning**
> Do not modify the non-English versions of the checklists, as they are dynamically generated

If you are adding new rules, make sure to include unique GUIDs for each. You can use your favorite GUID generation tool to generate new random GUIDs, such as [https://guidgenerator.com/](https://guidgenerator.com/)

### Option 2b: Using the spreadsheet to create new JSON files

Optionally, you can use the provided Excel spreadsheet to make changes to the existing checklists:

1. Open the [Excel spreadsheet](./spreadsheet/review_checklist.xlsm), and load the English version of any of the supported checklist
1. Make any changes you want. Some remarks:
    - If adding or changing hyperlinks, it is OK to put the raw URL in the corresponding cell. The export mechanism will take care of removing the localization
    - If adding new rules, you can leave the GUID field empty, the export mechanism will generate a new random GUID
1. Export the checklist to a JSON file (using the button "Export checklist to JSON"), which you can check into the GitHub repository (refer to [Option 1: Modifying the JSON file directly](#option-1-modifying-the-jSON-file-directly))

## 3. Changes to the spreadsheet

Modify the file [spreadsheet/review_checklist.xlsm](./spreadsheet/review_checklist.xlsm) in your own fork, and send a Pull Request to the main branch. Make sure not to check in temporary files (by closing the Excel spreadsheet before git-adding the files).

## Forking the Repository

If you fork this repository, you will need to set up an Azure Translator in Azure and define three secrets in your repository to enable automatic translation:

- `AZURE_TRANSLATOR_ENDPOINT`: containing the endpoint URL for your Azure Translator. You will find this in the Azure Portal, in the blade "Keys and Endpoint" of your Azure Translator, under "Text Translation".
- `AZURE_TRANSLATOR_REGION` (optional): containing the region for your Azure Translator. You will find this in the Azure Portal, in the blade "Keys and Endpoint" of your Azure Translator, under "Location/Region".
- `AZURE_TRANSLATOR_SUBSCRIPTION_KEY`: the subscription key for your Azure Translator. You will find this in the Azure Portal, in the blade "Keys and Endpoint" of your Azure Translator, under "Key 1" or "Key 2" (you can use either of them).
