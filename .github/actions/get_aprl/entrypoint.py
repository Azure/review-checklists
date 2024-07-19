# This scripts gets the latest recommendations from the APRL checklists
#   and stores them in JSON files with the checklist format.
# Sample usage:
#   python3 entrypoint.py ./checklists-ext/aprl_checklist.en.json true

import requests
import json
import datetime
import sys
import os
import yaml

# Parameters
try:
    output_file = sys.argv[1]
except:
    output_file = './checklists-ext/aprl_checklist.en.json'
try:
    verbose = (sys.argv[2].lower() == 'true')
except:
    verbose = 'true'

# Other control variables (which probably should be turned into parameters)
max_files = 0   # Maximum number of files to process. Set to 0 to process all files.

# Constants to create a compliant checklist
statuses_object = [
    {
      "name": "Not verified",
      "description": "This check has not been looked at yet"
    },
    {
      "name": "Open",
      "description": "There is an action item associated to this check"
    },
    {
      "name": "Fulfilled",
      "description": "This check has been verified, and there are no further action items associated to it"
    },
    {
      "name": "N/A",
      "description": "Not applicable for current design"
    },
    {
      "name": "Not required",
      "description": "Not required"
    }
]
yesno_object = [
    {'name': 'Yes'}, 
    {'name': 'No'}
]
waf_object = [
    {
      "name": "Reliability"
    },
    {
      "name": "Security"
    },
    {
      "name": "Cost"
    },
    {
      "name": "Operations"
    },
    {
      "name": "Performance"
    }
  ]
schema_url = 'https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/checklist.schema.json'

# Function to store an object in a JSON file
def store_json(obj, filename):
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=4)

# Function to load an object from a JSON file
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)

# Function to load an object from a YAML file
def load_yaml(filename):
    with open(filename, 'r') as f:
        return yaml.safe_load(f)

# Function to get list of URLs containing the APRL objects
def get_aprl_recos():
    # Variables
    github_org = 'Azure'
    github_repo = 'Azure-Proactive-Resiliency-Library-v2'
    github_folder = 'azure-resources/'
    github_file_extension = '.yaml'
    github_branch = 'master'
    retrieved_recos = []
    timestamp = datetime.date.today().strftime("%B %d, %Y")
    # Get last commit to APRL reco
    if (verbose): print("DEBUG: Scanning GitHub repository {0} for {1} files...".format(github_repo, github_file_extension))
    r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/commits')
    if (r.status_code == 200):
        commits = r.json()
        git_tree_id = commits[0]['commit']['tree']['sha']
        if (verbose): print("DEBUG: Git tree ID is", git_tree_id)
        r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/git/trees/{git_tree_id}?recursive=true')
        if r.status_code == 200:
            if (verbose): print("DEBUG: {0} files in repository.".format(len(r.json()['tree'])))
            files_processed = 0
            for path in r.json()['tree']:
                file_path = path['path']
                # Only process files in the containing folder defined in the variables above
                if (github_folder in file_path) and (github_file_extension in file_path):
                    files_processed += 1
                    if (max_files > 0) and (files_processed > max_files):
                        print("INFO: Maximum number of files processed reached: {0}".format(max_files))
                        break
                    file_url = f'https://raw.githubusercontent.com/{github_org}/{github_repo}/{github_branch}/' + file_path
                    # if (verbose): print("DEBUG: Found file '{0}'".format(file_path))
                    if (verbose): print("DEBUG: Retrieving recos from URL '{0}'...".format(file_url))
                    r = requests.get(file_url)
                    if r.status_code == 200:
                        aprl_recos = yaml.safe_load(r.text)
                        if (len(aprl_recos) > 0):
                            for item in aprl_recos:
                                # Fill in the service from the file name
                                # item['service'] = os.path.basename(file_path).replace(github_file_extension, '').title()
                                item['service'] = item['recommendationResourceType']
                                item['text'] = item['description']
                                item['description'] = item['longDescription']
                                if 'learnMoreLink' in item:
                                    if 'url' in item['learnMoreLink']:
                                        item['link'] = item['learnMoreLink']['url']
                                item['severity'] = item['recommendationImpact']
                                item['category'] = item['recommendationControl']
                                item['guid'] = item['aprlGuid']
                                item['sourceFile'] = file_path
                                item['source'] = 'aprl'
                                item['timestamp'] = timestamp
                            retrieved_recos += aprl_recos
                            if verbose: print("DEBUG: {0} recommendations found in file {1}".format(len(aprl_recos), file_path))
                    else:
                        print("ERROR: Unable to retrieve recos from URL {0}".format(file_url))
            return retrieved_recos
        else:
            print("ERROR: Unable to retrieve list of files from GitHub API")
            return None
    else:
        print("ERROR: Unable to retrieve list of commits from GitHub API: {0}. Message: {1}".format(r.status_code, r.text))
        return None

def get_aprl_kql(aprl_recos):
    # Variables
    github_org = 'Azure'
    github_repo = 'Azure-Proactive-Resiliency-Library-v2'
    github_folder = 'azure-resources/'
    github_file_extension = '.kql'
    github_branch = 'master'
    files_processed = 0
    kql_matches = 0
    # Get last commit
    if (verbose): print("DEBUG: Scanning GitHub repository {0} for {1} files...".format(github_repo, github_file_extension))
    r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/commits')
    if (r.status_code == 200):
        commits = r.json()
        git_tree_id = commits[0]['commit']['tree']['sha']
        if (verbose): print("DEBUG: Git tree ID is", git_tree_id)
        r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/git/trees/{git_tree_id}?recursive=true')
        if r.status_code == 200:
            if (verbose): print("DEBUG: {0} files in repository.".format(len(r.json()['tree'])))
            # Browse all found files
            for path in r.json()['tree']:
                file_path = path['path']
                # Only process files in the containing folder folder
                if (github_folder in file_path) and (github_file_extension in file_path):
                    files_processed += 1
                    if (max_files > 0) and (files_processed > max_files):
                        print("INFO: Maximum number of files processed reached: {0}".format(max_files))
                        break
                    file_url = f'https://raw.githubusercontent.com/{github_org}/{github_repo}/{github_branch}/' + file_path
                    r = requests.get(file_url)
                    if r.status_code == 200:
                        kql = r.text
                        guid = os.path.basename(file_path).replace(github_file_extension, '').lower()
                        # Find the reco in the list and update the graph property
                        reco_found = False
                        for reco in aprl_recos:
                            if reco['guid'].lower() == guid:
                                reco_found = True
                                kql_matches += 1
                                reco['graph'] = kql
                                break
                        if not reco_found:
                            print("ERROR: Unable to find recommendation with GUID {0}".format(guid))
                    else:
                        print("ERROR: Unable to retrieve KQL from URL {0}".format(file_url))
        else:
            print("ERROR: Unable to retrieve list of files from GitHub API")
            return None
    else:
        print("ERROR: Unable to retrieve list of commits from GitHub API: {0}. Message: {1}".format(r.status_code, r.text))
    # The modified list of recos is returned
    if (verbose): print("DEBUG: {0} KQL files processed, {1} matched to recommendations...".format(files_processed, kql_matches))
    return aprl_recos

#######################
#       Main          #
#######################

# Browse the APRL repo
aprl_recos = get_aprl_recos()
print("INFO: {0} recommendations retrieved from APRL.".format(len(aprl_recos)))
# Enrich with queries
aprl_recos = get_aprl_kql(aprl_recos)

# Get the category JSON from the reco items
aprl_categories = list(set([reco['category'] for reco in aprl_recos]))
aprl_categories_object = [{'name': x} for x in aprl_categories]
aprl_severities = list(set([reco['severity'] for reco in aprl_recos]))
aprl_severities_object = [{'name': x} for x in aprl_severities]

# Add metadata and other info
aprl_checklist = {
    '$schema': schema_url,
    'items': aprl_recos,
    'categories': aprl_categories_object,
    'severities': aprl_severities_object,
    'waf': waf_object,
    'yesno': yesno_object,
    'status': statuses_object,
    'metadata': {
        'name': 'APRL Checklist',
        'waf': 'none',
        'state': 'preview',
        'timestamp': datetime.date.today().strftime("%B %d, %Y")
    }
}

# If save_filename is set, store the recommendations in a file
if (output_file):
    store_json(aprl_checklist, output_file)
    print("INFO: Recommendations stored in file {0}".format(output_file))
