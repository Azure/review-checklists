#!/bin/bash
#########################################################
# This script triggers post-processing of changes
#    in a checklist file, that should be provided as
#    first argument.
# This script should be run from the root directory of
#    of the repo
# Example:
#    ./scripts/process_checklist ./checklists/aks_checklist.en.json
#########################################################
checklist_file=$1
if [[ -z $checklist_file ]]; then
    echo "You should supply a parameter with the path location of the checklist to process"
    exit 0
else
    if [[ -e $checklist_file ]]; then
        file_beginning=${checklist_file:0:12}
        if [[ "$file_beginning" == "./checklists" ]]; then
            file_end=${checklist_file: -8}
            if [[ "$file_end" == ".en.json" ]]; then
                echo "Processing file $checklist_file..."
                # Sort original checklist
                python3 ./scripts/sort_checklist.py --input-file "$checklist_file"
                # Timestamp original checklist
                python3 ./scripts/timestamp_checklist.py --input-file "$checklist_file"
                # Translate checklist
                python3 ./scripts/translate.py --input-file "$checklist_file"
                # Generate macro-free spreadsheets
                python3 ./scripts/update_excel_openpyxl.py --checklist-file="$checklist_file" --find-all --excel-file="./spreadsheet/review_checklist_empty.xlsx" --output-name-is-input-name --output-path="./spreadsheet/macrofree/" --verbose
                # Create Azure Monitor Workbook
                python3 ./scripts/workbook_create.py --checklist-file "$checklist_file" --output-path ./workbooks --blocks-path ./workbooks/blocks
            else
                echo "File $checklist_file doesn't have the right extension '.en.json'"
            fi
        else
            echo "File $checklist_file doesnt start with './checklists' but with $file_beginning, are you sure you are in the right folder?"
            exit 0
        fi
    else
        echo "File $checklist_file could not be found"
        exit 0
    fi
fi