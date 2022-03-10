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
                    help='You can optionally supply a JSON file containing the checklist you want to dump to the Excel spreadsheet. Otherwise it will take the latest file from Github')
parser.add_argument('--technology', dest='technology', action='store',
                    help='If you do not supply a JSON file with the checklist, you need to specify the technology from which the latest checklist will be downloaded from Github')
parser.add_argument('--excel-file', dest='excel_file', action='store',
                    help='You need to supply an Excel file where the checklist will be written')
parser.add_argument('--app-mode', dest='appmode', action='store_true',
                    default=False,
                    help='Open Excel workbook in App mode, not great for systems without Excel installed (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()
checklist_file = args.checklist_file
excel_file = args.excel_file
technology = args.technology

# Constants
worksheet_checklist_name = 'Checklist'
row1 = 10        # First row after which the Excel spreadsheet will be updated
col_checklist_name = "A"
row_checklist_name = "6"
guid_column_index = "L"
comment_column_index = "G"
sample_cell_index = 'A2'
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
info_link_text = 'More info'
training_link_text = 'Training'
worksheet_values_name = 'Values'
values_row1 = 2
col_values_severity = "A"
col_values_status = "B"
col_values_area = "C"
col_values_description = "H"


# Download checklist
if checklist_file:
    if args.verbose:
        print("DEBUG: Opening checklist file", checklist_file)
    # Get JSON
    try:
        with open(checklist_file) as f:
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
    if args.appmode:
        print("DEBUG: opening Excel workbook in app mode 'App().books.open'...")
        app = xw.App()
        wb = app.books.open(excel_file)
    else:
        print("DEBUG: opening Excel workbook with xb.Book function...")
        wb = xw.Book(excel_file)  # This line is occassionally giving the error "(-2147352570, 'Unknown name.', None, None)"
    if args.verbose:
        print("DEBUG: workbook", excel_file, "opened successfully")
except Exception as e:
    print("ERROR: Error when opening Excel file", excel_file, "-", str(e))
    sys.exit(1)

# Get worksheet
try:
    ws = wb.sheets[worksheet_checklist_name]
    if args.verbose:
        print("DEBUG: worksheet", worksheet_checklist_name, "selected successfully")
except Exception as e:
    print("ERROR: Error when selecting worksheet", worksheet_checklist_name, "-", str(e))
    sys.exit(1)

# Set checklist name
try:
    ws.range(col_checklist_name + row_checklist_name).value = checklist_data["metadata"]["name"]
    if args.verbose:
        print("DEBUG: starting filling the Excel spreadsheet with the values of checklist '{0}'".format(checklist_data["metadata"]["name"]))
except Exception as e:
    print("ERROR: Error when selecting worksheet", worksheet_checklist_name, "-", str(e))
    sys.exit(1)

# Get default status from the JSON, default to "Not verified"
try:
    status_list = checklist_data.get("status")
    default_status = status_list[0].get("name")
    if args.verbose:
        print ("DEBUG: default status retrieved from checklist: '{0}'".format(default_status))
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
    # ws.range(col_link + str(row_counter)).value = link
    if link != None:
        link_elements = link.split('#')
        link_address = link_elements[0]
        if len(link_elements) > 1:
            link_subaddress = link_elements[1]
        else:
            link_subaddress = ""
        ws.api.Hyperlinks.Add (Anchor=ws.range(col_link + str(row_counter)).api, Address=link_address, SubAddress=link_subaddress, ScreenTip="", TextToDisplay=info_link_text)
    # ws.range(col_training + str(row_counter)).value = training
    if training != None:
        training_elements = training.split('#')
        training_address = training_elements[0]
        if len(training_elements) > 1:
            training_subaddress = training_elements[1]
        else:
            training_subaddress = ""
        ws.api.Hyperlinks.Add (Anchor=ws.range(col_training + str(row_counter)).api, Address=training_address, SubAddress=training_subaddress, ScreenTip="", TextToDisplay=training_link_text)
    # GUID and ARG queries
    ws.range(col_arg_success + str(row_counter)).value = graph_query_success
    ws.range(col_arg_failure + str(row_counter)).value = graph_query_failure
    ws.range(col_guid + str(row_counter)).value = guid
    # Next row
    row_counter += 1

# Display summary
if args.verbose:
    print("DEBUG:", str(row_counter - row1), "checks addedd to Excel spreadsheet")

# Get worksheet
try:
    wsv = wb.sheets[worksheet_values_name]
    if args.verbose:
        print("DEBUG: worksheet", worksheet_values_name, "selected successfully")
except Exception as e:
    print("ERROR: Error when selecting worksheet", worksheet_values_name, "-", str(e))
    sys.exit(1)


# Update categories
row_counter = values_row1
for item in checklist_data.get("categories"):
    area = item.get("name")
    wsv.range(col_values_area + str(row_counter)).value = area
    row_counter += 1

# Display summary
if args.verbose:
    print("DEBUG:", str(row_counter - values_row1), "categories addedd to Excel spreadsheet")

# Update status
row_counter = values_row1
for item in checklist_data.get("status"):
    status = item.get("name")
    description = item.get("description")
    wsv.range(col_values_status + str(row_counter)).value = status
    wsv.range(col_values_description + str(row_counter)).value = description
    row_counter += 1

# Display summary
if args.verbose:
    print("DEBUG:", str(row_counter - values_row1), "statuses addedd to Excel spreadsheet")

# Update severities
row_counter = values_row1
for item in checklist_data.get("severities"):
    severity = item.get("name")
    wsv.range(col_values_severity + str(row_counter)).value = severity
    row_counter += 1

# Display summary
if args.verbose:
    print("DEBUG:", str(row_counter - values_row1), "severities addedd to Excel spreadsheet")

# Close book
if args.verbose:
    print("DEBUG: saving workbook", excel_file)
try:
    wb.save()
    if args.appmode:
        app.quit()      # If we were in app mode, close Excel
except Exception as e:
    print("ERROR: Error when saving Excel file", excel_file, "-", str(e))
    sys.exit(1)
