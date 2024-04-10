#################################################################################
#
# This script verifies a specific checklist for correctness.
# 
# Last updated: April 2024
#
#################################################################################

import json
import argparse
import sys
import glob


# Get input arguments
parser = argparse.ArgumentParser(description='Verify a JSON checklist for correctness')
parser.add_argument('--input-file', dest='input_file', action='store',
                    help='You need to supply the name of the JSON file with the checklist to be filtered')
parser.add_argument('--input-folder', dest='input_folder', action='store',
                    help='If no input file has been specified, input folder where the checklists to verify are stored')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# Global variables
guids = []

# Function that verifies the correctness of a single checklist
def verify_file(input_file):
    # Banner
    if args.verbose:
        print("DEBUG: ======================================================================")
        print("DEBUG: Verifying file", input_file)
    # Look for non-unicode characters in the file
    if args.verbose:
        print("DEBUG: Verifying all characters are Unicode-8...")
    f1 = open (input_file, "r")
    text = f1.read()
    for line in text:
        for character in line:
            if ord(character) > 127:
                print("ERROR: Non-unicode character found in file", input_file, ":", character)
                sys.exit(1)
    # if args.verbose:
    #     print("DEBUG: All characters are Unicode-8")

    # Reading into JSON
    if args.verbose:
        print("DEBUG: Verifying JSON can be loaded up...")
    try:
        with open(input_file) as f:
            checklist = json.load(f)
    except Exception as e:
        print("ERROR: Error when processing JSON file, nothing changed", input_file, ":", str(e))
        sys.exit(1)
    # if args.verbose:
    #     print("DEBUG: JSON can be loaded up correctly")

    # Verify the required keys are present
    if args.verbose:
        print("DEBUG: Verifying the required keys are present...")
    required_keys = ['items', 'metadata', 'categories', 'status', 'severities', 'yesno']
    for key in required_keys:
        if key not in checklist:
            print("ERROR: Required key missing from JSON file", input_file, ":", key)

    # Verify the metadata keys are present
    if 'metadata' in checklist:
        if args.verbose:
            print("DEBUG: Verifying the metadata keys are present...")
        required_keys = ['name', 'timestamp', 'state', 'waf']
        for key in required_keys:
            if key not in checklist['metadata']:
                print("ERROR: Required key missing from metadata in JSON file", input_file, ":", key)
    else:
        if args.verbose:
            print("WARNING: skipping metadata verification, no metadata in JSON file", input_file)

    # Verify the metadata waf key has a valid value
    if 'metadata' in checklist:
        if 'waf' in checklist['metadata']:
            if checklist['metadata']['waf'].lower() not in ['none', 'all', 'reliability', 'security', 'performance', 'cost', 'operations']:
                print("ERROR: Invalid WAF value in metadata in JSON file", input_file, ":", checklist['metadata']['waf'])

    # Verify the items have all required keys
    if args.verbose:
        print("DEBUG: Verifying the items have all required keys...")
    # Counter dictionary for inconsistencies
    inconsistencies = {
        'wrong_cat': 0,
        'missing_cat': 0,
        'missing_subcat': 0,
        'missing_waf': 0,
        'missing_svc': 0,
        'missing_link': 0,
        'missing_sev': 0,
        'missing_guid': 0,
        'localized_link': 0
    }
    # Load categories to verify whether the items have the correct category
    if 'categories' in checklist:
        categories = [x['name'] for x in checklist['categories']]
        if args.verbose:
            print("DEBUG: Categories found in JSON file", input_file, ":", str(categories))
    else:
        categories = []
    if 'items' in checklist:
        for item in checklist['items']:
            if 'category' not in item:
                inconsistencies['missing_cat'] += 1
            elif item['category'] not in categories:
                inconsistencies['wrong_cat'] += 1
            if 'subcategory' not in item:
                inconsistencies['missing_subcat'] += 1
            if 'waf' not in item:
                inconsistencies['missing_waf'] += 1
            if 'service' not in item:
                inconsistencies['missing_svc'] += 1
            if 'guid' not in item:
                inconsistencies['missing_guid'] += 1
            elif item['guid'] in guids:
                print("ERROR: Duplicated GUID in JSON file", input_file, ":", item['guid'])
            else:
                guids.append(item['guid'])
            if 'link' not in item:
                inconsistencies['missing_link'] += 1
            elif 'en-us' in item['link']:
                inconsistencies['localized_link'] += 1
            if 'severity' not in item:
                inconsistencies['missing_sev'] += 1
        if inconsistencies['missing_cat'] > 0:
            print("ERROR: Items with missing category in JSON file", input_file, ":", inconsistencies['missing_cat'])
        if inconsistencies['wrong_cat'] > 0:
            print("WARNING: Items with wrong category in JSON file", input_file, ":", inconsistencies['wrong_cat'])
        if inconsistencies['missing_subcat'] > 0:
            print("ERROR: Items with missing subcategory in JSON file", input_file, ":", inconsistencies['missing_subcat'])
        if inconsistencies['missing_waf'] > 0:
            print("ERROR: Items with missing WAF in JSON file", input_file, ":", inconsistencies['missing_waf'])
        if inconsistencies['missing_svc'] > 0:
            print("ERROR: Items with missing service in JSON file", input_file, ":", inconsistencies['missing_svc'])
        if inconsistencies['missing_link'] > 0:
            print("ERROR: Items with missing link in JSON file", input_file, ":", inconsistencies['missing_link'])
        if inconsistencies['missing_sev'] > 0:
            print("ERROR: Items with missing severity in JSON file", input_file, ":", inconsistencies['missing_sev'])
        if inconsistencies['localized_link'] > 0:
            print("WARNING: Items with localized links in JSON file", input_file, ":", inconsistencies['localized_link'])

# We need an input file
if args.input_file:
    verify_file(args.input_file)
else:
    if args.input_folder:
        language = "en"  # This could be changed to a parameter
        if args.verbose:
            print("DEBUG: looking for JSON files in folder", args.input_folder, "with pattern *.", language + ".json...")
        checklist_files = glob.glob(args.input_folder + "/*." + language + ".json")
        if len(checklist_files) > 0:
            if args.verbose:
                print("DEBUG: found", len(checklist_files), "JSON files, analyzing correctness...")
            for file in checklist_files:
                if file:
                    verify_file(file)
        else:
            print("ERROR: no input file found, not doing anything")
    else:
        print("ERROR: you need to use the parameters `--input-file` or `--input-folder` to specify the file or folder to verify")

