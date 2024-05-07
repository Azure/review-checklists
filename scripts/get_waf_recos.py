# This scripts parses the WAF service guides and extracts the recommendations
#   for each service. The recommendations are stored in a dictionary and
#   can be compared to the recommendations in the WAF review checklist.

import requests
import argparse
import json
import re

# Arguments
parser = argparse.ArgumentParser(description='Retrieve recommendations in Azure Well-Architected Framework service guides')
parser.add_argument('--service', dest='service', action='store',
                    help='Optional service name to retrieve recommendations for (default: None)')
parser.add_argument('--print-json', dest='print_json', action='store_true',
                    default=False,
                    help='Print the full JSON (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='Run in verbose mode (default: False)')
args = parser.parse_args()

# Variables
github_org = 'MicrosoftDocs'
github_repo = 'well-architected'
waf_recos = []
max_files = 0   # Maximum number of files to process. Set to 0 to process all files.

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
                    recos.append({'waf': processing_pillar, 'service': service, 'text': remove_markdown(line_table_items[1]), 'description': remove_markdown(line_table_items[2]), 'type': 'recommendation'})
    if (verbose): print("DEBUG: {0} recommendations found in {1} lines".format(len(recos), line_count))
    return recos

# Function to add a list of recommendations to the global list to the item matching the service
def add_recos (recos, service):
    for svc in waf_recos:
        if svc['service'] == service:
            if (args.verbose): print("DEBUG: Service {0} found in recommendations list with {2} recommendations, adding {1} new recommendations".format(service, len(recos), len(svc['recos'])))
            svc['recos'] += recos
            return
    print("ERROR: Service {0} not found in recommendations list".format(service))

# Get list of WAF service guides URLs
# Get last commit
r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/commits')
if (r.status_code == 200):
    commits = r.json()
    git_tree_id = commits[0]['commit']['tree']['sha']
    if (args.verbose): print("DEBUG: Git tree ID is", git_tree_id)
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
                if (args.service is None) or (args.service == service):
                    svcguide_url = f'https://raw.githubusercontent.com/{github_org}/{github_repo}/main/' + file_path
                    # We should see whether the service already exists...
                    existing_svcs = [x['service'] for x in waf_recos if x['service'] == service]
                    if len(existing_svcs) == 0:
                        if (args.verbose): print("DEBUG: Service '{0}' not found in recommendations list, adding it...".format(service))
                        # new_service = {}
                        # new_service['service'] = service
                        # new_service['url'] = svcguide_url
                        # new_service['recos'] = []
                        # waf_recos.append(new_service)
                        waf_recos.append({'service': service, 'url': svcguide_url, 'recos': []})
                    if (args.verbose): print("DEBUG: Found service guide '{0}' for service '{1}'".format(file_path, service))
                    if (args.verbose): print("DEBUG: Retrieving service guide from URL '{0}'...".format(svcguide_url))
                    r = requests.get(svcguide_url)
                    if r.status_code == 200:
                        svcguide = r.text
                        if args.verbose: print("DEBUG: Parsing service guide '{0}', {1} characters retrieved...".format(file_path, len(svcguide)))
                        svc_recos = parse_markdown(svcguide, service, verbose=False)
                        if (len(svc_recos) > 0):
                            add_recos (svc_recos, service)
                            if args.verbose: print("DEBUG: {0} recommendations found for service {1}".format(len(svc_recos), service))
                    else:
                        print("ERROR: Unable to retrieve service guide from URL {0}".format(svcguide_url))
                        exit(1)
    else:
        print("ERROR: Unable to retrieve list of files from GitHub API")
        exit(1)
    
else:
    print("ERROR: Unable to retrieve list of commits from GitHub API: {0}. Message: {1}".format(r.status_code, r.text))
    exit(1)

# Print recommendations if print_json is on
if (args.print_json) and (len(waf_recos) > 0):
    print(json.dumps(waf_recos, indent=2))
# Print summary
for svc in waf_recos:
    print("INFO: {0} service: {1} rules found".format(svc['service'], len(svc['recos'])))