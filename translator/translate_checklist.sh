#!/bin/zsh

# Variables
technology=aks
target_language=es
akv_name=erjositoKeyvault  # AKV where translator URL and key are stored
translator_key_secret_name=checklist-translator-key
api_endpoint="https://api.cognitive.microsofttranslator.com/"
translator_region=eastus2
checklist_url="https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/${technology}_checklist.en.json"
# category='general'  # default translator
category='1189c438-382c-4dd4-83ca-d0de3a7ac49b-checklist-TECH' # custom model for en2es

# Day 0: store your key as keyvault secret
# az keyvault secret set -n $translator_key_secret_name --vault-name $akv_name --value "your_azure_translator_key"

# Retrieve the translator API from AKV
translator_key=$(az keyvault secret show -n $translator_key_secret_name --vault-name $akv_name --query value -o tsv)
url="https://api.cognitive.microsofttranslator.com/translate?api-version=3.0&from=en&to=${target_language}&category=${category}"
region_header="Ocp-Apim-Subscription-Region: ${translator_region}"
key_header="Ocp-Apim-Subscription-Key: ${translator_key}"
content_header="Content-Type: application/json; charset=UTF-8"

# Get the JSON file, and extract the texts
local_file=/tmp/checklist.json
wget -q -O $local_file $checklist_url
text_list=$(cat $local_file | jq -r '.items[].text')

# Translate, and print original and translation, tab-separated
while read -r original_text; do
    payload="[{\"Text\":\"$original_text\"}]"
    translated_text=$(curl -s -X POST "$url" -H "$key_header" -H $region_header -H "$content_header" -d "$payload" | jq -r '.[0].translations[0].text')
    echo "${original_text}\t${translated_text}"
done <<< "$text_list"

