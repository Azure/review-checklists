import json
import argparse
import sys
import requests

# Get input arguments
parser = argparse.ArgumentParser(description='Verify an external file (in the-aks-checklist repo) against this repos checklist')
parser.add_argument('--input-file', dest='input_file', action='store', default='./checklists/aks_checklist.en.json',
                    help='You can supply the name of the JSON file with the checklist to be checked. Defaults to ./checklists/aks_checklist.en.json')
parser.add_argument('--remote-url', dest='remote_url', action='store', default='https://www.the-aks-checklist.com/fta/aks_checklist.en.json',
                    help='You can supply the name of the URL containing the remote checklist. Defaults to https://www.the-aks-checklist.com/fta/aks_checklist.en.json')
parser.add_argument('--output-file', dest='output_file', action='store',
                    help='You can optionally supply the name of a new JSON file that will be used to save the output. Otherwise the sorted checklist will replace the unused one')
parser.add_argument('--dry-run', dest='dry_run', action='store_true', default=False,
                    help='do not save anything, only output to console (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true', default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# Output file defaults to input file
if not args.output_file:
    args.output_file = args.input_file

# Load the local checklist
if args.verbose:
    print("DEBUG: Loading local checklist from file", args.input_file)
try:
    with open(args.input_file) as f:
        local_checklist = json.load(f)
    if args.verbose:
        print("DEBUG: Loaded", len(local_checklist['items']), "items from local checklist")
except Exception as e:
    print("ERROR: Error when opening input JSON file, nothing changed", args.input_file, "-", str(e))
    sys.exit(1)

# Load the remote checklist
if args.verbose:
    print("DEBUG: Downloading remote checklist from", args.remote_url)
response = requests.get(args.remote_url)
if response.status_code == 200:
    if args.verbose:
        print ("DEBUG: File downloaded successfully from {0}".format(args.remote_url))
    try:
        # Deserialize JSON to object variable
        remote_checklist = json.loads(response.text)
        if args.verbose:
            print("DEBUG: Loaded", len(remote_checklist['items']), "items from remote checklist")
    except Exception as e:
        print("Error deserializing JSON content: {0}".format(str(e)))
        sys.exit(1)

def find_guid(item_list, guid):
    for item in item_list:
        if item['guid'] == guid:
            return item
    return None

# Compare the two checklists
new_items = []
if args.verbose:
    print("DEBUG: Comparing the two checklists")
local_items = local_checklist['items']
remote_items = remote_checklist['items']
if len(local_items) != len(remote_items):
    if args.verbose:
        print("DEBUG: The number of items in the local and remote checklist does not match")
    for remote_item in remote_items:
        if not find_guid(local_items, remote_item['guid']):
            new_items.append(remote_item)
if args.verbose:
    print("DEBUG: Found", len(new_items), "new items in the remote checklist")

# Print the new items if dry run
if args.dry_run:
    print(json.dumps(new_items, indent=4))
else:
    local_items.extend(new_items)
    if args.verbose:
        print("DEBUG: generating new list with", len(local_items), "items")
    local_items = sorted(local_items, key=lambda k: (k['category'],k["subcategory"]))       # Sort the items by category and subcategory
    local_checklist['items'] = local_items
    if args.verbose:
        print("DEBUG: Saving updated checklist to", args.output_file)
    with open(args.output_file, 'w') as f:
        json.dump(local_checklist, f, indent=4)
