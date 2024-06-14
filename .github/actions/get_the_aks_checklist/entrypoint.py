# This scripts gets the latest recommendations from The AKS Checklist
#   and stores them in a JSON file with the checklist format

import requests
import json
import datetime
import sys

try:
    output_file = sys.argv[1]
except:
    output_file = './checklists/theaks_checklist.en.json'
try:
    checklist_file = sys.argv[2]
except:
    checklist_file = './checklists/aks_checklist.en.json'
try:
    verbose = sys.argv[3]
except:
    verbose = 'true'

# Change string to boolean
verbose = (verbose.lower() == 'true')

# Function to store an object in a JSON file
def store_json(obj, filename):
    with open(filename, 'w') as f:
        json.dump(obj, f, indent=4)

# Function to load an object from a JSON file
def load_json(filename):
    with open(filename, 'r') as f:
        return json.load(f)


# Function to get list of URLs containing the objects of The-AKS-Checklist
# The URL is https://github.com/lgmorand/the-aks-checklist/tree/master/data/en/items
def get_theaks_recos():
    # Variables
    github_org = 'lgmorand'
    github_repo = 'the-aks-checklist'
    github_folder = 'data/en/items'
    github_file_extension = '.json'
    github_branch = 'master'
    max_files = 0   # Maximum number of files to process. Set to 0 to process all files.
    retrieved_recos = []
    # Get last commit
    r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/commits')
    if (r.status_code == 200):
        commits = r.json()
        git_tree_id = commits[0]['commit']['tree']['sha']
        if (verbose): print("DEBUG: Git tree ID is", git_tree_id)
        r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/git/trees/{git_tree_id}?recursive=true')
        if r.status_code == 200:
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
                        theaks_recos = r.json()
                        if (len(theaks_recos) > 0):
                            retrieved_recos += theaks_recos
                            if verbose: print("DEBUG: {0} recommendations found in file {1}".format(len(theaks_recos), file_path))
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

# Browse the The-AKS-checklist repo
theaks_recos = get_theaks_recos()
print("INFO: {0} recommendations retrieved from the-aks-checklist".format(len(theaks_recos)))

# If load_filename is set, load the local recommendations from a file.
if (checklist_file):
    checklist_recos = load_json(checklist_file)
    # For each reco retrieved from the-aks-checklist complete with missing fields from the existing checklist
    match_count = 0
    for reco in theaks_recos:
        if 'guid' in reco:
            guid = reco['guid']
            # Find the reco in the existing checklist matching the guid
            found = False
            for i in range(len(checklist_recos['items'])):
                if checklist_recos['items'][i]['guid'] == guid:
                    found = True
                    match_count += 1
                    # Update the new reco with values from the existing one
                    reco['category'] = checklist_recos['items'][i]['category']
                    reco['subcategory'] = checklist_recos['items'][i]['subcategory']
                    reco['waf'] = checklist_recos['items'][i]['waf']
                    if 'service' in checklist_recos['items'][i]['waf']:
                        reco['service'] = checklist_recos['items'][i]['service']
                    if 'graph' in checklist_recos['items'][i]['waf']:
                        reco['graph'] = checklist_recos['items'][i]['graph']
            if not found and verbose:
                print("DEBUG: Recommendation with guid {0} from the-aks-checklist not found in the existing checklist".format(guid))
        else:
            print("WARNING: Recommendation without guid found in the-aks-checklist")
    print("INFO: {0}/{1} recommendations matched with the existing checklist".format(match_count, len(theaks_recos)))
    # Add metadata and other info
    theaks_checklist = {
        'items': checklist_recos['items'],
        'categories': checklist_recos['categories'],
        'severities': checklist_recos['severities'],
        'waf': checklist_recos['waf'],
        'yesno': checklist_recos['yesno'],
        'status': checklist_recos['status'],
        'metadata': {
            'name': 'The AKS Checklist',
            'waf': 'none',
            'state': 'preview',
            'timestamp': datetime.date.today().strftime("%B %d, %Y")
        }
    }
# If no local checklist is loaded, add metadata with empty values
else:
    theaks_checklist = {
        'items': theaks_recos,
        'categories': [],
        'severities': [],
        'waf': [],
        'yesno': [],
        'status': [],
        'metadata': {
            'name': 'The AKS Checklist',
            'waf': 'none',
            'state': 'preview',
            'timestamp': datetime.date.today().strftime("%B %d, %Y")
        }
    }

# If save_filename is set, store the recommendations in a file
if (output_file):
    store_json(theaks_checklist, output_file)
    print("INFO: Recommendations stored in file {0}".format(output_file))
