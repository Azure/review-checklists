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
import os
from modules import cl_analyze

# Get input arguments
parser = argparse.ArgumentParser(description='Verify a JSON checklist for correctness')
parser.add_argument('--input-file', dest='input_file', action='store',
                    help='You need to supply the name of the JSON file with the checklist to be filtered')
parser.add_argument('--compare-file', dest='compare_file', action='store',
                    help='You can optionally supply the name of the JSON file with a second checklist to be compared against the first one')
parser.add_argument('--input-folder', dest='input_folder', action='store',
                    help='If no input file has been specified, input folder where the checklists to verify are stored')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# We need an input file
if args.input_file:
    guids = []
    file_stats, guids = cl_analyze.verify_file(args.input_file, guids=guids, verbose=args.verbose)
    if args.compare_file:
        compare_stats, guids = cl_analyze.verify_file(args.compare_file, guids=guids, verbose=args.verbose)
        # Print the differences between the two checklists stats in a table format
        print("INFO: Comparing the two checklists...")
        print("INFO: {0: <40} {1: <40} {2: <40}".format("Item", os.path.basename(args.input_file), os.path.basename(args.compare_file)))
        print("INFO: {0: <40} {1: <40} {2: <40}".format("----", "-" * len(os.path.basename(args.input_file)), "-" * len(os.path.basename(args.compare_file))))
        print("INFO: {0: <40} {1: <40} {2: <40}".format("Total items", file_stats['item_count'], compare_stats['item_count']))
        for key in file_stats['inconsistencies']:
            print("INFO: {0: <40} {1: <40} {2: <40}".format(key, file_stats['inconsistencies'][key], compare_stats['inconsistencies'][key]))
else:
    if args.input_folder:
        guids = []
        language = "en"  # This could be changed to a parameter
        if args.verbose:
            print("DEBUG: looking for JSON files in folder", args.input_folder, "with pattern *.", language + ".json...")
        checklist_files = glob.glob(args.input_folder + "/*." + language + ".json")
        if len(checklist_files) > 0:
            if args.verbose:
                print("DEBUG: found", len(checklist_files), "JSON files, analyzing correctness...")
            for file in checklist_files:
                if file:
                    file_stats, guids = cl_analyze.verify_file(file, guids=guids, verbose=args.verbose)
        else:
            print("ERROR: no input file found, not doing anything")
    else:
        print("ERROR: you need to use the parameters `--input-file` or `--input-folder` to specify the file or folder to verify")

