# This scripts parses the WAF service guides and extracts the recommendations
#   for each service. The recommendations are stored in a dictionary and
#   can be compared to the recommendations in the WAF review checklist.
# Optionally a file is saved with the recommendations from the WAF svc guides 
#   in JSON format.
# Examples:
#   python ./scripts/entrypoint.py --service 'Azure Kubernetes Service' --output-checklist-folder ./checklists

import requests
# import argparse
import json
import re
import sys
import os
import datetime

# # Arguments
# parser = argparse.ArgumentParser(description='Retrieve recommendations in Azure Well-Architected Framework service guides')
# parser.add_argument('--service', dest='service', action='store',
#                     help='Optional service name to retrieve recommendations for (default: None)')
# parser.add_argument('--print-json', dest='print_json', action='store_true',
#                     default=False,
#                     help='Print the full JSON (default: False)')
# parser.add_argument('--extract-key-phrases-for-checklist', dest='extract_key_phrases_checklist', action='store_true',
#                     default=False,
#                     help='Extract key phrases for each recommendation found in the WAF review checklist (default: False)')
# parser.add_argument('--extract-key-phrases-for-svcguide', dest='extract_key_phrases_svcguide', action='store_true',
#                     default=False,
#                     help='Extract key phrases for each recommendation found in service guides (default: False)')
# parser.add_argument('--update-svcguide-recos', dest='update_svcguide_recos', action='store_true',
#                     default=False,
#                     help='Update the service guide recos in the input and output files (default: False)')
# parser.add_argument('--compare-recos', dest='compare_recos', action='store_true',
#                     default=False,
#                     help='Try to match checklist recos to each WAF service guide reco (default: False)')
# parser.add_argument('--key-phrases-only-if-empty', dest='key_phrases_only_if_empty', action='store_true',
#                     default=True,
#                     help='Only extract key phrases if there were none stored (default: True)')
# parser.add_argument('--text-analytics-endpoint', dest='text_analytics_endpoint', action='store',
#                     default='https://product-feedback.cognitiveservices.azure.com/',
#                     help='Optional endpoint of text analytics (default: https://product-feedback.cognitiveservices.azure.com/)')
# parser.add_argument('--text-analytics-key', dest='text_analytics_key', action='store',
#                     help='Key for text analytics endpoint (default: None)')
# parser.add_argument('--save-to-file', dest='save_filename', action='store',
#                     help='Save the recommendations in a local file (default: None)')
# parser.add_argument('--load-from-file', dest='load_filename', action='store',
#                     help='Load the recommendations from a local file (default: None)')
# parser.add_argument('--checklist-file', dest='checklist_filename', action='store',
#                     help='Filename with the review recommendations (default: None)')
# parser.add_argument('--output-checklist-folder', dest='output_checklist_folder', action='store',
#                     help='Path where output files in checklist format will be stored (default: None)')
# parser.add_argument('--verbose', dest='verbose', action='store_true',
#                     default=False,
#                     help='Run in verbose mode (default: False)')
# args = parser.parse_args()

# The script has been modified to be run from a github action with positional parameters
# 1. Output folder
# 2. Service (CSV supported)
# 3. Verbose
try:
    args_service = sys.argv[1].lower()
    if len(args_service) > 0:
        args_service_list = args_service.split(',')
        # Remove leading and trailing spaces
        args_service_list = [x.strip() for x in args_service_list]
except:
    args_service = ''
try:
    args_output_checklist_folder = sys.argv[2]
except:
    args_output_checklist_folder = './checklists'
try:
    args_verbose = (sys.argv[3].lower() == 'true')
except:
    args_verbose = True
# These parameters haven't been implemented in the github action
args_print_json = False
args_extract_key_phrases_checklist = False
args_extract_key_phrases_svcguide = False
args_update_svcguide_recos = False
args_compare_recos = False
args_key_phrases_only_if_empty = True
args_text_analytics_endpoint = 'https://product-feedback.cognitiveservices.azure.com/'
args_text_analytics_key = None
args_save_filename = None
args_load_filename = None
args_checklist_filename = None


# Function to store an object in a JSON file
def store_json(obj, filename):
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=4)

# Function to load an object from a JSON file
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Function to extract key phrases from recommendation
def extract_key_phrases(text, text_analytics_endpoint, text_analytics_key):
    try:
        # Set skeleton for text analytics request
        document_list = '[{"id": "1", "language": "en", "text": "' + text + '"}]'
        text_analytics_body_string = '{ "kind": "KeyPhraseExtraction", "parameters": { "modelVersion": "latest" }, "analysisInput": { "documents": ' + document_list + ' } }'
        # Send Text Analytics request
        text_analytics_url = f'{text_analytics_endpoint}language/:analyze-text?api-version=2023-04-01'
        text_analytics_headers = {
            'Ocp-Apim-Subscription-Key': text_analytics_key,
            'Content-Type': 'application/json'
            }
        r = requests.post(text_analytics_url, headers=text_analytics_headers, json=json.loads(text_analytics_body_string))
        if r.status_code == 200:
            return r.json()
        else:
            print("ERROR: Unable to retrieve key phrases from text analytics: {0}. Message: {1}".format(r.status_code, r.text))
            return None
    except Exception as e:
        print("ERROR: Exception in extract_key_phrases: {0}".format(str(e)))
        return None

# Function to extract key phrases for all recommendations
def extract_all_key_phrases(recos, text_analytics_endpoint, text_analytics_key):
    reco_counter=0
    for reco in recos:
        reco_counter += 1
        if (args_verbose):
            print("DEBUG: Extracting key phrases for recommendation '{0}'".format(reco['text']))
        else:
            sys.stdout.write('\rINFO: Extracting key phrases from recommendation %d of %d' % (reco_counter, len(recos)))
        if (args_key_phrases_only_if_empty and ('key_phrases' in reco) and (len(reco['key_phrases']) > 0)):
            if (args_verbose): print("DEBUG: Recommendation '{0}' already has key phrases".format(reco['text']))
        else:
            key_phrases = extract_key_phrases(reco['text'], text_analytics_endpoint, text_analytics_key)
            if key_phrases:
                # if (args_verbose): print("DEBUG: Key phrases extracted: {0}".format(str(key_phrases)))
                if 'results' in key_phrases:
                    reco['key_phrases'] = key_phrases['results']['documents'][0]['keyPhrases']
                else:
                    print("ERROR: Unable to extract key phrases from recommendation '{0}'. Text analytics answer: {1}".format(reco['text'], str(key_phrases)))
    if not args_verbose:
        print('')   # Otherwise the next print will be on the same line
    return recos


# Function to remove markdown formatting
def remove_markdown(markdown):
    # If the markdown contains strings with link formatting [text](url) we should only keep the text and throw away the URL
    markdown = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', markdown)
    markdown = markdown.replace('<br>', '')    # Remove <br> tags
    markdown = markdown.replace('**', '')    # Remove ** tags
    # Remove any asterisk enclosing a word
    markdown = re.sub(r'\*([^\*]+)\*', r'\1', markdown)
    # Remove trailing and leading spaces
    markdown = markdown.strip()
    # Go back
    return markdown

# Function that translates the WAF pillar to a short name
def short_pillar(pillar):
    pillar = pillar.lower()
    if (pillar == 'cost optimization'): return 'cost'
    elif (pillar == 'operational excellence'): return 'operations'
    elif (pillar == 'performance efficiency'): return 'performance'
    elif (pillar == 'reliability'): return 'reliability'
    elif (pillar == 'security'): return 'security'
    else: return pillar

# Function to parse markdown
def parse_markdown(markdown, service, verbose=False):
    recos = []
    waf_pillars = ['cost optimization', 'operational excellence', 'performance efficiency', 'reliability', 'security']
    processing_pillar = ''
    if (verbose): print("DEBUG: Processing markdown file...")
    line_count = 0
    for line in markdown.split('\n'):
        line_count += 1
        line = line.strip()
        if (line[0:3] == '## ') and (line[3:].lower() in waf_pillars):
            processing_pillar = short_pillar(line[3:])
            if (verbose): print("DEBUG: Processing pillar '{0}'".format(processing_pillar))
        if (line[0:4] == '> - ') and (processing_pillar != ''):
            reco = line[4:]
            recos.append({'waf': processing_pillar, 'service': service, 'text': remove_markdown(reco), 'description': '', 'type': 'checklist'})
        # If line matches a pattern that starts with "|" then comes a text, then "|" and a description and a closing "|"
        if (line[0:1] == '|'):
            line_table_items = line.split('|')
            if (len(line_table_items) == 4):
                if (len(line_table_items[1]) > 20) and (len(line_table_items[2]) > 20):     # We assume that long enough text and descriptions are valid
                    recos.append({'waf': processing_pillar.title(), 'service': service, 'text': remove_markdown(line_table_items[1]), 'description': remove_markdown(line_table_items[2]), 'type': 'recommendation'})
    if (verbose): print("DEBUG: {0} recommendations found in {1} lines".format(len(recos), line_count))
    return recos

# Function to get list of WAF service guides URLs
def get_waf_service_guide_recos():
    # Variables
    github_org = 'MicrosoftDocs'
    github_repo = 'well-architected'
    max_files = 0   # Maximum number of files to process. Set to 0 to process all files.
    retrieved_recos = []
    # Get last commit
    r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/commits')
    if (r.status_code == 200):
        commits = r.json()
        git_tree_id = commits[0]['commit']['tree']['sha']
        if (args_verbose): print("DEBUG: Git tree ID is", git_tree_id)
        r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/git/trees/{git_tree_id}?recursive=true')
        if r.status_code == 200:
            files_processed = 0
            for path in r.json()['tree']:
                file_path = path['path']
                # Only process markdown files in the well-architected/service-guides/ folder
                if ('well-architected/service-guides/' in file_path) and ('.md' in file_path) and (len(file_path.split('/')) == 3):
                    files_processed += 1
                    if (max_files > 0) and (files_processed > max_files):
                        print("INFO: Maximum number of files processed reached: {0}".format(max_files))
                        break
                    service = file_path.split('/')[2]
                    service = service.replace('.md', '')
                    service = service.replace('-', ' ')
                    service = service.title()
                    if (len(args_service) == 0) or (service.lower() in args_service_list):
                        if (args_verbose): print("DEBUG: Service {0} in service guide '{1}' matching input services '{2}'...".format(service, file_path, args_service))
                        svcguide_url = f'https://raw.githubusercontent.com/{github_org}/{github_repo}/main/' + file_path
                        if (args_verbose): print("DEBUG: Found service guide '{0}' for service '{1}'".format(file_path, service))
                        # if (args_verbose): print("DEBUG: Retrieving service guide from URL '{0}'...".format(svcguide_url))
                        r = requests.get(svcguide_url)
                        if r.status_code == 200:
                            svcguide = r.text
                            if (args_verbose): print("DEBUG: Parsing service guide '{0}', {1} characters retrieved...".format(file_path, len(svcguide)))
                            svc_recos = parse_markdown(svcguide, service, verbose=False)
                            if (len(svc_recos) > 0):
                                retrieved_recos += svc_recos
                                if args_verbose: print("DEBUG: {0} recommendations found for service '{1}'".format(len(svc_recos), service))
                        else:
                            print("ERROR: Unable to retrieve service guide from URL {0}".format(svcguide_url))
                    else:
                        if (args_verbose): print("DEBUG: Service {0} in service guide '{1}' does not match input services '{2}'...".format(service, file_path, args_service))
            return retrieved_recos
        else:
            print("ERROR: Unable to retrieve list of files from GitHub API")
            return None
    else:
        print("ERROR: Unable to retrieve list of commits from GitHub API: {0}. Message: {1}".format(r.status_code, r.text))
        return None

# Find the checklist reco that matches the most closely for each WAF reco
def compare_recos(waf_recos, checklist_recos, minimum_similarity=0.5):
    reco_counter = 0
    max_score = 0
    match_count = 0
    for waf_reco in waf_recos:
        reco_counter += 1
        if (args_verbose): print("DEBUG: Comparing recommendation number {1}: '{0}'".format(waf_reco['text'], reco_counter))
        best_match = None
        best_match_score = 0
        for checklist_reco in checklist_recos:
            # Calculate the similarity between the two recommendations
            similarity = 0
            if ('key_phrases' in waf_reco) and ('key_phrases' in checklist_reco):
                similarity = len(set(waf_reco['key_phrases']).intersection(checklist_reco['key_phrases'])) / len(set(waf_reco['key_phrases']).union(checklist_reco['key_phrases']))
            # If the similarity is higher than the best match, update the best match
            if (similarity > best_match_score):
                best_match = checklist_reco
                best_match_score = similarity
            # Record the maximum score found
            if (similarity > max_score):
                max_score = similarity
        # If a best match was found, store it in the WAF reco
        if best_match:
            if best_match_score >= minimum_similarity:
                match_count += 1
                waf_reco['checklist_match'] = best_match
                waf_reco['checklist_match_score'] = best_match_score
                if (args_verbose): print("DEBUG:   BEST MATCH FOUND! '{0}' (score {1})".format(best_match['text'], best_match_score))
            else:
                if (args_verbose): print("DEBUG:   Best match found but score is too low: '{0}' (score {1})".format(best_match['text'], best_match_score))
                if 'checklist_match' in waf_reco: waf_reco.pop('checklist_match')
                if 'checklist_match_score' in waf_reco: waf_reco.pop('checklist_match_score')
        else:
            if (args_verbose): print("DEBUG:   No match found for recommendation '{0}'".format(waf_reco['text']))
    if (args_verbose): print("DEBUG: Recommendations compared and {1} matches found. Maximum score found was {0}".format(max_score, match_count))
    return waf_recos

#######################
#       Main          #
#######################

# If load_filename is set, load the recommendations from a file. Otherwise retrieve them from the WAF service guides
if (args_load_filename):
    recos = load_json(args_load_filename)
    if 'svcguide_recos' in recos:
        waf_recos = recos['svcguide_recos']
        print("INFO: {1} service guide recommendations loaded from file {0}".format(args_load_filename, len(waf_recos)))
    else:
        waf_recos = []
        print("INFO: No service guide recommendations found in file {0}".format(args_load_filename))
    if 'checklist_recos' in recos:
        checklist_recos = recos['checklist_recos']
        print("INFO: {1} review checklist recommendations loaded from file {0}".format(args_load_filename, len(checklist_recos)))
    else:
        checklist_recos = []
        print("INFO: No review checklist recommendations found in file {0}".format(args_load_filename))
else:
    waf_recos = []
    checklist_recos = []

# Browse the WAF service guides if there were no recommendations loaded from the file, or if the user explicitly requested to update the recommendations
if (len(waf_recos) == 0) or (args_update_svcguide_recos):
    if (args_verbose): print("DEBUG: Retrieving recommendations from WAF service guides for {0} services ({1})...".format(len(args_service_list), str(args_service_list)))
    waf_recos = get_waf_service_guide_recos()
    print("INFO: {0} recommendations retrieved from WAF service guides".format(len(waf_recos)))

# Load the checklist recommendations from the checklist file if they were not in the loaded file
if (args_checklist_filename) and (len(checklist_recos) == 0):
    review = load_json(args_checklist_filename)
    if 'items' in review:
        checklist_recos = review['items']
        print("INFO: {1} recommendations loaded from checklist file {0}".format(args_checklist_filename, len(checklist_recos)))
    else:
        checklist_recos = []
        print("ERROR: No recommendations found in checklist file {0}".format(args_checklist_filename))
elif (args_checklist_filename):
    print("INFO: Skipping checklist loading from file since {0} recommendations were already loaded.".format(len(checklist_recos)))

# If extract_key_phrases is on, extract key phrases for each recommendation
if (args_extract_key_phrases_svcguide):
    if (args_verbose): print("DEBUG: Extracting key phrases for {0} service guide recommendations...".format(len(waf_recos)))
    waf_recos = extract_all_key_phrases(waf_recos, args_text_analytics_endpoint, args_text_analytics_key)
if (args_extract_key_phrases_checklist):
    if (args_verbose): print("DEBUG: Extracting key phrases for {0} review checklist recommendations...".format(len(waf_recos)))
    checklist_recos = extract_all_key_phrases(checklist_recos, args_text_analytics_endpoint, args_text_analytics_key)

# Proceed to compare the svcguide recos and try to find the checklist reco that matches the svcguide reco most closely
if (args_compare_recos):
    waf_recos = compare_recos(waf_recos, checklist_recos, minimum_similarity=0.3)

# Print recommendations if print_json is on
if (args_print_json) and (len(waf_recos) > 0):
    print(json.dumps({'svcguide_recos': waf_recos, 'checklist_recos': checklist_recos}, indent=4))

# If save_filename is set, store the recommendations in a file
if (args_save_filename):
    store_json({'svcguide_recos': waf_recos, 'checklist_recos': checklist_recos}, args_save_filename)
    print("INFO: Recommendations stored in file {0}".format(args_save_filename))

# If output_checklist_folder is set, store the recommendations in files, one per service
if (len(args_output_checklist_folder) > 0):
    # Check that the output folder is a valid directory
    if os.path.isdir(args_output_checklist_folder):
        # First, create a list with all the services in the recommendations
        services = list(set([x['service'] for x in waf_recos]))
        waf_pillars = list(set([x['waf'] for x in waf_recos]))
        waf_pillars_object = [{'name': x} for x in waf_pillars]
        for service in services:
            # Only export recommendations!
            service_recos = [x for x in waf_recos if x['service'] == service and x['type'] == 'recommendation']
            # Create a dictionary with checklist format
            service_checklist = {
                'items': service_recos,
                'categories': (),
                'waf': waf_pillars_object,
                'yesno': ({'name': 'Yes'}, {'name': 'No'}),
                'metadata': {
                    'name': f'{service} Service Guide',
                    'waf': 'all',
                    'state': 'preview',
                    'timestamp': datetime.date.today().strftime("%B %d, %Y")

                }
            }
            # Derive a valid file name from the service in lower case replacing blanks with underscores
            service_filename = service.lower().replace(' ', '') + '_sg_checklist.en.json'
            # Concatenate the folder with the filename using the os module
            service_filename = os.path.join(args_output_checklist_folder, service_filename)
            # Store the service checklist in the output folder
            store_json(service_checklist, service_filename)
            # Print a message
            if (args_verbose): print("DEBUG: Exported {0} recos (only recommendations and not design checks are exported) to filename {1}".format(len(service_recos), service_filename))
        # Finally, export the full file
        full_checklist = {
            'items': waf_recos,
            'categories': (),
            'waf': waf_pillars_object,
            'yesno': ({'name': 'Yes'}, {'name': 'No'}),
            'metadata': {
                'name': f'WAF Service Guides',
                'waf': 'all',
                'state': 'preview',
                'timestamp': datetime.date.today().strftime("%B %d, %Y")

            }
        }
        full_checklist_filename = os.path.join(args_output_checklist_folder, 'wafsg_checklist.en.json')
        store_json(full_checklist, full_checklist_filename)
        if (args_verbose): print("DEBUG: Exported {0} recos (only recommendations and not design checks are exported) to filename {1}".format(len(waf_recos), full_checklist_filename))

    else:
        print("ERROR: Output folder {0} is not a valid directory".format(args_output_checklist_folder))
else:
    if (args_verbose): print("DEBUG: Skipping export to output folder since no folder was provided")