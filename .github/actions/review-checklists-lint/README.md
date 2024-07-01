# Azure review checklist linter

This action verifies the correctness of an Azure review checklist (stored in [this repo](https://github.com/Azure/review-checklists) and forks).

## Inputs

## `file_extension`

**Optional** File extension for the lists to be linted. Default `"en.json"`.

## `key_name`

**Optional** Key name in the JSON files to look for the unique values. Default `"guid"`.

## `criteria_key`

**Optional** JSON key to use so that only specific checklists are linted. Default `""`. It requires `criteria_value`.

## `criteria_value`

**Optional** JSON value to use so that only specific checklists are linted. Default `""`. It requires `criteria_key`.

## Outputs

## `number_of_checklists`

Number of checklists that have been linted

## Example usage

uses: erjosito/review-checklists-lint@v1
with:
  language: 'en'