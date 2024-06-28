# Retrieve recommendations from Well Architected service guides

This action retrieves the recommendations described in [Well-Architected Service Guides](https://learn.microsoft.com/azure/well-architected/service-guides/?product=popular) and stores it as a new checklist.

## Inputs

## `output_folder`

**Optional** File where the new checklist will be stored. Default `"./checklists"`.

## `service`

**Optional** Service for which recommendations will be stored. For example, `"Azure Firewall"` or `"Azure Kubernetes Service"`. Default `""`.

## `verbose`

**Optional** Whether verbose output is generated. Default `"true"`.

## Example usage

```
uses: ./.github/actions/get_service_guides
with:
  output_file: './checklists'
  service: 'Azure Kubernetes Service'
  verbose: 'true'
```