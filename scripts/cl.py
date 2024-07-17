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
import yaml
import argparse
import sys
import glob
import os
from modules import cl_analyze
from modules import cl_v1tov2
from modules import cl_analyze_v2

# Get input arguments
parser = argparse.ArgumentParser(description='Checklists CLI', prog='checklists')
subparsers = parser.add_subparsers(dest='command', help='Command help')
# Define common shared arguments
base_subparser = argparse.ArgumentParser(add_help=False)
base_subparser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
# Create the 'analyze-v1' command
analyze_parser = subparsers.add_parser('analyze-v1', help='Analyze a v1 checklist', parents=[base_subparser])
analyze_parser.add_argument('--input-file', dest='analyze_input_file', metavar= 'INPUT_FILE', action='store',
                    help='name of the JSON file with the checklist to be analyzed')
analyze_parser.add_argument('--compare-file', dest='analyze_compare_file', metavar='COMPARE_FILE', action='store',
                    help='you can optionally supply the name of the JSON file with a second checklist to be compared against the first one')
analyze_parser.add_argument('--input-folder', dest='analyze_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='if no input file has been specified, input folder where the checklists to verify are stored')
# Create the 'analyze-v2' command
analyzev2_parser = subparsers.add_parser('analyze-v2', help='Analyze a folder structure containing v2 recos', parents=[base_subparser])
analyzev2_parser.add_argument('--input-folder', dest='analyzev2_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='if no input file has been specified, input folder where the checklists to verify are stored')
analyzev2_parser.add_argument('--format', dest='analyzev2_format', metavar='FORMAT', action='store',
                    default='yaml',
                    help='format of the v2 checklist items (default: yaml)')
analyzev2_parser.add_argument('--show-labels', dest='analyzev2_labels', action='store_true',
                    default=False,
                    help='show all labels and its number of items (default: False)')
analyzev2_parser.add_argument('--show-services', dest='analyzev2_services', action='store_true',
                    default=False,
                    help='show all services and its number of items (default: False)')
analyzev2_parser.add_argument('--show-waf', dest='analyzev2_waf', action='store_true',
                    default=False,
                    help='show all services and its number of items (default: False)')
analyzev2_parser.add_argument('--show-severities', dest='analyzev2_severities', action='store_true',
                    default=False,
                    help='show all severities and its number of items (default: False)')
analyzev2_parser.add_argument('--label-selector', dest='analyzev2_labels', metavar='LABELS', action='store',
                    help='label selector for the items to analyze, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
analyzev2_parser.add_argument('--service-selector', dest='analyzev2_services', metavar='SERVICES', action='store',
                    help='comma-separated services for the items to analyze, for example "AKS,firewall"')
analyzev2_parser.add_argument('--waf-selector', dest='analyzev2_waf_pillars', metavar='WAF_PILLARS', action='store',
                    help='comma-separated WAF pillars for the items to analyze, for example "cost,reliability"')
# Create the 'list-recos' command
getrecos_parser = subparsers.add_parser('list-recos', help='List recommendations from a folder structure containing v2 recos', parents=[base_subparser])
getrecos_parser.add_argument('--input-folder', dest='getrecos_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='if no input file has been specified, input folder where the checklists to verify are stored')
getrecos_parser.add_argument('--format', dest='getrecos_format', metavar='FORMAT', action='store',
                    default='yaml',
                    help='format of the v2 checklist items (default: yaml)')
getrecos_parser.add_argument('--label-selector', dest='getrecos_labels', metavar='LABELS', action='store',
                    help='label selector for the items to retrieve, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
getrecos_parser.add_argument('--service-selector', dest='getrecos_services', metavar='SERVICES', action='store',
                    help='comma-separated services for the items to retrieve, for example "AKS,firewall"')
getrecos_parser.add_argument('--waf-selector', dest='getrecos_waf_pillars', metavar='WAF_PILLARS', action='store',
                    help='comma-separated WAF pillars for the items to retrieve, for example "cost,reliability"')
getrecos_parser.add_argument('--show-labels', dest='getrecos_show_labels', action='store_true',
                    default=False, help='show labels (default: False)')
# Create the 'show-reco' command
showreco_parser = subparsers.add_parser('show-reco', help='Show a specific recommendation', parents=[base_subparser])
showreco_parser.add_argument('--input-folder', dest='showreco_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the checklists to verify are stored')
showreco_parser.add_argument('--guid', dest='showreco_guid', metavar='GUID', action='store',
                    help='GUID of the recommendation to show')
# Create the 'v1tov2' command
v12_parser = subparsers.add_parser('v1tov2', help='Convert v1 to v2', parents=[base_subparser])
v12_parser.add_argument('--input-file', dest='v12_input_file', metavar='INPUT_FILE', action='store',
                    help='name of the JSON file with the v1 checklist to be converted to v2'),
v12_parser.add_argument('--service-dictionary', dest='v12_service_dictionary', metavar='SERVICE_DICTIONARY', action='store',
                    help='JSON file with dictionary to map services to standard names and to ARM services')
v12_parser.add_argument('--output-folder', dest='v12_output_folder', metavar='OUTPUT_FOLDER', action='store',
                    help='output folder where the v2 checklist items will be stored')
v12_parser.add_argument('--output-format', dest='v12_output_format', metavar='OUTPUT_FORMAT', action='store',
                    default='yaml',
                    help='output format of the v12 checklist items (default: yaml)')
v12_parser.add_argument('--labels', dest='v12_labels', metavar='LABELS', action='store',
                    help='additional labels to add to the items, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
v12_parser.add_argument('--id-label', dest='v12_id_label', metavar='ID_LABEL', action='store',
                    help='label to use for the checklist ID, for example "alzid".')
v12_parser.add_argument('--overwrite', dest='v12_overwrite', action='store_true',
                    default=False,
                    help='overwrite existing reco files with the same GUID (default: False)')

# Parse the command-line arguments
args = parser.parse_args()

# Handle the parsed arguments based on the command and sub-command
if args.command == 'analyze-v1':
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
elif args.command == 'v1tov2':
    # We need an input file and an output folder
    if args.v12_input_file and args.v12_output_folder:
        # Load service dictionary if provided
        if args.v12_service_dictionary:
            try:
                if args.verbose: print("DEBUG: Loading service dictionary from", args.v12_service_dictionary)
                with open(args.v12_service_dictionary) as f:
                    service_dictionary = json.load(f)
                    if args.verbose: print("DEBUG: service dictionary loaded successfully with {0} elements".format(len(service_dictionary)))
            except Exception as e:
                service_dictionary = None
                print("ERROR: Error when loading service dictionary from", args.v12_service_dictionary, "-", str(e))
        else:
            service_dictionary = None
        # Convert labels argument to object if specified
        if args.v12_labels:
            try:
                labels = json.loads(args.v12_labels)
                if isinstance(labels, dict):
                    if args.verbose: print("DEBUG: Loaded {0} labels".format(len(labels)))
                else:
                    print("ERROR: Labels should be a dictionary, not a", type(labels))
                    labels = None
            except Exception as e:
                print("ERROR: Error when loading labels from", args.v12_labels, "-", str(e))
                labels = None
        else:
            labels = None
        # Generate v2 objects and store them in the output folder
        v2recos = cl_v1tov2.generate_v2(args.v12_input_file, service_dictionary=service_dictionary, labels=labels, id_label=args.v12_id_label, verbose=args.verbose)
        if v2recos:
            if args.verbose: print("DEBUG: Storing {0} v2 objects in folder {1}...".format(len(v2recos), args.v12_output_folder))
            cl_v1tov2.store_v2(args.v12_output_folder, v2recos, output_format=args.v12_output_format, overwrite=args.v12_overwrite, verbose=args.verbose)
        else:
            print("ERROR: No v2 objects generated, not storing anything.")
    else:
        print("ERROR: you need to use the parameters `--input-file` and `--output-folder` to specify the file to convert and the output folder")
elif args.command == 'analyze-v2':
    # We need an input folder
    if args.analyzev2_input_folder:
        v2_stats = cl_analyze_v2.v2_stats_from_folder(args.analyzev2_input_folder, format=args.analyzev2_format, 
                                                      labels=args.analyzev2_labels, services=args.analyzev2_services, waf_pillars=args.analyzev2_waf_pillars, 
                                                      verbose=args.verbose)
        print("INFO: Total items found =", v2_stats['total_items'])
        if args.analyzev2_severities:
            print("INFO: Items per severity:")
            for key in v2_stats['severity']:
                print("INFO: - {0} = {1}".format(key, v2_stats['severity'][key]))
        if args.analyzev2_labels:
            print("INFO: Items per label:")
            for key in v2_stats['labels']:
                print("INFO: - {0} = {1}".format(key, v2_stats['labels'][key]))
        if args.analyzev2_services:
            print("INFO: Items per service:")
            for key in v2_stats['services']:
                print("INFO: - {0} = {1}".format(key, v2_stats['services'][key]))
        if args.analyzev2_waf:
            print("INFO: Items per WAF pillar:")
            for key in v2_stats['waf']:
                print("INFO: - {0} = {1}".format(key, v2_stats['waf'][key]))
    else:
        print("ERROR: you need to use the parameter `--input-folder` to specify the folder to analyze")
elif args.command == 'list-recos':
    # We need an input folder
    if args.getrecos_input_folder:
        # Convert label selectors argument to an object if specified
        if args.getrecos_labels:
            try:
                labels = json.loads(args.getrecos_labels)
            except Exception as e:
                print("ERROR: Error when loading labels from", args.getrecos_labels, "-", str(e))
                labels = None
        else:
            labels = None
        if args.getrecos_services:
            services = args.getrecos_services.lower().split(",")
        else:
            services = None
        if args.getrecos_waf_pillars:
            waf_pillars = args.getrecos_waf_pillars.lower().split(",")
        else:
            waf_pillars = None
        v2recos = cl_analyze_v2.get_recos(args.getrecos_input_folder, labels=labels, services=services, waf_pillars=waf_pillars, format=args.getrecos_format, verbose=args.verbose)
        if v2recos:
            cl_analyze_v2.print_recos(v2recos, show_labels=args.getrecos_show_labels)
        else:
            print("ERROR: No v2 objects found.")
    else:
        print("ERROR: you need to use the parameter `--input-folder` to specify the folder to analyze")
elif args.command == 'show-reco':
    # We need an input folder and a GUID
    if args.showreco_input_folder and args.showreco_guid:
        recos = cl_analyze_v2.get_reco(args.showreco_input_folder, args.showreco_guid, verbose=args.verbose)
        if recos:
            if len(recos) > 1:
                print("ERROR: {0} recos found with GUID {1}".format(len(recos), args.showreco_guid))
            else:
                for reco in recos:
                    yaml.dump(reco, sys.stdout, default_flow_style=False)
                    print("---")
        else:
            print("ERROR: No reco found with GUID", args.showreco_guid)
    else:
        print("ERROR: you need to use the parameters `--input-folder` and `--guid` to specify the folder and GUID to analyze")
else:
    print("ERROR: unknown command, please verify the command syntax with {0} --help".format(sys.argv[0]))
