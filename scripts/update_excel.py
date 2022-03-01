######################################################################
#
# This script reads the checklist items from the latest checklist file
#   in Github (or from a local file) and populates an Excel spreadsheet
#   with the contents.
# 
# Last updated: March 2022
#
######################################################################

import json
import argparse
import sys
import os
import requests
import xlwings as xw

# Get input arguments
parser = argparse.ArgumentParser(description='Update a checklist spreadsheet with JSON-formated Azure Resource Graph results')
parser.add_argument('--checklist-file', dest='checklist_file', action='store',
                    help='You can supply a JSON file containing the checklist you want to dump to the Excel spreadsheet')
parser.add_argument('--technology', dest='technology', action='store',
                    help='If you do not supply a JSON file with the checklist, you need to specify the technology from which the latest checklist will be downloaded from Github')
parser.add_argument('--excel-file', dest='excel_file', action='store',
                    help='You need to supply an Excel file where the checklist will be written')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()
checklist_file = args.checklist_file
excel_file = args.excel_file
technology = args.technology

# Constants
guid_column_index = "L"
comment_column_index = "G"
sample_cell_index = 'A2'
row1 = 5        # First row after which the Excel spreadsheet will be updated
col_area = "A"
col_subarea = "B"
col_check = "C"
col_desc = "D"
col_sev = "E"
col_status = "F"
col_comment = "G"
col_link = "H"
col_training = "I"
col_arg_success = "J"
col_arg_failure = "K"
col_guid = "L"

# Download checklist
if checklist_file:
    if args.verbose:
        print("DEBUG: Opening checklist file", checklist_file)
    # Get JSON
    try:
        with open(graph_file) as f:
            checklist_data = json.load(f)
    except Exception as e:
        print("ERROR: Error when processing JSON file", checklist_file, "-", str(e))
        sys.exit(1)
else:
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

# Load workbook
try:
    wb = xw.Book(excel_file)
    ws = wb.sheets['Checklist']
except Exception as e:
    print("ERROR: Error when opening Excel file", excel_file, "-", str(e))
    sys.exit(1)

# Get default status from the JSON, default to "Not verified"
try:
    status_list = checklist_data.get("status")
    default_status = status_list[0].get("name")
    if args.verbose:
        print ("DEBUG: default status retrieved from checklist:", default_status)
except:
    default_status = "Not verified"
    if args.verbose:
        print ("DEBUG: Using default status 'Not verified'")
    pass

# For each checklist item, add a row to spreadsheet
row_counter = row1
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
    status = default_status
    graph_query_success = item.get("graph_success")
    graph_query_failure = item.get("graph_failure")
    # Update Excel
    ws.range(col_area + str(row_counter)).value = category
    ws.range(col_subarea + str(row_counter)).value = subcategory
    ws.range(col_check + str(row_counter)).value = text
    ws.range(col_desc + str(row_counter)).value = description
    ws.range(col_sev + str(row_counter)).value = severity
    ws.range(col_status + str(row_counter)).value = status
    ws.range(col_link + str(row_counter)).value = link
    ws.range(col_training + str(row_counter)).value = training
    ws.range(col_arg_success + str(row_counter)).value = graph_query_success
    ws.range(col_arg_failure + str(row_counter)).value = graph_query_failure
    ws.range(col_guid + str(row_counter)).value = guid
    # Next row
    row_counter += 1

# Display summary
if args.verbose:
    print(str(row_counter - row1), "rows addedd to Excel spreadsheet")

# Close book
if args.verbose:
    print("DEBUG: saving workbook", excel_file)
try:
    wb.save()
except Exception as e:
    print("ERROR: Error when saving Excel file", excel_file, "-", str(e))
    sys.exit(1)
