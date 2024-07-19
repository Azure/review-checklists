#################################################################################
#
# This is the checklists CLI. It is a command-line interface that allows users to
#    perform various operations on checklists.
#
# Supported commands:
# - analyze-v1: Analyze a checklist
# - analyze-v2: Analyze a folder structure containing v2 recommendations
# - list-recos: List recommendations from a folder structure containing v2 recommendations
# - show-reco: Show a specific recommendation
# - v1tov2: Convert a v1 checklist to v2
# - run-arg: Run Azure Resource Graph queries stored in v2 recommendations
# 
# Usage examples for v1-to-v2 conversion:
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists/aks_checklist.en.json --output-folder ./recos-v2 --overwrite
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists/alz_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./recos-v2 --output-format yaml --labels '{"checklist": "alz"}' --id-label alzId --category-label alzArea --subcategory-label alzSubarea --overwrite
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists-ext/aprl_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./recos-v2
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists-ext/wafsg_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./recos-v2
#
# Usage examples for v2 analysis:
# python3 ./scripts/cl.py analyze-v2 --input-folder ./recos-v2 --format yaml --show-services
# python3 ./scripts/cl.py analyze-v2 --input-folder ./recos-v2 --format yaml --checklist-file .\checklists-v2\alz.yaml
#
# Usage examples for v2 reco listing:
# python3 ./scripts/cl.py list-recos --input-folder ./recos-v2 --format yaml --label-selector '{"checklist": "alz"}' --show-labels
# python3 ./scripts/cl.py list-recos --input-folder ./recos-v2 --format yaml --label-selector '{"source": "aprl"}' --show-labels
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
from modules import cl_analyze_v1
from modules import cl_v1tov2
from modules import cl_analyze_v2
from modules import cl_arg
from modules import cl_v2tov1

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
                    help='folder where the recommendations to verify are stored')
analyzev2_parser.add_argument('--format', dest='analyzev2_format', metavar='FORMAT', action='store',
                    default='yaml',
                    help='format of the v2 checklist items (default: yaml)')
analyzev2_parser.add_argument('--show-labels', dest='analyzev2_show_labels', action='store_true',
                    default=False,
                    help='show all labels and its number of items (default: False)')
analyzev2_parser.add_argument('--show-services', dest='analyzev2_show_services', action='store_true',
                    default=False,
                    help='show all services and its number of items (default: False)')
analyzev2_parser.add_argument('--show-waf', dest='analyzev2_show_waf', action='store_true',
                    default=False,
                    help='show all services and its number of items (default: False)')
analyzev2_parser.add_argument('--show-severities', dest='analyzev2_show_severities', action='store_true',
                    default=False,
                    help='show all severities and its number of items (default: False)')
analyzev2_parser.add_argument('--label-selector', dest='analyzev2_labels', metavar='LABELS', action='store',
                    help='label selector for the items to analyze, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
analyzev2_parser.add_argument('--service-selector', dest='analyzev2_services', metavar='SERVICES', action='store',
                    help='comma-separated services for the items to analyze, for example "AKS,firewall"')
analyzev2_parser.add_argument('--waf-selector', dest='analyzev2_waf_pillars', metavar='WAF_PILLARS', action='store',
                    help='comma-separated WAF pillars for the items to analyze, for example "cost,reliability"')
analyzev2_parser.add_argument('--checklist-file', dest='analyzev2_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='YAML file with a checklist definition that can include label-selectors, service-selectors and WAF-selectors as well as other metadata')
# Create the 'list-recos' command
getrecos_parser = subparsers.add_parser('list-recos', help='List recommendations from a folder structure containing v2 recos', parents=[base_subparser])
getrecos_parser.add_argument('--input-folder', dest='getrecos_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='folder where the recommendations to verify are stored')
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
getrecos_parser.add_argument('--show-arg', dest='getrecos_show_arg', action='store_true',
                    default=False, help='show Azure Resource Graph queries (default: False)')
getrecos_parser.add_argument('--with-arg', dest='getrecos_arg', action='store_true',
                    default=False, help='only return queries with ARG queries (default: False)')
getrecos_parser.add_argument('--checklist-file', dest='getrecos_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='YAML file with a checklist definition that can include label-selectors, service-selectors and WAF-selectors as well as other metadata')
# Create the 'show-reco' command
showreco_parser = subparsers.add_parser('show-reco', help='Show a specific recommendation', parents=[base_subparser])
showreco_parser.add_argument('--input-folder', dest='showreco_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations to verify are stored')
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
                    help='label to use for the checklist ID, for example "alzId".')
v12_parser.add_argument('--category-label', dest='v12_cat_label', metavar='CATEGORY_LABEL', action='store',
                    help='label to use for the checklist categories, for example "alzArea".')
v12_parser.add_argument('--subcategory-label', dest='v12_subcat_label', metavar='SUBCATEGORY_LABEL', action='store',
                    help='label to use for the checklist subcategories, for example "alzSubarea".')
v12_parser.add_argument('--overwrite', dest='v12_overwrite', action='store_true',
                    default=False,
                    help='overwrite existing reco files with the same GUID (default: False)')
# Create the 'run-arg' command
runarg_parser = subparsers.add_parser('run-arg', help='Run Azure Resource Graph queries stored in v2 recommendations', parents=[base_subparser])
runarg_parser.add_argument('--input-folder', dest='runarg_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the checks to run are stored')
runarg_parser.add_argument('--format', dest='runarg_format', metavar='FORMAT', action='store',
                    default='yaml',
                    help='format of the v2 checklist items (default: yaml)')
runarg_parser.add_argument('--label-selector', dest='runarg_labels', metavar='LABELS', action='store',
                    help='label selector for the items to run the queries from, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
runarg_parser.add_argument('--service-selector', dest='runarg_services', metavar='SERVICES', action='store',
                    help='comma-separated services for the items to run the queries from, for example "AKS,firewall"')
runarg_parser.add_argument('--waf-selector', dest='runarg_waf_pillars', metavar='WAF_PILLARS', action='store',
                    help='comma-separated WAF pillars for the items to run the queries from, for example "cost,reliability"')
runarg_parser.add_argument('--guid', dest='runarg_guid', metavar='GUID', action='store',
                    help='GUID of the recommendation to run the queries from')
runarg_parser.add_argument('--subscription-id', dest='runarg_subscription_id', metavar='SUBSCRIPTION_ID', action='store',
                    help='Azure subscription ID where to run the queries')
# Create the 'export-checklist' command
export_parser = subparsers.add_parser('export-checklist', help='Show a specific recommendation', parents=[base_subparser])
export_parser.add_argument('--checklist-file', dest='export_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='YAML file with a checklist definition that can include label-selectors, service-selectors and WAF-selectors as well as other metadata')
export_parser.add_argument('--input-folder', dest='export_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations are stored')
export_parser.add_argument('--output-file', dest='export_output_file', metavar='OUTPUT_FILE', action='store',
                    help='output file where the v1 checklist will be stored')


# Parse the command-line arguments
args = parser.parse_args()

# Handle the parsed arguments based on the command and sub-command
if args.command == 'analyze-v1':
    guids = []
    # We need an input file or an input folder
    if args.analyze_input_file:
        file_stats, guids = cl_analyze_v1.verify_file(args.analyze_input_file, guids=[], verbose=args.verbose)
        if args.analyze_compare_file:
            compare_stats, guids = cl_analyze_v1.verify_file(args.analyze_compare_file, guids=[], verbose=args.verbose)
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
                    file_stats, guids = cl_analyze_v1.verify_file(file, guids=[], verbose=args.verbose)
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
        v2recos = cl_v1tov2.generate_v2(args.v12_input_file, service_dictionary=service_dictionary, 
                                        labels=labels, id_label=args.v12_id_label, cat_label=args.v12_cat_label, subcat_label=args.v12_subcat_label,
                                        verbose=args.verbose)
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
        # Convert label selectors argument to an object if specified
        if args.analyzev2_labels:
            try:
                labels = json.loads(args.analyzev2_labels)
            except Exception as e:
                print("ERROR: Error when loading labels from", args.analyzev2_labels, "-", str(e))
                labels = None
        else:
            labels = None
        if args.analyzev2_services:
            services = args.analyzev2_services.lower().split(",")
        else:
            services = None
        if args.analyzev2_waf_pillars:
            waf_pillars = args.analyzev2_waf_pillars.lower().split(",")
        else:
            waf_pillars = None
        if args.analyzev2_checklist_file:
            if (not (labels or services or waf_pillars)):
                labels, services, waf_pillars = cl_analyze_v2.get_checklist_selectors(args.analyzev2_checklist_file)
            else:
                print("ERROR: You should either specify a checklist file or individual selectors, but not both.")
                sys.exit(1)
        # Retrieve stats
        v2_stats = cl_analyze_v2.v2_stats_from_folder(args.analyzev2_input_folder, format=args.analyzev2_format, 
                                                      labels=labels, services=services, waf_pillars=waf_pillars, 
                                                      verbose=args.verbose)
        # Print stats
        print("INFO: Total items found =", v2_stats['total_items'])
        if args.analyzev2_show_severities:
            print("INFO: Items per severity:")
            for key in v2_stats['severity']:
                print("INFO: - {0} = {1}".format(key, v2_stats['severity'][key]))
        if args.analyzev2_show_labels:
            print("INFO: Items per label:")
            for key in v2_stats['labels']:
                print("INFO: - {0} = {1}".format(key, v2_stats['labels'][key]))
        if args.analyzev2_show_services:
            print("INFO: Items per service:")
            for key in v2_stats['services']:
                print("INFO: - {0} = {1}".format(key, v2_stats['services'][key]))
        if args.analyzev2_show_waf:
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
        if args.getrecos_checklist_file:
            if (not (labels or services or waf_pillars)):
                labels, services, waf_pillars, variables = cl_analyze_v2.get_checklist_selectors(args.analyzev2_checklist_file)
            else:
                print("ERROR: You should either specify a checklist file or individual selectors, but not both.")
                sys.exit(1)
        # Retrieve recos
        v2recos = cl_analyze_v2.get_recos(args.getrecos_input_folder, 
                                          labels=labels, services=services, waf_pillars=waf_pillars, format=args.getrecos_format, 
                                          arg=args.getrecos_arg, verbose=args.verbose)
        # Print recos
        if v2recos:
            cl_analyze_v2.print_recos(v2recos, show_labels=args.getrecos_show_labels, show_arg=args.getrecos_show_arg)
        else:
            print("ERROR: No v2 objects found satisfying the criteria.")
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
elif args.command == 'run-arg':
    if args.runarg_input_folder:
        # Convert label selectors argument to an object if specified
        if args.runarg_labels:
            try:
                labels = json.loads(args.runarg_labels)
            except Exception as e:
                print("ERROR: Error when loading labels from", args.runarg_labels, "-", str(e))
                labels = None
        else:
            labels = None
        if args.runarg_services:
            services = args.runarg_services.lower().split(",")
        else:
            services = None
        if args.runarg_waf_pillars:
            waf_pillars = args.runarg_waf_pillars.lower().split(",")
        else:
            waf_pillars = None
        v2recos = cl_analyze_v2.get_recos(args.runarg_input_folder, labels=labels, services=services, waf_pillars=waf_pillars, guid=args.runarg_guid, format=args.runarg_format, verbose=args.verbose)
        if v2recos:
            arg_results = cl_arg.run_arg_queries(v2recos, subscription_id=args.runarg_subscription_id, verbose=args.verbose)
            for result in arg_results:
                print("INFO: ARG query result for reco with GUID", result['guid'])
                print("INFO: - {0}".format(result['argResult']))
        else:
            print("ERROR: No v2 objects found.")
elif args.command == "export-checklist":
    if args.export_checklist_file and args.export_input_folder:
        cl_v2tov1.generate_v1(args.export_checklist_file, args.export_input_folder, args.export_output_file, verbose=args.verbose)
    else:
        print("ERROR: you need to use the parameters `--checklist-file` and `--input-folder` to specify the checklist file and the input folder")
else:
    print("ERROR: unknown command, please verify the command syntax with {0} --help".format(sys.argv[0]))
