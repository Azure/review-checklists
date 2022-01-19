# Contributing

For any contribution, please create the proposed changes in a forked repo, and open a Pull Request against the main branch.

## Changes to existing checklists

There are two ways in which you can send changes to the existing checklists:

### Option 1: Modifying the JSON file directly

Modify the relevant `.en.json` file in the `checklists` directory, either in the Github portal or in your own clone with your favorite text editor, and send a Pull Request to the main branch. Each checklist (LZ, AKS, AVD) has a predefined set of owners that will review the individual PRs (see [CODEOWNERS](./CODEOWNERS)).

If you are adding new rules, make sure to include unique GUIDs for each. You can use your favorite GUID generation tool to generate new random GUIDs, such as [https://guidgenerator.com/](https://guidgenerator.com/)

### Option 2: Using the spreadsheet to create new JSON files

Optionally, you can use the provided Excel spreadsheet to do changes to the existing checklists:

1. Open the [Excel spreadsheet](./spreadsheet/review_checklist.xlsm), and load the English version of any of the supported checklist
1. Do any change you want. Some remarks:
    - If adding or changing hyperlinks, it is OK putting the raw URL in the corresponding cell. The export mechanism will take care of removing the localization
    - If adding new rules, you can leave the GUID field empty, the export mechanism will generate a new random GUID
1. Export the checklist to a JSON file (using the button "Export checklist to JSON"), which you can check into the Github repository (refer to [Option 1: Modifying the JSON file directly](#option-1-modifying-the-jSON-file-directly))

## Adding Resource Graph queries

When adding Azure Resource Graph queries, two different queries are expected:

* **Success** query, returning a list of resources that are **compliant** with the checklist recommendation
* **Failure** query, returning a list of resources that are **non-compliant** with the checklist recommendation

Both queries should return at least the following fields for each resource:

- id
- name
- resourceGroup (if applicable, subscriptions do not have a resource group)

## Changes to the spreadsheet

Modify the file [spreadsheet/review_checklist.xlsm](./spreadsheet/review_checklist.xlsm) in your own fork, and send a Pull Request to the main branch. Make sure not to check in temporary files (by closing the Excel spreadsheet before git-adding the files).
