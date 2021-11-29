# Contributing

For any contribution, please create the proposed changes in a forked repo, and open a Pull Request against the main branch.

## Changes to existing checklists

Modify the relevant `.en.json` file in the `checklists` directory and send a Pull Request to the main branch. Each checklist (LZ, AKS, AVD) has a predefined set of owners that will review the individual PRs (see [CODEOWNERS](./CODEOWNERS)).

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
