#################################################################################
#
# This is the checklists CLI. It is a command-line interface that allows users to
#    perform various operations on checklists.
#
# Supported commands:
# - analyze: Analyze a checklist
#
# Last updated: July 2024
#
#################################################################################

import json
import argparse
import sys
import glob
import os
from modules import cl_analyze
from modules import cl_v1tov2

# Get input arguments
parser = argparse.ArgumentParser(description='Checklists CLI', prog='checklists')
subparsers = parser.add_subparsers(dest='command', help='Command help')
# Define common shared arguments
base_subparser = argparse.ArgumentParser(add_help=False)
base_subparser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
# Create the 'analyze' command
analyze_parser = subparsers.add_parser('analyze', help='Analyze a checklist', parents=[base_subparser])
analyze_parser.add_argument('--input-file', dest='analyze_input_file', action='store',
                    help='name of the JSON file with the checklist to be analyzed')
analyze_parser.add_argument('--compare-file', dest='analyze_compare_file', action='store',
                    help='you can optionally supply the name of the JSON file with a second checklist to be compared against the first one')
analyze_parser.add_argument('--input-folder', dest='analyze_input_folder', action='store',
                    help='if no input file has been specified, input folder where the checklists to verify are stored')
# Create the 'v1tov2' command
v12_parser = subparsers.add_parser('v12', help='Convert v1 to v2', parents=[base_subparser])
v12_parser.add_argument('--input-file', dest='v12_input_file', action='store',
                    help='name of the JSON file with the v1 checklist to be converted to v2')
v12_parser.add_argument('--output-folder', dest='v12_output_folder', action='store',
                    help='output folder where the v2 checklist items will be stored')
v12_parser.add_argument('--output-format', dest='v12_output_format', action='store',
                    default='yaml',
                    help='output format of the v12 checklist items (default: yaml)')


# Parse the command-line arguments
args = parser.parse_args()

# Handle the parsed arguments based on the command and sub-command
if args.command == 'analyze':
    guids = []
    # We need an input file or an input folder
    if args.analyze_input_file:
        file_stats, guids = cl_analyze.verify_file(args.analyze_input_file, guids=[], verbose=args.verbose)
        if args.analyze_compare_file:
            compare_stats, guids = cl_analyze.verify_file(args.analyze_compare_file, guids=[], verbose=args.verbose)
            # Print the differences between the two checklists stats in a table format
            print("INFO: Comparing the two checklists...")
            print("INFO: {0: <40} {1: <40} {2: <40}".format("Item", os.path.basename(args.analyze_input_file), os.path.basename(args.analyze_compare_file)))
            print("INFO: {0: <40} {1: <40} {2: <40}".format("----", "-" * len(os.path.basename(args.analyze_input_file)), "-" * len(os.path.basename(args.analyze_compare_file))))
            print("INFO: {0: <40} {1: <40} {2: <40}".format("Total items", file_stats['item_count'], compare_stats['item_count']))
            for key in file_stats['inconsistencies']:
                print("INFO: {0: <40} {1: <40} {2: <40}".format(key, file_stats['inconsistencies'][key], compare_stats['inconsistencies'][key]))
    # Otherwise, there should be an input folder
    elif args.analyze_input_folder:
        language = "en"  # This could be changed to a parameter
        if args.verbose:
            print("DEBUG: looking for JSON files in folder", args.analyze_input_folder, "with pattern *.", language + ".json...")
        checklist_files = glob.glob(args.analyze_input_folder + "/*." + language + ".json")
        if len(checklist_files) > 0:
            if args.verbose:
                print("DEBUG: found", len(checklist_files), "JSON files, analyzing correctness...")
            for file in checklist_files:
                if file:
                    file_stats, guids = cl_analyze.verify_file(file, guids=[], verbose=args.verbose)
        else:
            print("ERROR: no input file found, not doing anything")
    # If no input file or folder has been specified, show an error message
    else:
        print("ERROR: you need to use the parameters `--input-file` or `--input-folder` to specify the file or folder to analyze")
elif args.command == 'v12':
    # We need an input file and an output folder
    if args.v12_input_file and args.v12_output_folder:
        v2recos = cl_v1tov2.generate_v2(args.v12_input_file, verbose=args.verbose)
        cl_v1tov2.store_v2(args.v12_output_folder, v2recos, args.v12_output_format, verbose=args.verbose)
    else:
        print("ERROR: you need to use the parameters `--input-file` and `--output-folder` to specify the file to convert and the output folder")
else:
    print("ERROR: unknown command, please verify the command syntax with {0} --help".format(sys.argv[0]))
