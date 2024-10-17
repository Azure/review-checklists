# Retrieve recommendations from Well Architected service guides

This action retrieves the recommendations described in [Well-Architected Service Guides](https://learn.microsoft.com/azure/well-architected/service-guides/?product=popular) and stores it as a new checklist.

## Inputs

## `services`

**Optional** Service(s) whose service guide will be downloaded (leave blank for all service guides). You can specify multiple comma-separated values. Default `""`.

## `output_folder`

**Optional** Folder where the new checklists will be stored. Default `"./checklists-ext"`.

## `verbose`

**Optional** Whether script output is verbose or not. Default `"true"`.

## Example usage

```
uses: ./.github/actions/get_service_guides
with:
  output_file: './checklists'
  service: 'Azure Kubernetes Service'
```
