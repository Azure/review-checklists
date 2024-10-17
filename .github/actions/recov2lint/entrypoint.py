# This scripts runs checks on the v2 recommendations and checklists
import jsonschema
import sys
import yaml
import json
import os
from pathlib import Path
from collections import Counter


# The script has been modified to be run from a github action with positional parameters
# 1. Root Folder where the v2 recommendations, checklists and schemas are stored
# 2. Verbose
try:
    root_folder = sys.argv[1]
except:
    root_folder = './v2'
try:
    verbose = (sys.argv[2].lower() == 'true')
except:
    verbose = True

# Print the parameters
if verbose: print("INFO: Running recov2lint with parameters: root_folder='{0}', verbose={1}".format(root_folder, verbose))

# Constants
checklist_subfolder = os.path.join(root_folder, 'checklists')
reco_subfolder = os.path.join(root_folder, 'recos')
schema_subfolder = os.path.join(root_folder, 'schema')
reco_schema_file = os.path.join(schema_subfolder, 'recommendation.schema.json')
checklist_schema_file = os.path.join(schema_subfolder, 'checklist.schema.json')

# Verify that the root folder and the subfolders exist
if not os.path.exists(root_folder):
    print(f"ERROR: Root folder '{root_folder}' does not exist.")
    sys.exit(1)
if not os.path.exists(checklist_subfolder):
    print(f"ERROR: Checklist subfolder '{checklist_subfolder}' does not exist.")
    sys.exit(1)
if not os.path.exists(reco_subfolder):
    print(f"ERROR: Reco subfolder '{reco_subfolder}' does not exist.")
    sys.exit(1)
if not os.path.exists(schema_subfolder):
    print(f"ERROR: Schema subfolder '{schema_subfolder}' does not exist.")
    sys.exit(1)
if not os.path.exists(reco_schema_file):
    print(f"ERROR: Reco schema file '{reco_schema_file}' does not exist.")
    sys.exit(1)
if not os.path.exists(checklist_schema_file):
    print(f"ERROR: Checklist schema file '{checklist_schema_file}' does not exist.")
    sys.exit(1)

# Gets all YAML files in a folder and parses them into a list of objects, adding the filepath for reference
def get_yml_objects(folder, verbose=False):
    files = list(Path(folder).rglob( '*.*' ))
    if verbose: print("DEBUG: Found {0} files in folder {1}".format(len(files), folder))
    objects = []
    for file in files:
        if (file.suffix == '.yaml') or (file.suffix == '.yml'):
            try:
                with open(file.resolve()) as f:
                    object = yaml.safe_load(f)
            except Exception as e:
                print("ERROR: Error when loading YAML file {0} - {1}". format(file, str(e)))
            item = {
                'filepath': str(file.resolve()),
                'object': object
            }
            objects.append(item)
    if verbose: print("DEBUG: Loaded {0} objects from folder {1}".format(len(objects), folder))
    return objects        

# Given a list of objects, compares them with a JSON schema
def get_invalid_objects(items, schema_file, verbose=False):
    # Retrieve checklists schema
    if verbose: print("DEBUG: Loading schema from", schema_file)
    with open(schema_file, 'r') as stream:
        try:
            schema = json.load(stream)
        except:
            print("ERROR: Error loading JSON schema from", schema_file)
            return None
    # Start validation
    if verbose: print("DEBUG: Starting validation with schema {0}...".format(schema_file))
    object_counter = 0
    finding_counter = 0
    for item in items:
        object = item['object']
        object_counter +=1
        if 'name' in object:
            object_name = object['name']
        else:
            object_name = 'unnamed'
        try:
            jsonschema.validate(object, schema)
            if verbose: print("DEBUG: Checklist '{0}' in '{1}' validates correctly against the schema.".format(object_name, item['filepath']))
        except jsonschema.exceptions.ValidationError as e:
            print("ERROR: Object '{0}' in '{1}' does not validate against the schema.".format(object_name, item['filepath']))
            print("DEBUG: -", str(e))
            finding_counter += 1
        except jsonschema.exceptions.SchemaError as e:
            print("ERROR: Schema", schema_file, "does not seem to be valid.")
            if verbose: print("DEBUG: -", str(e))
            sys.exit(1)
        except Exception as e:
            print("ERROR: Unknown error validating checklist '{0}' against the schema {1}: {2}".format(cl['name'], schema_file,str(e)))
    return finding_counter


# Get all recos
v2recos = get_yml_objects(reco_subfolder)
# Look for duplicate names
name_list = [reco['object']['name'] for reco in v2recos if 'name' in reco['object']]
name_counts = Counter(name_list)
duplicate_names = [item for item, count in name_counts.items() if count > 1]
if len(duplicate_names) > 0:
    print("ERROR: Duplicate reco names found: {0}".format(duplicate_names))
    sys.exit(1)
else:
    print("INFO: No duplicate reco names found in {0} recommendations.".format(len(v2recos)))
# Validate recos
reco_errors = get_invalid_objects(v2recos, reco_schema_file, verbose=verbose)
if reco_errors > 0:
    print("ERROR: {0} recos did not validate against the schema.".format(reco_errors))
    sys.exit(1)
else:
    print("INFO: {0} recommendations validated from folder {2}, {1} non-compliances found.".format(len(v2recos), reco_errors, reco_subfolder))

# Get all checklists
v2checklists = get_yml_objects(checklist_subfolder)
# Validate checklists
checklist_errors = get_invalid_objects(v2checklists, checklist_schema_file, verbose=verbose)
if checklist_errors > 0:
    print("ERROR: {0} checklists did not validate against the schema.".format(checklist_errors))
    sys.exit(1)
else:
    print("INFO: {0} checklists validated from folder {2}, {1} non-compliances found.".format(len(v2checklists), checklist_errors, checklist_subfolder))


