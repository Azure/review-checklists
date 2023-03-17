######################################################################
#
# This script combines all of the existing checklists into one big
#   checklist, and saves it in JSON and XLSX (macrofree) formats.
#
# Example usage:
# python3 ./scripts/create_master_checklist.py \
#   --input-folder="./checklists" \
#   --language="en" \
#   --excel-file="./spreadsheet/macrofree/review_checklist_master_empty.xlsx" \
#   --output-name="checklist.en.master" \
#   --json-output-folder="./checklists/" \
#   --xlsx-output-folder="./spreadsheet/macrofree/"
# 
# Last updated: March 2022
#
######################################################################

import json
import argparse
import sys
import os
import requests
import glob
import datetime
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

# Get input arguments
parser = argparse.ArgumentParser(description='Update a checklist spreadsheet with JSON-formatted Azure Resource Graph results')
parser.add_argument('--input-folder', dest='input_folder', action='store',
                    help='Input folder where the checklists to merge are stored')
parser.add_argument('--language', dest='language', action='store', default='en',
                    help='if checklist files are specified, ignore the non-English ones and only generate a spreadsheet for the English version (default: False)')
parser.add_argument('--excel-file', dest='excel_file', action='store',
                    help='You need to supply an Excel file that will be taken as template to create the XLSX file with the checklist')
parser.add_argument('--json-output-folder', dest='json_output_folder', action='store',
                    help='Folder where to store the JSON output')
parser.add_argument('--xlsx-output-folder', dest='xlsx_output_folder', action='store',
                    help='Folder where to store the macro free Excel output')
parser.add_argument('--output-name', dest='output_name', action='store',
                    help='File name (without extension) for the output files (.json and .xlsx extensions will be added automatically)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# Consolidate all checklists into one big checklist object
def get_consolidated_checklist(input_folder, language):
    # Initialize checklist object
    checklist_master_data = {
        'items': [],
        'metadata': {
            'name': 'Master checklist',
            'timestamp': datetime.date.today().strftime("%B %d, %Y")
        }
    }
    # Find all files in the input folder matching the pattern "language*.json"
    if args.verbose:
        print("DEBUG: looking for JSON files in folder", input_folder, "with pattern *.", language + ".json...")
    checklist_files = glob.glob(input_folder + "/*." + language + ".json")
    if args.verbose:
        print("DEBUG: found", len(checklist_files), "JSON files")
    for checklist_file in checklist_files:
        # Get JSON
        try:
            with open(checklist_file) as f:
                checklist_data = json.load(f)
                if args.verbose:
                    print("DEBUG: JSON file", checklist_file, "loaded successfully with {0} items".format(len(checklist_data["items"])))
                for item in checklist_data["items"]:
                    # Add field with the name of the checklist
                    item["checklist"] = checklist_data["metadata"]["name"]
                # Add items to the master checklist
                checklist_master_data['items'] += checklist_data['items']
                # Replace the master checklist severities and status sections (for a given language they should be all the same)
                checklist_master_data['severities'] = checklist_data['severities']
                checklist_master_data['status'] = checklist_data['status']
        except Exception as e:
            print("ERROR: Error when processing JSON file", checklist_file, "-", str(e))
    if args.verbose:
        print("DEBUG: master checklist contains", len(checklist_master_data["items"]), "items")
    return checklist_master_data

# Dump JSON object to file
def dump_json_file(json_object, filename):
    if args.verbose:
        print("DEBUG: dumping JSON object to file", filename)
    json_string = json.dumps(json_object, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json_string)
        f.close()

# Main function
def update_excel_file(input_excel_file, output_excel_file, checklist_data):
    # Constants
    worksheet_checklist_name = 'Checklist'
    row1 = 8        # First row after which the Excel spreadsheet will be updated
    col_checklist_name = "A"
    row_checklist_name = "4"
    guid_column_index = "L"
    comment_column_index = "G"
    sample_cell_index = 'A4'
    col_checklist="A"
    col_area = "B"
    col_subarea = "C"
    col_check = "D"
    col_desc = "E"
    col_sev = "F"
    col_status = "G"
    col_comment = "H"
    col_link = "I"
    col_training = "J"
    col_arg_success = "K"
    col_arg_failure = "L"
    col_guid = "M"
    info_link_text = 'More info'
    training_link_text = 'Training'
    worksheet_values_name = 'Values'
    values_row1 = 2
    col_values_severity = "A"
    col_values_status = "B"
    col_values_area = "C"
    col_values_description = "H"

    # Load workbook
    try:
        wb = load_workbook(filename = input_excel_file)
        if args.verbose:
            print("DEBUG: workbook", input_excel_file, "opened successfully")
    except Exception as e:
        print("ERROR: Error when opening Excel file", input_excel_file, "-", str(e))
        sys.exit(1)

    # Get worksheet
    try:
        ws = wb[worksheet_checklist_name]
        if args.verbose:
            print("DEBUG: worksheet", worksheet_checklist_name, "selected successfully")
    except Exception as e:
        print("ERROR: Error when selecting worksheet", worksheet_checklist_name, "-", str(e))
        sys.exit(1)

    # Set checklist name
    try:
        ws[col_checklist_name + row_checklist_name] = checklist_data["metadata"]["name"]
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
        checklist_name = item.get("checklist")
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
        ws[col_checklist + str(row_counter)].value = checklist_name
        ws[col_area + str(row_counter)].value = category
        ws[col_subarea + str(row_counter)].value = subcategory
        ws[col_check + str(row_counter)].value = text
        ws[col_desc + str(row_counter)].value = description
        ws[col_sev + str(row_counter)].value = severity
        ws[col_status + str(row_counter)].value = status
        ws[col_link + str(row_counter)].value = link
        # if link != None:
        #     link_elements = link.split('#')
        #     link_address = link_elements[0]
        #     if len(link_elements) > 1:
        #         link_subaddress = link_elements[1]
        #     else:
        #         link_subaddress = ""
        #     ws.api.Hyperlinks.Add (Anchor=ws[col_link + str(row_counter)].api, Address=link_address, SubAddress=link_subaddress, ScreenTip="", TextToDisplay=info_link_text)
        ws[col_training + str(row_counter)].value = training
        # if training != None:
        #     training_elements = training.split('#')
        #     training_address = training_elements[0]
        #     if len(training_elements) > 1:
        #         training_subaddress = training_elements[1]
        #     else:
        #         training_subaddress = ""
        #     ws.api.Hyperlinks.Add (Anchor=ws[col_training + str(row_counter)].api, Address=training_address, SubAddress=training_subaddress, ScreenTip="", TextToDisplay=training_link_text)
        # GUID and ARG queries
        ws[col_arg_success + str(row_counter)].value = graph_query_success
        ws[col_arg_failure + str(row_counter)].value = graph_query_failure
        ws[col_guid + str(row_counter)].value = guid
        # Next row
        row_counter += 1

    # Display summary
    if args.verbose:
        number_of_checks = row_counter - row1
        print("DEBUG:", str(number_of_checks), "checks addedd to Excel spreadsheet")

    # Get worksheet
    try:
        wsv = wb[worksheet_values_name]
        if args.verbose:
            print("DEBUG: worksheet", worksheet_values_name, "selected successfully")
    except Exception as e:
        print("ERROR: Error when selecting worksheet", worksheet_values_name, "-", str(e))
        sys.exit(1)

    # Update status
    row_counter = values_row1
    for item in checklist_data.get("status"):
        status = item.get("name")
        description = item.get("description")
        wsv[col_values_status + str(row_counter)].value = status
        wsv[col_values_description + str(row_counter)].value = description
        row_counter += 1

    # Display summary
    if args.verbose:
        print("DEBUG:", str(row_counter - values_row1), "statuses addedd to Excel spreadsheet")

    # Update severities
    row_counter = values_row1
    for item in checklist_data.get("severities"):
        severity = item.get("name")
        wsv[col_values_severity + str(row_counter)].value = severity
        row_counter += 1

    # Display summary
    if args.verbose:
        print("DEBUG:", str(row_counter - values_row1), "severities addedd to Excel spreadsheet")

    # Data validation
    # dv = DataValidation(type="list", formula1='=Values!$B$2:$B$6', allow_blank=True, showDropDown=True)
    dv = DataValidation(type="list", formula1='=Values!$B$2:$B$6', allow_blank=True)
    rangevar = col_status + str(row1) +':' + col_status + str(row1 + number_of_checks)
    if args.verbose:
        print("DEBUG: adding data validation to range", rangevar)
    dv.add(rangevar)
    ws.add_data_validation(dv)

    # Close book
    if args.verbose:
        print("DEBUG: saving workbook", output_excel_file)
    try:
        wb.save(output_excel_file)
    except Exception as e:
        print("ERROR: Error when saving Excel file to", output_excel_file, "-", str(e))
        sys.exit(1)

########
# Main #
########

# Download checklist
if args.input_folder:
    # Get consolidated checklist
    checklist_master_data = get_consolidated_checklist(args.input_folder, args.language)
    # Set output file variables
    xlsx_output_file = os.path.join(args.xlsx_output_folder, args.output_name + ".xlsx")
    json_output_file = os.path.join(args.json_output_folder, args.output_name + ".json")
    # Dump master checklist to JSON file
    dump_json_file(checklist_master_data, json_output_file)
    # Update spreadsheet
    update_excel_file(args.excel_file, xlsx_output_file, checklist_master_data)
else:
    print("ERROR: No input folder specified")
