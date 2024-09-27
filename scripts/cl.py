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
# Usage examples for v1-to-v2 conversion (use the --max-items parameter to limit the number of items to convert):
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists/aks_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./v2/recos --text-analytics-endpoint $text_endpoint --text-analytics-key $text_key --overwrite --source-type revcl --verbose 
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists/alz_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./v2/recos --output-format yaml --text-analytics-endpoint $text_endpoint --text-analytics-key $text_key --overwrite --source-type revcl --verbose
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists/waf_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./v2/recos --output-format yaml --text-analytics-endpoint $text_endpoint --text-analytics-key $text_key --overwrite --source-type revcl --verbose
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists-ext/aprl_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./v2/recos --text-analytics-endpoint $text_endpoint --text-analytics-key $text_key --overwrite --source-type aprl --verbose
# python3 ./scripts/cl.py v1tov2 --input-file ./checklists-ext/wafsg_checklist.en.json --service-dictionary ./scripts/service_dictionary.json --output-folder ./v2/recos --text-analytics-endpoint $text_endpoint --text-analytics-key $text_key --overwrite --source-type wafsg --verbose
#
# Usage examples for v2 analysis:
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --format yaml
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --format yaml --show-sources
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --format yaml --show-sources --source-selector revcl
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --format yaml --delete-assistant
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --format yaml --show-resource-types
#
# Usage examples for specific reco inspection:
# python3 ./scripts/cl.py show-reco --input-folder ./v2/recos --guid 1b1b1b1b-1b1b-1b1b-1b1b-1b1b1b1b1b1b
# python3 ./scripts/cl.py show-reco --input-folder ./v2/recos --name revcl-AzureSiteRecoveryMonitoringDisasterRecoveryService
# python3 ./scripts/cl.py open-reco --input-folder ./v2/recos --guid 1b1b1b1b-1b1b-1b1b-1b1b-1b1b1b1b1b1b
# python3 ./scripts/cl.py open-reco --input-folder ./v2/recos --name revcl-AzureSiteRecoveryMonitoringDisasterRecoveryService
#
# Validate reco files
# python3 ./scripts/cl.py validate-recos --input-folder ./v2/recos --schema ./v2/schema/recommendation.schema.json --verbose --max-items 10
# python3 ./scripts/cl.py validate-recos --input-folder ./v2/recos --schema ./v2/schema/recommendation.schema.json --verbose --max-findings 1
# python3 ./scripts/cl.py validate-recos --input-folder ./v2/recos --schema ./v2/schema/recommendation.schema.json --verbose
#
# Validate checklist files
# python3 ./scripts/cl.py validate-checklists --input-folder ./v2/checklists --schema ./v2/schema/checklist.schema.json --verbose
#
# Disambiguate names
# python3 ./scripts/cl.py disambiguate-names --input-folder ./v2/recos --verbose
#
# Usage examples for v2 reco listing:
# python3 ./scripts/cl.py list-recos --input-folder ./v2/recos --format yaml --label-selector '{"checklist": "alz"}' --show-labels
# python3 ./scripts/cl.py list-recos --input-folder ./v2/recos --format yaml --source-selector 'aprl'
# python3 ./scripts/cl.py list-recos --input-folder ./v2/recos --format yaml --with-arg
# python3 ./scripts/cl.py list-recos --input-folder ./v2/recos --checklist-file ./v2/checklists/alz.yaml --verbose
# python3 ./scripts/cl.py list-recos --input-folder ./v2/recos --checklist-file ./v2/checklists/alz.yaml --only-filenames
#
# Usage examples for renaming:
# python3 ./scripts/cl.py rename-reco --input-folder ./v2/recos --guid 1b1b1b1b-1b1b-1b1b-1b1b-1b1b1b1b1b1b
#
# Usage examples for updating recos:
# python3 ./scripts/cl.py update-recos --input-folder ./v2/recos --reviewed --verbose
# python3 ./scripts/cl.py update-recos --input-folder ./v2/recos --default-severity 1 --verbose
#
# Create a v2 checklist file out of a v1 checklist file:
# python3 ./scripts/cl.py checklist-to-v2 --checklist-file .\checklists\alz_checklist.en.json --output-file .\v2\checklists\alz.yaml --input-folder .\v2\recos --verbose
#
# Usage examples for analysis of checklist files:
# Analyze a single checklist file:
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --checklist-file ./v2/checklists/alz.yaml --verbose
# python3 ./scripts/cl.py analyze-v2 --input-folder ./v2/recos --checklist-file ./v2/checklists/alz.yaml --show-areas --verbose
# python3 ./scripts/cl.py list-recos --input-folder ./v2/recos --checklist-file ./v2/checklists/alz.yaml --verbose
#
# Export v2 checklist to v1 JSON format:
# python3 ./scripts/cl.py export-checklist --input-folder ./v2/recos --service-dictionary ./scripts/service_dictionary.json --checklist-file ./v2/checklists/alz.yaml --output-file ./v2/checklists/alz.json
# python3 ./scripts/cl.py export-checklist --input-folder ./v2/recos --service-dictionary ./scripts/service_dictionary.json --checklist-file ./v2/checklists/app_delivery.yaml --output-file ./v2/checklists/app_delivery.json
#
# Appendix: importing latest rules from APRL and WAF service guides (maybe useful before using v1-to-v2):
# python3 ./.github/actions/get_aprl/entrypoint.py './checklists-ext/aprl_checklist.en.json' 'true'
# python3 ./.github/actions/get_service_guides/entrypoint.py 'Azure Kubernetes Service, Azure Firewall, Azure ExpressRoute, Azure Application Gateway, Azure Front Door, App Service Web Apps, Azure Blob Storage, Azure Cosmos DB, Azure Files, Azure Machine Learning, Azure OpenAI, Virtual Machines' './checklists-ext' 'true'
# Last updated: July 2024
#
#################################################################################

import json
import yaml
import argparse
import sys
import glob
import os
import jsonschema
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
analyzev2_parser.add_argument('--show-sources', dest='analyzev2_show_sources', action='store_true',
                    default=False,
                    help='show all source types and its number of items (default: False)')
analyzev2_parser.add_argument('--show-severities', dest='analyzev2_show_severities', action='store_true',
                    default=False,
                    help='show all severities and its number of items (default: False)')
analyzev2_parser.add_argument('--show-resource-types', dest='analyzev2_show_resourceTypes', action='store_true',
                    default=False,
                    help='show all resource types and its number of items (default: False)')
analyzev2_parser.add_argument('--show-areas', dest='analyzev2_show_areas', action='store_true',
                    default=False,
                    help='show areas and subareas and its number of items (default: False)')
analyzev2_parser.add_argument('--label-selector', dest='analyzev2_labels', metavar='LABELS', action='store',
                    help='label selector for the items to analyze, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
analyzev2_parser.add_argument('--service-selector', dest='analyzev2_services', metavar='SERVICES', action='store',
                    help='comma-separated services for the items to analyze, for example "AKS,firewall"')
analyzev2_parser.add_argument('--waf-selector', dest='analyzev2_waf_pillars', metavar='WAF_PILLARS', action='store',
                    help='comma-separated WAF pillars for the items to analyze, for example "cost,reliability"')
analyzev2_parser.add_argument('--source-selector', dest='analyzev2_sources', metavar='SOURCE', action='store',
                    help='comma-separated source types for the items to analyze, for example "aprl,internal,wafsg"')
analyzev2_parser.add_argument('--checklist-file', dest='analyzev2_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='YAML file with a checklist definition that can include label-selectors, service-selectors and WAF-selectors as well as other metadata')
analyzev2_parser.add_argument('--delete-assistant', dest='analyzev2_delete_assistant', action='store_true',
                    default=False,
                    help='run delete assistant to delete duplicate recos (default: False)')
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
getrecos_parser.add_argument('--source-selector', dest='getrecos_sources', metavar='SOURCE', action='store',
                    help='comma-separated source types for the items to retrieve, for example "aprl,internal,wafsg"')
getrecos_parser.add_argument('--show-labels', dest='getrecos_show_labels', action='store_true',
                    default=False, help='show labels (default: False)')
getrecos_parser.add_argument('--show-arg', dest='getrecos_show_arg', action='store_true',
                    default=False, help='show Azure Resource Graph queries (default: False)')
getrecos_parser.add_argument('--with-arg', dest='getrecos_arg', action='store_true',
                    default=False, help='only return queries with ARG queries (default: False)')
getrecos_parser.add_argument('--checklist-file', dest='getrecos_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='YAML file with a checklist definition that can include label-selectors, service-selectors and WAF-selectors as well as other metadata')
getrecos_parser.add_argument('--only-filenames', dest='getrecos_only_filenames', action='store_true',
                    default=False, help='only show the reco filenames (default: False)')
# Create the 'update-recos' command
updaterecos_parser = subparsers.add_parser('update-recos', help='Update recommendations from a folder structure containing v2 recos', parents=[base_subparser])
updaterecos_parser.add_argument('--input-folder', dest='updaterecos_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='folder where the recommendations to update are stored')
updaterecos_parser.add_argument('--service-dictionary', dest='updaterecos_service_dictionary', metavar='SERVICE_DICTIONARY', action='store',
                    help='JSON file with dictionary to map services to standard names and to ARM services')
updaterecos_parser.add_argument('--format', dest='updaterecos_format', metavar='FORMAT', action='store',
                    default='yaml',
                    help='format of the v2 checklist items (default: yaml)')
updaterecos_parser.add_argument('--reviewed', dest='updaterecos_reviewed', action='store_true',
                    default=False, help='Set the reviewed field to the current date (default: False)')
updaterecos_parser.add_argument('--default-severity', dest='updaterecos_default_severity', metavar='DEFAULT_SEVERITY', action='store',
                    default='yaml', type=int,
                    help='Set any missing severity to the default value (default: None)')
# Create the 'validate-recos' command
validaterecos_parser = subparsers.add_parser('validate-recos', help='Validate recommendations to the reco schema', parents=[base_subparser])
validaterecos_parser.add_argument('--input-folder', dest='validaterecos_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='folder where the recommendations to update are stored')
validaterecos_parser.add_argument('--schema', dest='validaterecos_schema_file', metavar='SCHEMA_FILE', action='store',
                    help='file with validation schema')
validaterecos_parser.add_argument('--max-items', dest='validaterecos_max_items', metavar='MAX_ITEMS', action='store',
                    default=0, type=int,
                    help='Maximum number of items to validate, default is 0 (all items)')
validaterecos_parser.add_argument('--max-findings', dest='validaterecos_max_findings', metavar='MAX_FINDINGS', action='store',
                    default=0, type=int,
                    help='Maximum number of non-compliances to find, default is 0 (all non-compliances)')
# Create the 'validate-checklists' command
validatechecklists_parser = subparsers.add_parser('validate-checklists', help='Validate checklists to the reco schema', parents=[base_subparser])
validatechecklists_parser.add_argument('--input-folder', dest='validatechecklists_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='folder where the recommendations to update are stored')
validatechecklists_parser.add_argument('--schema', dest='validatechecklists_schema_file', metavar='SCHEMA_FILE', action='store',
                    help='file with validation schema')
validatechecklists_parser.add_argument('--max-items', dest='validatechecklists_max_items', metavar='MAX_ITEMS', action='store',
                    default=0, type=int,
                    help='Maximum number of items to validate, default is 0 (all items)')
validatechecklists_parser.add_argument('--max-findings', dest='validatechecklists_max_findings', metavar='MAX_FINDINGS', action='store',
                    default=0, type=int,
                    help='Maximum number of non-compliances to find, default is 0 (all non-compliances)')
# Create the 'show-reco' command
showreco_parser = subparsers.add_parser('show-reco', help='Show a specific recommendation', parents=[base_subparser])
showreco_parser.add_argument('--input-folder', dest='showreco_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations to show are stored')
showreco_parser.add_argument('--guid', dest='showreco_guid', metavar='GUID', action='store',
                    help='GUID of the recommendation to show')
showreco_parser.add_argument('--name', dest='showreco_name', metavar='NAME', action='store',
                    help='Name of the recommendation to show')
# Create the 'rename-reco' command
showreco_parser = subparsers.add_parser('rename-reco', help='Show a specific recommendation', parents=[base_subparser])
showreco_parser.add_argument('--input-folder', dest='renamereco_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations to rename are stored')
showreco_parser.add_argument('--guid', dest='renamereco_guid', metavar='GUID', action='store',
                    help='GUID of the recommendation to rename')
showreco_parser.add_argument('--new-name', dest='renamereco_newname', metavar='NEW_NAME', action='store',
                    help='new name for the recommendation. If not specified, you need to specify text analytics endpoint and key')
showreco_parser.add_argument('--text-analytics-endpoint', dest='renamereco_endpoint', metavar='ENDPOINT', action='store',
                    help='Text analytics endpoint to use for renaming')
showreco_parser.add_argument('--text-analytics-key', dest='renamereco_key', metavar='KEY', action='store',
                    help='Text analytics key to use for renaming')
# Create the 'open-reco' command
openreco_parser = subparsers.add_parser('open-reco', help='Open with a text editor a specific recommendation', parents=[base_subparser])
openreco_parser.add_argument('--input-folder', dest='openreco_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations to verify are stored')
openreco_parser.add_argument('--guid', dest='openreco_guid', metavar='GUID', action='store',
                    help='GUID of the recommendation to open')
openreco_parser.add_argument('--name', dest='openreco_name', metavar='NAME', action='store',
                    help='NAME of the recommendation to open')
openreco_parser.add_argument('--text-editor', dest='openreco_editor', metavar='GUID', action='store',
                    help='Text editor to use, for example "code" or "notepad"')
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
v12_parser.add_argument('--source-type', dest='v12_source_type', metavar='SOURCE_TYPE', action='store',
                    default=None,
                    help='Override source type with a specific value (default: None, possible options: revcl, wafsg, aprl)')
v12_parser.add_argument('--labels', dest='v12_labels', metavar='LABELS', action='store',
                    help='additional labels to add to the items, for example {"mykey1": "myvalue1", "mykey2": "myvalue2"}')
v12_parser.add_argument('--id-label', dest='v12_id_label', metavar='ID_LABEL', action='store',
                    help='label to use for the checklist ID, for example "alzId".')
v12_parser.add_argument('--category-label', dest='v12_cat_label', metavar='CATEGORY_LABEL', action='store',
                    help='label to use for the checklist categories, for example "alzArea".')
v12_parser.add_argument('--subcategory-label', dest='v12_subcat_label', metavar='SUBCATEGORY_LABEL', action='store',
                    help='label to use for the checklist subcategories, for example "alzSubarea".')
v12_parser.add_argument('--text-analytics-endpoint', dest='v12_text_endpoint', metavar='TEXT_ANALYTICS_ENDPOINT', action='store',
                    help='Text analytics endpoint to use for deriving missing reco names')
v12_parser.add_argument('--text-analytics-key', dest='v12_text_key', metavar='TEXT_ANALYTICS_KEY', action='store',
                    help='Text analytics key to use for deriving missing reco names')
v12_parser.add_argument('--overwrite', dest='v12_overwrite', action='store_true',
                    default=False,
                    help='overwrite existing reco files with the same GUID (default: False)')
v12_parser.add_argument('--max-items', dest='v12_max_items', metavar='SCHEMA_FILE', action='store',
                    default=0, type=int,
                    help='Maximum number of v1 recos to convert to v2, default is 0 (all items)')
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
export_parser = subparsers.add_parser('export-checklist', help='Exports a v2 checklist file (YAML) to a v1 format (JSON)', parents=[base_subparser])
export_parser.add_argument('--checklist-file', dest='export_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='YAML file with a checklist definition that can include label-selectors, service-selectors and WAF-selectors as well as other metadata')
export_parser.add_argument('--input-folder', dest='export_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations are stored')
export_parser.add_argument('--output-file', dest='export_output_file', metavar='OUTPUT_FILE', action='store',
                    help='output file where the v1 checklist will be stored')
export_parser.add_argument('--service-dictionary', dest='export_service_dictionary', metavar='SERVICE_DICTIONARY', action='store',
                    help='JSON file with dictionary to map services to standard names and to ARM services')
# Create the 'checklist-v1tov2' command
checklist_v12_parser = subparsers.add_parser('checklist-to-v2', help='Exports a v1 checklist file (JSON) to a checklist v2 format (YAML) including the required areas and selectors', parents=[base_subparser])
checklist_v12_parser.add_argument('--checklist-file', dest='checklist_v12_checklist_file', metavar='CHECKLIST_FILE', action='store',
                    help='JSON file with a v1 checklist definition')
checklist_v12_parser.add_argument('--output-file', dest='checklist_v12_output_file', metavar='OUTPUT_FILE', action='store',
                    help='output file where the v2 checklist will be stored')
checklist_v12_parser.add_argument('--use-names', dest='checklist_v12_use_names', action='store_true',
                    default=True,
                    help='use names instead of GUIDs (default: True)')
checklist_v12_parser.add_argument('--input-folder', dest='checklist_v12_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations are stored. This parameter is required if using names instead of GUIDs.')
# Create the 'disambiguate-names' command
disambiguate_names_parser = subparsers.add_parser('disambiguate-names', help='Exports a v1 checklist file (JSON) to a checklist v2 format (YAML) including the required areas and selectors', parents=[base_subparser])
disambiguate_names_parser.add_argument('--input-folder', dest='disambiguate_names_input_folder', metavar='INPUT_FOLDER', action='store',
                    help='input folder where the recommendations are stored.')

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
        # Create an array with the existing recos in the output folder
        existing_v2recos = cl_analyze_v2.load_v2_files(args.v12_output_folder, import_filepaths=True, verbose=False)
        if args.verbose: print("DEBUG: Found {0} existing v2 objects in folder {1}".format(len(existing_v2recos), args.v12_output_folder))
        # Generate v2 objects and store them in the output folder
        new_v2recos = cl_v1tov2.generate_v2(args.v12_input_file, service_dictionary=service_dictionary,
                                        text_analytics_endpoint=args.v12_text_endpoint, text_analytics_key=args.v12_text_key,
                                        labels=labels, id_label=args.v12_id_label, cat_label=args.v12_cat_label, subcat_label=args.v12_subcat_label,
                                        source_type=args.v12_source_type,
                                        existing_v2recos=existing_v2recos, max_items=args.v12_max_items,
                                        verbose=args.verbose)
        if new_v2recos:
            if args.verbose: print("DEBUG: Storing {0} v2 objects in folder {1}...".format(len(new_v2recos), args.v12_output_folder))
            cl_v1tov2.store_v2(args.v12_output_folder, new_v2recos, existing_v2recos=existing_v2recos, output_format=args.v12_output_format, overwrite=args.v12_overwrite, verbose=args.verbose)
        else:
            print("ERROR: No v2 objects generated, not storing anything.")
    else:
        print("ERROR: you need to use the parameters `--input-file` and `--output-folder` to specify the file to convert and the output folder")
elif args.command == 'analyze-v2':
    # We need an input folder
    if args.analyzev2_input_folder:
        # If a checklist file is specified, load the selectors from it
        if args.analyzev2_checklist_file:
            if (not (args.analyzev2_labels or args.analyzev2_services or args.analyzev2_waf_pillars)):
                v2_stats = cl_analyze_v2.v2_stats_from_checklist(args.analyzev2_checklist_file, args.analyzev2_input_folder, format=args.analyzev2_format, verbose=args.verbose)
            else:
                print("ERROR: You should either specify a checklist file or individual selectors, but not both.")
                sys.exit(1)
        else:
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
            if args.analyzev2_sources:
                sources = args.analyzev2_sources.lower().split(",")
            else:
                sources = None
            # Retrieve stats (with verbosity disabled)
            v2_stats = cl_analyze_v2.v2_stats_from_folder(args.analyzev2_input_folder, format=args.analyzev2_format, 
                                                        labels=labels, services=services, waf_pillars=waf_pillars, sources=sources,
                                                        verbose=False)
        if v2_stats:
            # Print stats
            print("INFO: Total items found =", v2_stats['total_items'])
            print("INFO: Duplicate GUIDs =", str(v2_stats['duplicate_guids']))
            print("INFO: Duplicate Names =", str(v2_stats['duplicate_names']))
            print("INFO: Recos with ARG queries =", str(v2_stats['arg']))
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
            if args.analyzev2_show_sources:
                print("INFO: Items per source:")
                for key in v2_stats['sources']:
                    print("INFO: - {0} = {1}".format(key, v2_stats['sources'][key]))
            if args.analyzev2_show_resourceTypes:
                print("INFO: Items per resource type:")
                for key in v2_stats['resourceTypes']:
                    print("INFO: - {0} = {1}".format(key, v2_stats['resourceTypes'][key]))
            if args.analyzev2_show_areas:
                print("INFO: Items per area | subarea:")
                for key in v2_stats['areas']:
                    print("INFO: - {0} = {1}".format(key, v2_stats['areas'][key]))
        else:
            print("ERROR: No v2 objects found.")
        if args.analyzev2_delete_assistant:
            print('WARNING: WIP!!')
            if args.verbose: print("DEBUG: Running delete assistant and loading up recos...")
            v2_recos = cl_analyze_v2.load_v2_files(args.analyzev2_input_folder, import_filepaths=True, verbose=False)
            for reco_name in v2_stats['duplicate_names']:
                recos = [x for x in v2_recos if x['name'].lower() == reco_name.lower()]
                if len(recos) > 1:
                    print("INFO: Found", len(recos), "duplicates for reco {0}:".format(reco_name))
                    for reco in recos:
                        print(json.dumps(reco, indent=2))
                print("QUESTION: which reco do you want to delete? (0-{0}/none) ".format(len(recos)-1), end='')
                answer = input()
                if answer.isnumeric():
                    reco_to_delete = recos[int(answer)]
                    print("INFO: Deleting reco {0} in file {1}...".format(reco_to_delete['name'], reco_to_delete['filepath']))
                    try:
                        os.remove(reco_to_delete['filepath'])
                    except Exception as e:
                        print("ERROR: Error deleting file", reco_to_delete['filepath'], "-", str(e))
    else:
        print("ERROR: you need to use the parameter `--input-folder` to specify the folder to analyze")
elif args.command == 'list-recos':
    # We need an input folder
    if args.getrecos_input_folder:
        if args.getrecos_checklist_file:
            # Get recos from the checklist file
            v2recos = cl_analyze_v2.get_recos_from_checklist( args.getrecos_checklist_file, args.getrecos_input_folder, verbose=args.verbose, import_filepaths=True)
        else:
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
            if args.getrecos_sources:
                sources = args.getrecos_sources.lower().split(",")
            else:
                sources = None
            # Retrieve recos
            v2recos = cl_analyze_v2.get_recos(args.getrecos_input_folder, 
                                            labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, format=args.getrecos_format, 
                                            arg=args.getrecos_arg, verbose=args.verbose)
        # Print recos
        if v2recos:
            if args.getrecos_only_filenames:
                for reco in v2recos:
                    print(reco['filepath'])
            else:
                cl_analyze_v2.print_recos(v2recos, show_labels=args.getrecos_show_labels, show_arg=args.getrecos_show_arg)
        else:
            print("ERROR: No v2 objects found satisfying the criteria.")
    else:
        print("ERROR: you need to use the parameter `--input-folder` to specify the folder to analyze")
elif args.command == 'update-recos':
    # We need an input folder
    if args.updaterecos_input_folder:
        # Retrieve recos
        if args.verbose: print("DEBUG: Retrieving recos from", args.updaterecos_input_folder)
        v2recos = cl_analyze_v2.get_recos(args.updaterecos_input_folder, format=args.updaterecos_format, import_filepaths=True, verbose=False)
        if v2recos and len(v2recos) > 0:
            updated_v2recos = []
            if args.updaterecos_reviewed:
                answer = input("\nDo you want to refresh the reviewed field in {0} recommendations? (Y/n) ".format(len(v2recos)))
                if (answer == "") or (answer.lower() == "y"):
                    updated_v2recos = cl_analyze_v2.refresh_reviewed(v2recos, verbose=args.verbose)
            if args.updaterecos_default_severity:
                for reco in v2recos:
                    if 'severity' not in reco:
                        if args.verbose: print("DEBUG: Setting default severity to {0} for reco {1}".format(args.updaterecos_default_severity, reco['name']))
                        reco['severity'] = args.updaterecos_default_severity
                        updated_v2recos.append(reco)
            if updated_v2recos and len(updated_v2recos) > 0:
                if args.verbose: print("DEBUG: Storing {0} updated v2 objects in folder {1}...".format(len(updated_v2recos), args.updaterecos_input_folder))
                cl_v1tov2.store_v2(args.updaterecos_input_folder, updated_v2recos, existing_v2recos=v2recos, overwrite=True, output_format=args.updaterecos_format, verbose=args.verbose)
            else:
                print("INFO: No v2 objects updated.")
        else:
            print("ERROR: No v2 objects found.")
    else:
        print("ERROR: you need to use the parameter `--input-folder` to specify the folder to analyze")
elif args.command == 'validate-recos':
    # We need an input folder and a schema file
    if args.validaterecos_input_folder and args.validaterecos_schema_file:
        # Retrieve recos and schema
        if args.verbose: print("DEBUG: Loading schema from", args.validaterecos_schema_file)
        with open(args.validaterecos_schema_file, 'r') as stream:
            try:
                reco_schema = json.load(stream)
            except:
                print("ERROR: Error loading JSON schema from", args.validaterecos_schema_file)
                sys.exit(1)
        # To Do: validate that the schema is valid
        if reco_schema:
            if args.verbose: print("DEBUG: Retrieving recos from", args.validaterecos_input_folder)
            v2recos = cl_analyze_v2.get_recos(args.validaterecos_input_folder, verbose=False)
            if args.verbose: print("DEBUG: Starting validation with schema {0}...".format(args.validaterecos_schema_file))
            reco_counter = 0
            finding_counter = 0
            for reco in v2recos:
                reco_counter +=1
                if (args.validaterecos_max_items == 0) or (reco_counter <= args.validaterecos_max_items):
                    try:
                        jsonschema.validate(reco, reco_schema)
                        if args.verbose: print("INFO: Reco", reco['name'], "validates correctly against the schema.")
                    except jsonschema.exceptions.ValidationError as e:
                        print("ERROR: Reco", reco['name'], "does not validate against the schema.")
                        if args.verbose: print("DEBUG: -", str(e))
                        finding_counter += 1
                        if (args.validaterecos_max_findings > 0) and (finding_counter >= args.validaterecos_max_findings):
                            print("INFO: Maximum number of non-compliances reached, stopping validation.")
                            break
                    except jsonschema.exceptions.SchemaError as e:
                        print("ERROR: Schema", args.validaterecos_schema_file, "does not seem to be valid.")
                        if args.verbose: print("DEBUG: -", str(e))
                        sys.exit(1)
                    except Exception as e:
                        print("ERROR: Unknown error validating reco", reco['name'], "against the schema", args.validaterecos_schema_file, "-", str(e))
            print("INFO: {0} recos validated, {1} non-compliances found.".format(reco_counter, finding_counter))
        else:
            print("ERROR: Schema could not be loaded.")
    else:
        print("ERROR: you need to use the parameters `--input-folder` and `--schema` to specify the recos folder and their schema")
elif args.command == 'validate-checklists':
    # We need an input folder and a schema file
    if args.validatechecklists_input_folder and args.validatechecklists_schema_file:
        # Retrieve checklists schema
        if args.verbose: print("DEBUG: Loading schema from", args.validatechecklists_schema_file)
        with open(args.validatechecklists_schema_file, 'r') as stream:
            try:
                cl_schema = json.load(stream)
            except:
                print("ERROR: Error loading JSON schema from", args.validatechecklists_schema_file)
                sys.exit(1)
        # Load checklists (every yaml in the folder)
        if cl_schema:
            if args.verbose: print("DEBUG: Retrieving checklists from", args.validatechecklists_input_folder)
            v2cls = cl_analyze_v2.get_checklists(args.validatechecklists_input_folder, verbose=False)
            if args.verbose: print("DEBUG: Starting validation with schema {0}...".format(args.validatechecklists_schema_file))
            cl_counter = 0
            finding_counter = 0
            for cl in v2cls:
                cl_counter +=1
                if (args.validatechecklists_max_items == 0) or (cl_counter <= args.validatechecklists_max_items):
                    try:
                        jsonschema.validate(cl, cl_schema)
                        if args.verbose: print("INFO: Checklist {0} validates correctly against the schema.".format(cl['name']))
                    except jsonschema.exceptions.ValidationError as e:
                        print("ERROR: Checklist '{0}' does not validate against the schema.".format(cl['name']))
                        if args.verbose: print("DEBUG: -", str(e))
                        finding_counter += 1
                        if (args.validatechecklists_max_findings > 0) and (finding_counter >= args.validatechecklists_max_findings):
                            print("INFO: Maximum number of non-compliances reached, stopping validation.")
                            break
                    except jsonschema.exceptions.SchemaError as e:
                        print("ERROR: Schema", args.validatechecklists_schema_file, "does not seem to be valid.")
                        if args.verbose: print("DEBUG: -", str(e))
                        sys.exit(1)
                    except Exception as e:
                        print("ERROR: Unknown error validating checklist '{0}' against the schema {1}: {2}".format(cl['name'], args.validatechecklists_schema_file,str(e)))
            print("INFO: {0} recos validated, {1} non-compliances found.".format(cl_counter, finding_counter))
        else:
            print("ERROR: Schema could not be loaded.")
    else:
        print("ERROR: you need to use the parameters `--input-folder` and `--schema` to specify the recos folder and their schema")
elif args.command == 'show-reco':
    # We need an input folder and a GUID or a name
    if args.showreco_input_folder and args.showreco_guid:
        recos = cl_analyze_v2.get_reco_from_guid(args.showreco_input_folder, args.showreco_guid, verbose=args.verbose)
    elif args.showreco_input_folder and args.showreco_name:
        recos = cl_analyze_v2.get_reco_from_name(args.showreco_input_folder, args.showreco_name, verbose=args.verbose)
    else:
        print("ERROR: you need to use the parameters `--input-folder` and `--guid` or `--name` to specify the folder and GUID/name to retrieve")
    if recos:
        if len(recos) > 1:
            print("WARNING: {0} recos found".format(len(recos)))
        for reco in recos:
            cl_analyze_v2.print_reco(reco)
            print("---")
    else:
        print("ERROR: No reco found with GUID", args.showreco_guid)
elif args.command == 'rename-reco':
    # We need an input folder and a GUID
    if args.renamereco_input_folder and args.renamereco_guid:
        recos = cl_analyze_v2.get_reco(args.renamereco_input_folder, args.renamereco_guid, verbose=args.verbose)
        if recos:
            if len(recos) > 1:
                print("ERROR: {0} recos found with GUID {1}".format(len(recos), args.showreco_guid))
            else:
                for reco in recos:
                    if args.renamereco_newname:
                        # WIP!!!
                        new_name = args.renamereco_newname
                    else:
                        new_name = cl_v1tov2.guess_reco_name(reco, cognitive_services_endpoint=args.renamereco_endpoint, cognitive_services_key=args.renamereco_key , verbose=args.verbose)
                    reco['name'] = new_name
                    cl_v1tov2.store_v2(args.renamereco_input_folder, [reco], output_format='yaml', verbose=args.verbose)
                    print("---")
        else:
            print("ERROR: No reco found with GUID", args.showreco_guid)
    else:
        print("ERROR: you need to use the parameters `--input-folder` and `--guid` to specify the folder and GUID to analyze")
elif args.command == 'open-reco':
    # We need an input folder and a GUID
    if args.openreco_input_folder and args.openreco_guid:
        cl_analyze_v2.load_v2_files(args.openreco_input_folder, guids=[ args.openreco_guid ], open_editor=True, text_editor=args.openreco_editor, verbose=args.verbose)
    elif args.openreco_input_folder and args.openreco_name:
        cl_analyze_v2.load_v2_files(args.openreco_input_folder, names=[ args.openreco_name ], open_editor=True, text_editor=args.openreco_editor, verbose=args.verbose)
    else:
        print("ERROR: you need to use the parameters `--input-folder` and `--guid` to specify the folder and GUID to open")
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
        if args.export_service_dictionary:
            try:
                if args.verbose: print("DEBUG: Loading service dictionary from", args.export_service_dictionary)
                with open(args.export_service_dictionary) as f:
                    service_dictionary = json.load(f)
                    if args.verbose: print("DEBUG: service dictionary loaded successfully with {0} elements".format(len(service_dictionary)))
            except Exception as e:
                service_dictionary = None
                print("ERROR: Error when loading service dictionary from", args.export_service_dictionary, "-", str(e))
                sys.exit(1)
        else:
            print("WARNING: you may want to use the parameter `--service-dictionary` to extract human-readable service names from ARM resource types.")
            service_dictionary = None
        cl_v2tov1.generate_v1(args.export_checklist_file, args.export_input_folder, args.export_output_file, service_dictionary=service_dictionary, verbose=args.verbose)
    else:
        print("ERROR: you need to use the parameters `--checklist-file` and `--input-folder` to specify the checklist file and the input folder")
elif args.command == "checklist-to-v2":
    if args.checklist_v12_checklist_file and args.checklist_v12_output_file:
        cl_v1tov2.checklist_v1_to_v2(args.checklist_v12_checklist_file, args.checklist_v12_output_file,
                                     use_names=args.checklist_v12_use_names, v2recos_folder=args.checklist_v12_input_folder, 
                                     verbose=args.verbose)
    else:
        print("ERROR: you need to use the parameters `--checklist-file` and `--output-file` to specify the v1 checklist file and the v2 output file")
elif args.command == 'disambiguate-names':
    # We need an input folder
    if args.disambiguate_names_input_folder:
        if args.verbose: print("DEBUG: loading up recos from folder", args.disambiguate_names_input_folder)
        v2_recos = cl_analyze_v2.get_recos(args.disambiguate_names_input_folder, verbose=False)
        if args.verbose: print("DEBUG: getting statistics", args.disambiguate_names_input_folder)
        v2_stats = cl_analyze_v2.v2_stats_from_object(v2_recos, verbose=args.verbose)
        if 'duplicate_names' in v2_stats:
            if args.verbose: print("DEBUG: Disambiguating {0} duplicate names".format(len(v2_stats['duplicate_names'])))
            print("INFO: Found {0} duplicate names".format(len(v2_stats['duplicate_names'])))
            for name in v2_stats['duplicate_names']:
                matching_recos = [reco for reco in v2_recos if reco['name'] == name]
                suffix = 1
                if len(matching_recos) > 1:
                    if args.verbose: print("DEBUG: Found {0} recos with name {1}".format(len(matching_recos), name))
                    for reco in matching_recos:
                        reco['name'] = name + "-" + str(suffix)
                        suffix += 1
                    # Store new recos
                    cl_v1tov2.store_v2(args.disambiguate_names_input_folder, matching_recos, overwrite=True, output_format='yaml', verbose=args.verbose)
                else:
                    print("ERROR: Found only {0} reco with name {1}".format(len(matching_recos), name))
    else:
        print("ERROR: You need to specify an input folder.")
        sys.exit(1)
else:
    print("ERROR: unknown command, please verify the command syntax with {0} --help".format(sys.argv[0]))
