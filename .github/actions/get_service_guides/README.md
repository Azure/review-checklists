# Retrieve recommendations from Well Architected service guides

This action retrieves the recommendations described in [Well-Architected Service Guides](https://learn.microsoft.com/azure/well-architected/service-guides/?product=popular) and stores it as a new checklist.

## Inputs

## `service`

**Optional** Service whose service guide will be downloaded (leave blank for all service guides). Default `""`.

## `output_folder`

**Optional** File where the new checklist will be stored. Default `"./checklists"`.

## `verbose`

**Optional** Whether script output is verbose or not. Default `"true"`.

## Example usage

```
uses: ./.github/actions/get_service_guides
with:
  output_file: './checklists'
  service: 'Azure Kubernetes Service'
```