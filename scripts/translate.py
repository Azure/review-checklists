import requests
import os
import argparse
import sys
import json
import uuid

# Variables
translate_keys = ('description', 'name', 'category', 'subcategory', 'text')
translate_languages = ['es', 'ja', 'pt', 'ko']

# Get environment variables
translator_endpoint = os.environ["AZURE_TRANSLATOR_ENDPOINT"]
translator_region = os.environ["AZURE_TRANSLATOR_REGION"]
translator_key = os.environ["AZURE_TRANSLATOR_SUBSCRIPTION_KEY"]
translator_url = translator_endpoint + 'translate'

# Get input arguments
parser = argparse.ArgumentParser(description='Translate a JSON file')
parser.add_argument('--input-file-name', dest='file_name_in', action='store',
                    help='you need to supply file name where your JSON to be translated is located')
parser.add_argument('--output-file-name', dest='file_name_out', action='store',
                    help='you need to supply file name where the translated JSON will be saved')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# Check we have all information
if translator_endpoint and translator_region and translator_key:
    if args.verbose:
        print('DEBUG: environment variables retrieved successfully: {0}, {1}, {2}'.format(translator_endpoint, translator_region, translator_key))
else:
    print('ERROR: couldnt retrieve environment variables for translation')
    sys.exit(1)

# Get JSON
try:
    with open(args.file_name_in) as f:
        checklist = json.load(f)
except Exception as e:
    print("ERROR: Error when processing JSON file", args.file_name_in, "-", str(e))
    sys.exit(1)

# Function to translate a single line of text to a single language
def translate_text(text_to_translate, languages):
    if args.verbose:
        print('DEBUG: translating text "{0}" on {1}...'.format(text_to_translate, translator_url))
    # If a single languages specified, convert to array
    if not type(languages) == list:
        languages = [languages]
    # Azure Translator parameters
    translator_params = {
        'api-version': '3.0',
        'from': 'en',
        'to': languages
    }
    translator_headers = {
        'Ocp-Apim-Subscription-Key': translator_key,
        'Ocp-Apim-Subscription-Region': translator_region,
        'Content-type': 'application/json',
        'Accept': 'application/json',
        'X-ClientTraceId': str(uuid.uuid4())
    }
    translator_body = [{
        'text': text_to_translate
    }]
    if args.verbose:
        print ("DEBUG: sending body", str(translator_body))
        print ("DEBUG: sending HTTP headers", str(translator_headers))
        print ("DEBUG: sending parameters", str(translator_params))
    try:
        request = requests.post(translator_url, params=translator_params, headers=translator_headers, json=translator_body)
        response = request.json()
        if args.verbose:
            print("DEBUG: translator response:")
            print(json.dumps(response, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
        return str(response[0]['translations'][0]['text'])
    except Exception as e:
        print("ERROR: Error in translation:", str(e))

# Go over all keys and translate them if required
def translate_object(checklist_object, language):
    translated_object = checklist_object.copy()
    for (k, v) in translated_object.items():
        if isinstance(v, list):
            translated_items = ()
            for list_item in v:
                translated_items.append(translate_object(list_item, language))
            translated_object[k] = translated_items
        else:
            if k in translate_keys:
                # print("Found key", k, "and scalar value", v)
                translated_object[k] = translate_text(v, language)
    return translated_object

################
#     Main     #
################

if args.verbose:
    print("DEBUG: Starting translations for languages", str(translate_languages))

for using_language in translate_languages:
    if args.verbose:
        print("DEBUG: Starting translation to", using_language)
    translated_checklist = translate_object(checklist, using_language)
    # If no output file was specified, use the input file, and append the language as extension before .json
    if not args.file_name_out:
        file_name_in_base = os.path.basename(args.file_name_in)
        file_name_in_dir = os.path.dirname(args.file_name_in)
        file_name_in_noext = file_name_in_base.split('.')[0]
        file_name_out = file_name_in_noext + '.' + using_language + '.json'
        file_name_out = os.path.join(file_name_in_dir, file_name_out)
        if args.verbose:
            print("DEBUG: saving output file to", file_name_out)
        translated_checklist_string = json.dumps(translated_checklist, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
        with open(file_name_out, 'w', encoding='utf-8') as f:
            f.write(translated_checklist_string)
            f.close()
        # print(json.dumps(translated_checklist, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': ')))
