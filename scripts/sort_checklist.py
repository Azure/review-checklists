#################################################################################
#
# This script sorts a specific checklist and saves it.
# 
# Last updated: January 2023
#
#################################################################################

import json
import argparse
import sys
import requests

# Get input arguments
parser = argparse.ArgumentParser(description='Update a checklist spreadsheet with JSON-formatted Azure Resource Graph results')
parser.add_argument('--input-file', dest='input_file', action='store',
                    help='You need to supply the name of the JSON file with the checklist to be filtered')
parser.add_argument('--output-file', dest='output_file', action='store',
                    help='You can optionally supply the name of a new JSON file that will be used to save the output. Otherwise the sorted checklist will replace the unused one')
parser.add_argument('--dry-run', dest='dry_run', action='store_true',
                    default=False,
                    help='do not save anything, only output to console (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

if not args.input_file:
    print("ERROR: no input file specified, not doing anything")

# Verifies that all dictionary items in the provided array have a non-empty "id" key
def all_items_have_id(items):
    for item in items:
        if not item['id']:
            return False
    return True

# Load the checklist
try:
    with open(args.input_file) as f:
        checklist = json.load(f)
except Exception as e:
    print("ERROR: Error when processing JSON file, nothing changed", args.input_file, "-", str(e))

# Sort the items per ID, or per category/subcategory if ID is missing
items = checklist['items']
if all_items_have_id(checklist['items']):
    items = sorted(items, key=lambda k: (k['id']))
else:
    items = sorted(items, key=lambda k: (k['category'],k["subcategory"]))
checklist['items'] = items

# If dry-run, show on screen
if args.dry_run:
    print(json.dumps(checklist, indent=4))

# Saving output file if specified in the argument
if not args.dry_run:
    if args.output_file:
        output_file = args.output_file
    else:
        output_file = args.input_file
    if args.verbose:
        print("DEBUG: saving output file to", output_file)
    checklist_string = json.dumps(checklist, indent=4)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(checklist_string)
        f.close()
