#################################################################################
#
# This script attempts to build a unified checklist out of all the different checklists
#   stored in this repo, and optionally filter it per design area.
# 
# Last updated: June 2022
#
#################################################################################

import json
import argparse
import sys
import requests

# Get input arguments
parser = argparse.ArgumentParser(description='Update a checklist spreadsheet with JSON-formated Azure Resource Graph results')
parser.add_argument('--output-file', dest='output_file', action='store',
                    help='You can optionally supply the name of the JSON file that will be created')
parser.add_argument('--category', dest='category_filter', action='store',
                    help='You can optionally provide a category name as a filter')
parser.add_argument('--checklist-name', dest='new_checklist_name', action='store',
                    default='Combined checklist',
                    help='You can optionally provide a category name as a filter')
parser.add_argument('--print-categories', dest='print_categories', action='store_true',
                    default=False,
                    help='print the categories of the combined checklist (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

if args.category_filter:
    category_filter = args.category_filter.lower()

# Variables
repo_contents_url = 'https://api.github.com/repos/azure/review-checklists/contents/checklists'

# Get existing checklists in the repo
response = requests.get(repo_contents_url)
# If download was successful
if response.status_code == 200:
    if args.verbose:
        print ("DEBUG: Github contents downloaded successfully from {0}".format(repo_contents_url))
    try:
        content_data = json.loads(response.text)
    except Exception as e:
        print("Error deserializing JSON content: {0}".format(str(e)))
        sys.exit(1)

# Get the list of checklist files
checklist_urls = []
if content_data:
    for github_object in content_data:
        if github_object['name'][-7:] == 'en.json':
            checklist_urls.append(github_object['download_url'])
else:
    print("Error deserializing JSON content from GitHub repository contents: {0}".format(str(e)))
    sys.exit(1)
if args.verbose:
    print("DEBUG: {0} checklists found".format(str(len(checklist_urls))))

# Load all of the items in memory
new_checklist = { 
    'items': [],
    'status': [
        {'name': 'Not verified', 'description': 'This check has not been looked at yet'},
        {'name': 'Open', 'description': 'There is an action item associated to this check'},
        {'name': 'Fulfilled', 'description': 'This check has been verified, and there are no further action items associated to it'},
        {'name': 'Not required', 'description': 'Recommendation understood, but not needed by current requirements'},
        {'name': 'N/A', 'description': 'Not applicable for current design'}
    ],
    'severities': [ {'name': 'High'}, {'name': 'Medium'}, {'name': 'Low'} ],
    'categories': [],
    'metadata': { 'name': args.new_checklist_name }
    }
for checklist_url in checklist_urls:
    if args.verbose:
        print("DEBUG: Downloading checklist file from", checklist_url)
    response = requests.get(checklist_url)
    if response.status_code == 200:
        if args.verbose:
            print ("DEBUG: File {0} downloaded successfully".format(checklist_url))
        try:
            # Deserialize JSON to object variable
            checklist_data = json.loads(response.text)
            checklist_name = checklist_data['metadata']['name']
            for item in checklist_data['items']:
                if checklist_name:
                    item['checklist'] = checklist_name
                item_category = str(item['category']).lower()
                if not args.category_filter or item_category.__contains__(category_filter):
                    new_checklist['items'].append(item)
        except Exception as e:
            print("Error deserializing JSON content: {0}".format(str(e)))
            sys.exit(1)
if args.verbose:
    print("DEBUG: Resulting combined checklist has {0} items".format(str(len(new_checklist['items']))))

# Add the categories to the new checklist
categories = []
for item in new_checklist['items']:
    if not item['category'] in categories:
        categories.append(item['category'])
if args.verbose:
    print("DEBUG: {0} categories found".format(str(len(categories))))
for category in categories:
    new_checklist['categories'].append({'name': category})
    if args.print_categories:
        print(category)

# Saving output file if specified in the argument
if args.output_file:
    if args.verbose:
        print("DEBUG: saving output file to", args.output_file)
    new_checklist_string = json.dumps(new_checklist)
    with open(args.output_file, 'w', encoding='utf-8') as f:
        f.write(new_checklist_string)
        f.close()
