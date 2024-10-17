# This script gets the latest files from the main branch of the repo
#   and copies them in the local folders. It can be used to sync the
#   local files with the latest version of the repo.

import requests
import argparse
import os

# Parameters
parser = argparse.ArgumentParser(description='Copy files from the remote branch of a GitHub repo to a local folder')
parser.add_argument('--branch', dest='github_branch', action='store',
                    default='main',
                    help='GitHub branch to copy files from (default: main)')
parser.add_argument('--folder', dest='github_folder', action='store',
                    default='checklists',
                    help='GitHub folder to copy files from (default: checklists)')
parser.add_argument('--dry-run', dest='dryrun', action='store_true',
                    default=False,
                    help='run in dry-run mode, no files are actually copied (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# Variables (could be parametrised)
github_org = 'Azure'
github_repo = 'review-checklists'
github_file_extension = '.json'
output_folder = os.path.join('.', args.github_folder)

# Function to copy files from a remote URL into a local folder
# Using global variables for the folders, but could be passed as parameters
def get_files():
    # Variables
    max_files = 0   # Maximum number of files to process. Set to 0 to process all files.
    retrieved_recos = []
    # Get last commit
    r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/commits')
    if (r.status_code == 200):
        commits = r.json()
        git_tree_id = commits[0]['commit']['tree']['sha']
        if (args.verbose): print("DEBUG: Git tree ID is", git_tree_id)
        r = requests.get(f'https://api.github.com/repos/{github_org}/{github_repo}/git/trees/{git_tree_id}?recursive=true')
        if r.status_code == 200:
            files_processed = 0
            files_errors = 0
            files_success = 0
            for path in r.json()['tree']:
                file_path = path['path']
                # Only process files in the containing folder with the right extension
                if (args.github_folder + "/" in file_path) and (github_file_extension in file_path):
                    files_processed += 1
                    if (max_files > 0) and (files_processed > max_files):
                        print("INFO: Maximum number of files processed reached: {0}".format(max_files))
                        break
                    file_url = f'https://raw.githubusercontent.com/{github_org}/{github_repo}/{args.github_branch}/' + file_path
                    if (args.verbose): print("DEBUG: Found file '{0}'".format(file_path))
                    # Download the file to the output folder
                    file_name = file_path.split('/')[-1]
                    output_path = os.path.join(output_folder, file_name)
                    if args.dryrun:
                        print("INFO: Would copy file {0} to {1}".format(file_url, output_path))    
                        files_success += 1
                    else:
                        r = requests.get(file_url)
                        if r.status_code == 200:
                            with open(output_path, 'w') as f:
                                f.write(r.text)
                                files_success += 1
                        else:
                            print("ERROR: Unable to download file {0} from GitHub API: {1}. Message: {2}".format(file_path, r.status_code, r.text))
                            files_errors += 1
            if args.verbose:
                print("INFO: {0} files processed, {1} errors, {2} success".format(files_processed, files_errors, files_success))
            return files_success
        else:
            print("ERROR: Unable to retrieve list of files from GitHub API")
            return None
    else:
        print("ERROR: Unable to retrieve list of commits from GitHub API: {0}. Message: {1}".format(r.status_code, r.text))
        return None

#######################
#       Main          #
#######################

# Get remote files
copied_files = get_files()
print("INFO: {0} files synced from branch {1} of {2}/{3} to output folder {4}".format(copied_files, args.github_branch, github_org, github_repo, output_folder))
