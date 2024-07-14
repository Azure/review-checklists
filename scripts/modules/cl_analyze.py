#######################################
#
# Module to analyze checklist files
#
#######################################

# Dependencies
import sys
import json
import os

# Function that verifies the correctness of a single checklist
def verify_file(input_file, guids=[], verbose=False):
    # Banner
    if verbose:
        print("DEBUG: ======================================================================")
        print("DEBUG: Verifying file", input_file)
    # Look for non-unicode characters in the file
    if verbose:
        print("DEBUG: Verifying all characters are Unicode-8...")
    f1 = open (input_file, "r")
    text = f1.read()
    for line in text:
        for character in line:
            if ord(character) > 127:
                print("ERROR: Non-unicode character found in file", input_file, ":", character)
                sys.exit(1)
    # if verbose:
    #     print("DEBUG: All characters are Unicode-8")

    # Reading into JSON
    if verbose:
        print("DEBUG: Verifying JSON can be loaded up...")
    try:
        with open(input_file) as f:
            checklist = json.load(f)
        if 'items' in checklist:
            if verbose:
                print("DEBUG: {0} items found in JSON file {1}".format(len(checklist['items']), input_file))
    except Exception as e:
        print("ERROR: Error when processing JSON file, nothing changed", input_file, ":", str(e))
        sys.exit(1)
    # if verbose:
    #     print("DEBUG: JSON can be loaded up correctly")

    # Verify the required keys are present
    if verbose:
        print("DEBUG: Verifying the required keys are present...")
    required_keys = ['items', 'metadata', 'categories', 'status', 'severities', 'yesno']
    for key in required_keys:
        if key not in checklist:
            print("ERROR: Required key missing from JSON file", input_file, ":", key)

    # Verify the metadata keys are present
    if 'metadata' in checklist:
        if verbose:
            print("DEBUG: Verifying the metadata keys are present...")
        required_keys = ['name', 'timestamp', 'state', 'waf']
        for key in required_keys:
            if key not in checklist['metadata']:
                print("ERROR: Required key missing from metadata in JSON file", input_file, ":", key)
    else:
        if verbose:
            print("WARNING: skipping metadata verification, no metadata in JSON file", input_file)

    # Verify the metadata waf key has a valid value
    if 'metadata' in checklist:
        if 'waf' in checklist['metadata']:
            if checklist['metadata']['waf'].lower() not in ['none', 'all', 'reliability', 'security', 'performance', 'cost', 'operations']:
                print("ERROR: Invalid WAF value in metadata in JSON file", input_file, ":", checklist['metadata']['waf'])

    # Verify the items have all required keys
    if verbose:
        print("DEBUG: Verifying the items have all required keys...")
    # Counter dictionary for inconsistencies
    item_count = 0
    inconsistencies = {
        'missing_graph': 0,
        'missing_description': 0,
        'wrong_cat': 0,
        'missing_cat': 0,
        'missing_subcat': 0,
        'missing_waf': 0,
        'wrong_waf': 0,
        'missing_svc': 0,
        'missing_link': 0,
        'missing_sev': 0,
        'missing_guid': 0,
        'localized_link': 0
    }
    # Load categories to verify whether the items have the correct category
    if 'categories' in checklist:
        categories = [x['name'] for x in checklist['categories']]
        if verbose:
            print("DEBUG: Categories found in JSON file", input_file, ":", str(categories))
    else:
        categories = []
    if 'items' in checklist:
        for item in checklist['items']:
            item_count += 1
            if 'category' not in item:
                inconsistencies['missing_cat'] += 1
            elif item['category'] not in categories:
                inconsistencies['wrong_cat'] += 1
            if 'subcategory' not in item:
                inconsistencies['missing_subcat'] += 1
            if 'waf' not in item:
                inconsistencies['missing_waf'] += 1
            elif item['waf'].lower() not in ['reliability', 'security', 'performance', 'cost', 'operations']:
                inconsistencies['wrong_waf'] += 1
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
            if 'graph' not in item:
                inconsistencies['missing_graph'] += 1
            if 'description' not in item:
                inconsistencies['missing_description'] += 1
        if inconsistencies['missing_cat'] > 0:
            print("ERROR: Items with missing category in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['missing_cat'], round(inconsistencies['missing_cat'] / item_count * 100, 2)))
        if inconsistencies['wrong_cat'] > 0:
            print("WARNING: Items with wrong category in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['wrong_cat'], round(inconsistencies['wrong_cat'] / item_count * 100, 2)))
        if inconsistencies['missing_subcat'] > 0:
            print("ERROR: Items with missing subcategory in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['missing_subcat'], round(inconsistencies['missing_subcat'] / item_count * 100, 2)))
        if inconsistencies['missing_waf'] > 0:
            print("WARNING: Items with missing WAF in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['missing_waf'], round(inconsistencies['missing_waf'] / item_count * 100, 2)))
        if inconsistencies['wrong_waf'] > 0:
            print("ERROR: Items with wrong WAF in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['wrong_waf'], round(inconsistencies['wrong_waf'] / item_count * 100, 2)))
        if inconsistencies['missing_svc'] > 0:
            print("WARNING: Items with missing service in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['missing_svc'], round(inconsistencies['missing_svc'] / item_count * 100, 2)))
        if inconsistencies['missing_link'] > 0:
            print("WARNING: Items with missing link in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['missing_link'], round(inconsistencies['missing_link'] / item_count * 100, 2)))
        if inconsistencies['missing_sev'] > 0:
            print("ERROR: Items with missing severity in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['missing_sev'], round(inconsistencies['missing_sev'] / item_count * 100, 2)))
        if inconsistencies['localized_link'] > 0:
            print("WARNING: Items with localized link in JSON file {0}: {1} ({2}%)".format(input_file, inconsistencies['localized_link'], round(inconsistencies['localized_link'] / item_count * 100, 2)))
    return {
        'item_count': item_count,
        'inconsistencies': inconsistencies
    }, guids
