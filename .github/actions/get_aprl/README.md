# Retrieve recommendations from the-aks-checklist

This action retrieves the recommendations stored in [the-aks-checklist repo](https://github.com/lgmorand/the-aks-checklist/tree/master/data/en/items) and stores it as a new checklist.

## Inputs

## `output_file`

**Optional** File where the new checklist will be stored. Default `"./checklists/theaks_checklist.en.json"`.

## `checklist_file`

**Optional** File where the existing checklist is located. Default `"./checklists/aks_checklist.en.json"`.

## `verbose`

**Optional** Whether verbose output is generated. Default `"true"`.


## Example usage

```
uses: ./.github/actions/get_the_aks_checklist
with:
  output_file: './checklists/theaks_checklist.en.json'
  checklist_file: './checklists/aks_checklist.en.json'
```