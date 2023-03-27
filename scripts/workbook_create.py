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
import re

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
parser.add_argument('--create-arm-template', dest='create_arm_template', action='store_true',
                    default=True,
                    help='create an ARM template, additionally to the workbook JSON (default: False)')
parser.add_argument('--category', dest='category', action='store',
                    help='if the workbook should be restricted to a category containing the specified string')
parser.add_argument('--counters', dest='counters', action='store_true',
                    default=False,
                    help='Whether compliance counters will be included in the workbook. Note that workbooks generated this way usually incur in ARG throttling limits. Default is False.')
parser.add_argument('--tab-counters', dest='tab_counters', action='store_true',
                    default=False,
                    help='Whether compliance counters will be included in the workbook tabs. Note that workbooks generated this way usually incur in ARG throttling limits. Default is False.')
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
    global block_invisible_parameter
    global block_arm

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
    # Load itemgroup (aka section, aka tab) building block
    if args.tab_counters:
        block_file = os.path.join(blocks_path, 'block_itemgroup_withcounters.json')
    else
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
    # Load invisible parameter building block
    block_file = os.path.join(blocks_path, 'block_invisible_parameter.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_invisible_parameter = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON workbook building block", block_file, "-", str(e))
        sys.exit(0)
    # Load ARM template building block
    block_file = os.path.join(blocks_path, 'block_arm.json')
    if args.verbose:
        print ("DEBUG: Loading file {0}...".format(block_file))
    try:
        with open(block_file) as f:
            block_arm = json.load(f)
    except Exception as e:
        print("ERROR: Error when opening JSON ARM template building block", block_file, "-", str(e))
        sys.exit(0)

# Function that corrects format issues in the queries stored in JSON
def fix_query_format(query_string):
    if query_string:
        query_string = str(query_string).replace('\\\\', '\\')  # Replace a double escaping inverted bar ('\\\\') through a single one ('\')
        return query_string
    else:
        return None

# Function that transforms a JSON string to be included in an ARM template
def serialize_data(workbook_string):
    if workbook_string:
        # Escape double quotes
        workbook_string = str(workbook_string).replace('"', '\"')
        # Escape escape characters
        # workbook_string = str(workbook_string).replace('\\', '\\\\')
        # Undo the scaping for the newline character (otherwise the markdown in the workbook would look wrong).
        # Note that this might impact newline characters in queries!
        # workbook_string = str(workbook_string).replace('\\\\n', '\\n')
        return workbook_string
    else:
        return None

# Returns the index of a specific item in the workbook content
def workbook_item_index(workbook, item_name):
    for i in range(len(workbook['items'])):
        if workbook['items'][i]['name'] == item_name:
            return i
    return -1


# Main function to generate the workbook JSON
def generate_workbook(output_file, checklist_data):

    # Initialize an empty workbook
    workbook = json.loads(json.dumps(block_workbook))
    workbook_title = "## " + checklist_data['metadata']['name']
    if args.category:
        workbook_title += ' - ' + args.category[0].upper() + args.category[1:]
    workbook_title += "\n\n---\n\nThis workbook has been automatically generated out of the checklists in the [Azure Review Checklists repo](https://github.com/Azure/review-checklists)."
    workbook_title += "\n\n---\n\n**NOTE**: If some queries in this workbook do not work at loading, it can be because there is a maximum of simultaneous queries that can be sent to Azure Resource Graph. Please refresh the failed queries manually."
    markdown_index = workbook_item_index(workbook, 'MarkdownHeader')
    workbook['items'][markdown_index]['content']['json'] = workbook_title

    # If not using counters, we can change some things in the workbook
    if not args.counters:
        if args.verbose:
            print("DEBUG: removing sections from workbook. Before removing, {0} items exist".format(len(workbook['items'])))
        # Setting width of markdown to 100% to avoid the counters to be displayed on the right
        workbook['items'][markdown_index]['customWidth'] = '100'
        # Deleting invisible parameter and tile items
        hidden_parameter_index = workbook_item_index(workbook, 'InvisibleParameters')
        workbook['items'].pop(hidden_parameter_index)
        tile_index = workbook_item_index(workbook, 'ProgressTile')
        workbook['items'].pop(tile_index)
        if args.verbose:
            print("DEBUG: removing sections from workbook. After removing, {0} items exist".format(len(workbook['items'])))

    # Decide whether we will match in the category, or subcategory, and update the corresponding variables
    if args.category:
        if args.verbose:
            print("DEBUG: creating tab list with subcategories list for categories containing the term {0}...".format(args.category))
        tab_name_field = 'subcategory'
        tab_title_list = [x["subcategory"] for x in checklist_data.get("items") if (args.category.lower() in str(x["category"]).lower())]
        tab_title_list = list(set(tab_title_list))
        checklist_items = [x for x in checklist_data.get("items") if (args.category.lower() in str(x["category"]).lower())]
        if args.verbose:
            print("DEBUG: {0} items match category {1}".format(str(len(checklist_items)), args.category))
    else:
        if args.verbose:
            print("DEBUG: creating tab list with categories...")
        tab_name_field = 'category'
        tab_title_list = [x["name"] for x in checklist_data.get("categories")]
        checklist_items = checklist_data.get("items")
        if args.verbose:
            print("DEBUG: {0} items found in checklist".format(str(len(checklist_items))))
    if args.verbose:
        print("DEBUG: created tab list: {0}".format(str(tab_title_list)))

    # Remove the cats/subcats without queries defined
    total_expected_queries = 0
    tabs_to_remove = []
    for tab_title in tab_title_list:
        if args.category:
            items_with_query = [x['guid'] for x in checklist_items if ((str(x['subcategory']) == tab_title) and ('graph' in x.keys()) and ('guid' in x.keys()))]
        else:
            items_with_query = [x['guid'] for x in checklist_items if ((x['category'] == tab_title) and ('graph' in x.keys()))]
        if args.verbose:
            print("DEBUG: Items with query matching subcategory {0}: {1}, length {2}".format(tab_title, str(items_with_query), str(len(items_with_query))))
        if len(items_with_query) == 0:
            if args.verbose:
                print("DEBUG: Removing tab {0} from list, it doesn't seem to have any graph queries defined".format(tab_title))
            tabs_to_remove.append(tab_title)
        else:
            total_expected_queries += len(items_with_query)
            if args.verbose:
                # print("DEBUG: Incrementing total_expected queries (type {0}) by {1} to {2}".format(str(type(total_expected_queries)), str(len(items_with_query)), str(total_expected_queries)))
                print("DEBUG: Leaving tab {0} in tab list, it has {1} graph queries".format(tab_title, str(len(items_with_query))))
    for tab_title in tabs_to_remove:
        tab_title_list.remove(tab_title)

    # If verbose show the final tab list:
    if args.verbose:
        print("DEBUG: final tab list: {0}".format(str(tab_title_list)))
        print("DEBUG: {0} expected queries".format(str(total_expected_queries)))

    # Bidimensional array to hold the graphs queries (x=>tab_index, y=>query_index)
    queries=[]
    for tab_title in tab_title_list:
        queries.append([])

    # Generate one tab in the workbook for each category/subcategory
    tab_id = 0
    query_id = 0
    tab_dict = {}
    links_index = workbook_item_index(workbook, 'Tabs')
    for tab_title in tab_title_list:
        tab_dict[tab_title] = tab_id  # We will use this dict later to know where to put each query
        if args.verbose:
            print("Adding tab {0} to workbook...".format(tab_title))
        # Create new link
        new_link = block_link.copy()
        new_link['id'] = str(uuid.uuid4())   # RANDOM GUID
        # The tab title depends if we are generating counters or not
        if args.counters:
            new_link['linkLabel'] = tab_title + ' ({Section' + str(tab_id) + 'Success:value}/{Section' + str(tab_id) + 'Total:value})'
        else:
            new_link['linkLabel'] = tab_title
        new_link['subTarget'] = 'tab' + str(tab_id)
        new_link['preText'] = tab_title
        # Create new section
        new_section = block_section.copy()
        new_section['name'] = 'tab' + str(tab_id)
        new_section['conditionalVisibility']['value'] = 'tab' + str(tab_id)
        new_section['content']['items'][0]['content']['json'] = "## " + tab_title
        new_section['content']['items'][0]['name'] = 'tab' + str(tab_id) + 'title'
        # Add link
        workbook['items'][links_index]['content']['links'].append(new_link.copy())   # I am getting crazy with Python variable references :(
        # Add section (group)
        new_new_section=json.loads(json.dumps(new_section.copy()))
        workbook['items'].append(new_new_section)
        tab_id += 1

    # Display dictionary in screen if on verbose
    if args.verbose:
        print("DEBUG: tab dictionary generated: {0}".format(str(tab_dict)))

    # For each checklist item, add a query to the workbook
    for item in checklist_data.get("items"):
        # We will append this to every query
        query_suffix = ' | extend onlyFailed = {OnlyFailed:label} | where compliant == 0 or not (onlyFailed == 1) | project-away onlyFailed'
        # Read variables from JSON
        guid = item.get("guid")
        tab = item.get(tab_name_field)
        text = item.get("text")
        description = item.get("description")
        severity = item.get("severity")
        link = item.get("link")
        training = item.get("training")
        graph_query = fix_query_format(item.get("graph"))
        if graph_query:
            if tab in tab_title_list:
                if args.verbose:
                    print("DEBUG: adding sections to workbook for ARG query '{0}', length of query is {1}".format(str(graph_query), str(len(str(graph_query)))))
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
                new_query['content']['query'] = graph_query + query_suffix
                new_query['content']['size'] = query_size
                # Add text and query to the workbook
                if args.counters:
                    tab_id = tab_dict[tab] + len(block_workbook['items'])
                else:
                    # If not using counters, we removed two sections...
                    tab_id = tab_dict[tab] + len(block_workbook['items']) - 2
                if args.verbose:
                    print ("DEBUG: Adding text and query to tab ID {0} ({1} -> {2}) of {3} elements in workbook".format(str(tab_id), tab, tab_dict[tab], len(workbook['items'])))
                    print ("DEBUG: Workbook object name is {0}".format(workbook['items'][tab_id]['name']))
                new_new_text = json.loads(json.dumps(new_text.copy()))
                new_new_query = json.loads(json.dumps(new_query.copy()))
                workbook['items'][tab_id]['content']['items'].append(new_new_text)
                workbook['items'][tab_id]['content']['items'].append(new_new_query)
                # Add query to the query array
                tab_id = tab_title_list.index(tab)
                queries[tab_id].append(graph_query)
                # Increment query counter
                query_id += 1
            # The fact that a query is not in the list is normal if doing the workbook for a specific category (such as Networking)
            # else:
            #     if args.verbose:
            #         print("ERROR: Query {0} in section {1}, but section not in the section list!".format(graph_query, tab))
    
    # Store the number of queries processed in its own variable (will be checked when deciding whether generating output or not)
    num_of_queries = query_id
    if num_of_queries != total_expected_queries:
        if args.verbose:
            print('WARNING: Something is not quite right, I was expecting to process {0} queries, but I found {1}'.format(str(total_expected_queries), str(num_of_queries)))

    # If generating workbook with detailed counters
    if args.counters:

        # Add invisible parameters to the workbook with number of success and total items
        if args.verbose:
            print("DEBUG: Adding hidden parameters to workbook main section for {0} tabs...".format(str(len(queries))))
        tab_id = 0
        hidden_parameter_index = workbook_item_index(workbook, 'InvisibleParameters')
        for tab_title in tab_title_list:
            print("DEBUG: Adding hidden parameters for tab {0} - {1}, with {2} queries".format(str(tab_id), tab_title, str(len(queries[tab_id]))))
            # We shouldn't have any tabs without queries, but still...
            if len(queries[tab_id]) > 0:
                query_id = 0
                summary_query = queries[tab_id][query_id]
                while query_id + 1 < len(queries[tab_id]):
                    query_id += 1
                    summary_query += "| union ({0})".format(queries[tab_id][query_id])
                success_query = summary_query + '| where compliant == 1 | summarize Total = tostring(count())'
                total_query = summary_query + '| summarize Total = tostring(count())'
                # Add parameter with Total elements
                new_parameter = block_invisible_parameter.copy()
                new_parameter['query'] = total_query
                new_parameter['name'] = 'Section' + str(tab_id) + 'Total'
                new_new_parameter = json.loads(json.dumps(new_parameter.copy()))
                workbook['items'][hidden_parameter_index]['content']['parameters'].append(new_new_parameter)
                # Add parameter with Success elements
                new_parameter = block_invisible_parameter.copy()
                new_parameter['query'] = success_query
                new_parameter['name'] = 'Section' + str(tab_id) + 'Success'
                new_new_parameter = json.loads(json.dumps(new_parameter.copy()))
                workbook['items'][hidden_parameter_index]['content']['parameters'].append(new_new_parameter)
            # Move to the next query
            tab_id += 1

        # We can now adapt the query of the success percent tile
        tile_index = workbook_item_index(workbook, 'ProgressTile')
        tab_id = 0
        total_formula = ''
        success_formula = ''
        for tab_title in tab_title_list:
            if len(total_formula) > 1:
                total_formula += '+'
            total_formula += '{Section' + str(tab_id) + 'Total:value}'
            if len(success_formula) > 1:
                success_formula += '+'
            success_formula += '{Section' + str(tab_id) + 'Success:value}'
            tab_id += 1
        progress_query = 'resources | summarize count() | extend Total = ' + total_formula + ', Success = ' + success_formula + ' | extend SuccessPercent = round(toreal(Success)/toreal(Total), 2) * 100, SubTitle = \'Percent of compliant resources\''
        workbook['items'][tile_index]['content']['query'] = progress_query

    # Dump the workbook to the output file or to console, if there was any query in the original checklist
    if args.verbose:
        print ("DEBUG: Starting output process. to {0}...".format(output_file))
    if num_of_queries > 0:
        if output_file:
            # Dump workbook JSON into a file
            workbook_string = json.dumps(workbook, indent=4)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(workbook_string)
                f.close()
            # Create ARM template (optionally, if specified in the parameters)
            if args.create_arm_template:
                arm_output_file = os.path.splitext(output_file)[0] + '_template.json'
                if args.verbose:
                    print ("DEBUG: Creating ARM template in file {0}...".format(arm_output_file))
                block_arm['parameters']['workbookDisplayName']['defaultValue'] = checklist_data['metadata']['name']
                if args.category:
                    block_arm['parameters']['workbookDisplayName']['defaultValue'] += ' - ' + args.category[0].upper() + args.category[1:]
                block_arm['resources'][0]['properties']['serializedData'] = serialize_data(workbook_string)
                arm_string = json.dumps(block_arm, indent=4)
                with open(arm_output_file, 'w', encoding='utf-8') as f:
                    f.write(arm_string)
                    f.close()
        else:
            print(workbook_string)
    else:
        print("INFO: sorry, the analyzed checklist did not contain any graph query")

def get_output_file(checklist_file_or_url, is_file=True):
    # If output file specified, use it
    if args.output_file:
        return args.output_file
    # Else, figure out one
    elif args.output_path:
        # First come up with an initial filename, depending if provided a file or an URL
        if is_file:
            output_file = os.path.basename(checklist_file_or_url)
        else:
            output_file = checklist_file_or_url.split('/')[-1]
        # Get filename without path and extension
        output_file = os.path.join(args.output_path, output_file)
        # If category specified, add to output file name
        if args.category:
            output_file = os.path.splitext(output_file)[0] + '_' + str(args.category).lower() + '.json'
        # If counters created, add 'counters' to output file name
        if args.counters:
            output_file = os.path.splitext(output_file)[0] + '_counters.json'
    # Return the final file name
    return os.path.splitext(output_file)[0] + '_workbook.json'

########
# Main #
########

# First thing of all, load the building blocks
load_building_blocks()
if args.verbose:
    print ("DEBUG: building blocks variables intialized:")
    print ("DEBUG:    - Workbook: {0}".format(str(block_workbook)))
    print ("DEBUG:    -    Number of items: {0}".format(str(len(block_workbook['items']))))
    print ("DEBUG:    - Link: {0}".format(str(block_link)))
    print ("DEBUG:    - Query: {0}".format(str(block_query)))

# Download checklist or process from local file
if checklist_file:
    checklist_file_list = checklist_file.split(" ")
    # Take only the English versions of the checklists (JSON files)
    checklist_file_list = [file[:-8] + '.en.json' for file in checklist_file_list if (os.path.splitext(file)[1] == '.json')]
    # Remove duplicates
    checklist_file_list = list(set(checklist_file_list))
    # Go over the list(s)
    for checklist_file in checklist_file_list:
        if args.verbose:
            print("DEBUG: Opening checklist file", checklist_file)
        # Get JSON
        try:
            # Open file
            with open(checklist_file) as f:
                checklist_data = json.load(f)
            # Set output file variable
            output_file = get_output_file(checklist_file, is_file=True)
            # Generate workbook
            generate_workbook(output_file, checklist_data)
        # If error, just continue
        except Exception as e:
            print("ERROR: Error when processing JSON file", checklist_file, "-", str(e))
            # sys.exit(0)
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

