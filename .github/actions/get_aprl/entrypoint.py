# This scripts gets the latest recommendations from the APRL checklists
#   and stores them in JSON files with the checklist format

import requests
import json
import datetime
import sys
import os
import yaml
import uuid

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
    # Get last commit
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
                # Only process markdown files in the containing folder folder
                if (github_folder in file_path) and (github_file_extension in file_path):
                    files_processed += 1
                    if (max_files > 0) and (files_processed > max_files):
                        print("INFO: Maximum number of files processed reached: {0}".format(max_files))
                        break
                    file_url = f'https://raw.githubusercontent.com/{github_org}/{github_repo}/{github_branch}/' + file_path
                    if (verbose): print("DEBUG: Found file '{0}'".format(file_path))
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
                                item['guid'] = str(uuid.uuid4())    # Generate a random GUID
                                item['source'] = file_path
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

#######################
#       Main          #
#######################

# Browse the APRL repo
aprl_recos = get_aprl_recos()
print("INFO: {0} recommendations retrieved from APRL.".format(len(aprl_recos)))

# Get the category JSON from the reco items
aprl_categories = list(set([reco['category'] for reco in aprl_recos]))
aprl_categories_object = [{'name': x} for x in aprl_categories]
aprl_severities = list(set([reco['severity'] for reco in aprl_recos]))
aprl_severities_object = [{'name': x} for x in aprl_severities]

# Add metadata and other info
aprl_checklist = {
    'items': aprl_recos,
    'categories': aprl_categories_object,
    'severities': aprl_severities_object,
    'waf': [{'name': 'Security'}, {'name': 'Resiliency'}, {'name': 'Operational Excellence'}, {'name': 'Performance'}, {'name': 'Cost'}],
    'yesno': [{'name': 'Yes'}, {'name': 'No'}],
    'status': [{'name': 'Not verified'}, {'name': 'Open'}, {'name': 'Fulfilled'}, {'name': 'Not required'}, {'name': 'N/A'}],
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
