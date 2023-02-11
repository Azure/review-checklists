######################################################################
#
# This script reads the checklist items from the latest checklist file
#   in Github (or from a local file) and generates an Azure Monitor
#   workbook in JSON format.
# 
# Last updated: February 2023
#
######################################################################

import json
import argparse
import sys
import os
import requests
import glob
import uuid

# Get input arguments
parser = argparse.ArgumentParser(description='Generate Azure Monitor workbook from Azure Review Checklist')
parser.add_argument('--checklist-file', dest='checklist_file', action='store',
                    help='You can optionally supply a JSON file containing the checklist you want to dump to the Excel spreadsheet. Otherwise it will take the latest file from Github')
parser.add_argument('--only-english', dest='only_english', action='store_true', default=False,
                    help='if checklist files are specified, ignore the non-English ones and only generate a spreadsheet for the English version (default: False)')
parser.add_argument('--find-all', dest='find_all', action='store_true', default=False,
                    help='if checklist files are specified, find all the languages for the given checklists (default: False)')
parser.add_argument('--technology', dest='technology', action='store',
                    help='If you do not supply a JSON file with the checklist, you need to specify the technology from which the latest checklist will be downloaded from Github')
parser.add_argument('--output-file', dest='output_file', action='store',
                    help='You can optionally supply an Excel file where the checklist will be saved, otherwise it will be updated in-place')
parser.add_argument('--output-path', dest='output_path', action='store',
                    help='Folder where to store the results (using the same name as the input_file)')
parser.add_argument('--blocks-path', dest='blocks_path', action='store',
                    help='Folder where the building blocks to build the workbook are stored)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()
checklist_file = args.checklist_file
technology = args.technology

block_workbook = None
block_link = None
block_section = None
block_query = None
block_text = None

query_size = 4 # 0: medium, 1: small, 4: tiny

# Workbook building blocks
def load_building_blocks():

    # Define the blocks as global variables
    global block_workbook
    global block_link
    global block_section
    global block_query
    global block_text

    # Set folder where to load from
    if args.blocks_path:
        blocks_path = args.blocks_path
        if args.verbose:
            print ("DEBUG: Setting building block folder to {0}".format(blocks_path))
    else:
        print("ERROR: please use the argument --blocks-path to specify the location of the workbook building blocks.")
        sys.exit(1)

    # Load initial workbook building block
    block_file = os.path.join(blocks_path, 'block_workbook.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_workbook = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON workbook building block", block_file, "-", str(e))
        sys.exit(0)
    # Load link building block
    block_file = os.path.join(blocks_path, 'block_link.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_link = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON workbook building block", block_file, "-", str(e))
        sys.exit(0)
    # Load itemgroup (aka section) building block
    block_file = os.path.join(blocks_path, 'block_itemgroup.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_section = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON workbook building block", block_file, "-", str(e))
        sys.exit(0)
    # Load query building block
    block_file = os.path.join(blocks_path, 'block_query.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_query = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON workbook building block", block_file, "-", str(e))
        sys.exit(0)
    # Load text building block
    block_file = os.path.join(blocks_path, 'block_text.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_text = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON workbook building block", block_file, "-", str(e))
        sys.exit(0)

# Main function to generate the workbook JSON
def generate_workbook(output_file, checklist_data):

    # Initialize an empty workbook
    workbook = block_workbook

    # Generate one tab in the workbook for each category
    category_id = 0
    query_id = 0
    category_dict = {}
    for item in checklist_data.get("categories"):
        category_title = item.get("name")
        category_id += 1
        category_dict[category_title] = category_id + 1  # We will use this dict later to know where to put each query
        # Create new link
        new_link = block_link.copy()
        new_link['id'] = str(uuid.uuid4())   # RANDOM GUID
        new_link['linkLabel'] = category_title
        new_link['subTarget'] = 'category' + str(category_id)
        new_link['preText'] = category_title
        # Create new section
        new_section = block_section.copy()
        new_section['name'] = 'category' + str(category_id)
        new_section['conditionalVisibility']['value'] = 'category' + str(category_id)
        new_section['content']['items'][0]['content']['json'] = "## " + category_title
        new_section['content']['items'][0]['name'] = 'category' + str(category_id) + 'title'
        # Add link and query to workbook
        # if args.verbose:
        #     print()
        #     print ("DEBUG: Adding link: {0}".format(json.dumps(new_link)))
        #     print ("DEBUG: Adding section: {0}".format(json.dumps(new_section)))
        #     print("DEBUG: Workbook so far: {0}".format(json.dumps(workbook)))
        workbook['items'][1]['content']['links'].append(new_link.copy())   # I am getting crazy with Python variable references :(
        # Add section to workbook
        new_new_section=json.loads(json.dumps(new_section.copy()))
        workbook['items'].append(new_new_section)

    # For each checklist item, add a row to spreadsheet
    for item in checklist_data.get("items"):
        # Read variables from JSON
        guid = item.get("guid")
        category = item.get("category")
        subcategory = item.get("subcategory")
        text = item.get("text")
        description = item.get("description")
        severity = item.get("severity")
        link = item.get("link")
        training = item.get("training")
        graph_query = item.get("graph")
        if graph_query:
            query_id += 1
            # Create new text
            new_text = block_text.copy()
            new_text['name'] = 'querytext' + str(query_id)
            new_text['content']['json'] = text
            if link:
                new_text['content']['json'] += ". Check [this link](" + link + ") for further information."
            if training:
                new_text['content']['json'] += ". [This training](" + training + ") can help to educate yourself on this."
            # Create new query
            new_query = block_query.copy()
            new_query['name'] = 'query' + str(query_id)
            new_query['content']['query'] = graph_query
            new_query['content']['size'] = query_size
            # Add text and query to the workbook
            category_id = category_dict[category]
            if args.verbose:
                print ("DEBUG: Adding text and query to category ID {0}, workbook object name is {1}".format(str(category_id), workbook['items'][category_id]['name']))
            new_new_text=json.loads(json.dumps(new_text.copy()))
            new_new_query=json.loads(json.dumps(new_query.copy()))
            workbook['items'][category_id]['content']['items'].append(new_new_text)
            workbook['items'][category_id]['content']['items'].append(new_new_query)

    # Dump the workbook to the output file or to console, if there was any query in the original checklist
    if query_id > 0:
        workbook_string = json.dumps(workbook, indent=4)
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(workbook_string)
                f.close()
        else:
            print(workbook_string)
    else:
        print("INFO: sorry, the analyzed checklist did not contain any graph query")

def get_output_file(checklist_file_or_url, is_file=True):
    if is_file:
        output_file = os.path.basename(checklist_file_or_url)
    else:
        output_file = checklist_file_or_url.split('/')[-1]
    if args.output_file:
        return args.output_file
    elif args.output_path:
        # Get filename without path and extension
        output_file = os.path.join(args.output_path, output_file)
        return os.path.splitext(output_file)[0] + '_workbook.json'
    else:
        output_file = None


########
# Main #
########

# First thing of all, load the building blocks
load_building_blocks()
if args.verbose:
    print ("DEBUG: building blocks variables intialized:")
    print ("DEBUG:    - Workbook: {0}".format(str(block_workbook)))
    print ("DEBUG:    - Link: {0}".format(str(block_link)))
    print ("DEBUG:    - Query: {0}".format(str(block_query)))

# Download checklist or process from local file
if checklist_file:
    checklist_file_list = checklist_file.split(" ")
    # Take only the English versions of the checklists and remove duplicates
    checklist_file_list = [file[:-8] + '.en.json' for file in checklist_file_list]
    checklist_file_list = list(set(checklist_file_list))
    # Go over the list(s)
    for checklist_file in checklist_file_list:
        if args.verbose:
            print("DEBUG: Opening checklist file", checklist_file)
        # Get JSON
        try:
            with open(checklist_file) as f:
                checklist_data = json.load(f)
        except Exception as e:
            print("ERROR: Error when processing JSON file", checklist_file, "-", str(e))
            sys.exit(0)
        # Set output files
        output_file = get_output_file(checklist_file, is_file=True)
        # Generate workbook
        generate_workbook(output_file, checklist_data)
else:
    # If no input files specified, fetch the latest from Github...
    if technology:
        checklist_url = "https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/" + technology + "_checklist.en.json"
    else:
        checklist_url = "https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/lz_checklist.en.json"
    if args.verbose:
        print("DEBUG: Downloading checklist file from", checklist_url)
    response = requests.get(checklist_url)
    # If download was successful
    if response.status_code == 200:
        if args.verbose:
            print ("DEBUG: File {0} downloaded successfully".format(checklist_url))
        try:
            # Deserialize JSON to object variable
            checklist_data = json.loads(response.text)
        except Exception as e:
            print("Error deserializing JSON content: {0}".format(str(e)))
            sys.exit(1)
        # Set output files
        output_file = get_output_file(checklist_url, is_file=False)
        # Generate workbook
        generate_workbook(output_file, checklist_data)

