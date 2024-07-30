#######################################
#
# Module to convert v1 checklist files
#   to v2.
#
#######################################

# Dependencies
import sys
import yaml
import json
import os
from pathlib import Path
from . import cl_analyze_v2

# Get the standard service name from the service dictionary
def get_standard_service_name(service_name, service_dictionary=None):
    svc_match_found = False
    if service_dictionary:
        for svc in service_dictionary:
            if service_name in svc['names']:
                svc_match_found = True
                return svc['service']
        if not svc_match_found:
            return service_name
    else:
        return service_name

# Get the resource type from the service dictionary
# Return None if no match
def get_resource_type_name(service_name, service_dictionary=None):
    svc_match_found = False
    if service_dictionary:
        for svc in service_dictionary:
            if service_name in svc['names']:
                svc_match_found = True
                if 'arm' in svc:
                    return svc['arm']
        if not svc_match_found:
            return None
    else:
        return None


# Function to modify yaml.dump for multiline strings, see https://github.com/yaml/pyyaml/issues/240
def str_presenter(dumper, data):
    if data.count('\n') > 0:
        data = "\n".join([line.rstrip() for line in data.splitlines()])  # Remove any trailing spaces, then put it back together again
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# Function that returns a data structure with the objects in v2 format
def generate_v2(input_file, service_dictionary=None, labels=None, id_label=None, cat_label=None, subcat_label=None, verbose=False):
    if verbose: print("DEBUG: Converting file", input_file)
    if verbose and not service_dictionary: print("DEBUG: unless a service dictionary is supplied, no service or resource type mappings will be done.")
    # Default values for non-mandatory labels
    if not id_label: id_label = 'id'
    if not cat_label: cat_label = 'area'
    if not subcat_label: subcat_label = 'subarea'
    try:
        with open(input_file) as f:
            checklist = json.load(f)
    except Exception as e:
        print("ERROR: Error when processing JSON file, nothing changed", input_file, ":", str(e))
        return None
    if 'items' in checklist:
        if verbose: print("DEBUG: {0} items found in JSON file {1}".format(len(checklist['items']), input_file))
        # Create a list of objects in v2 format
        v2recos = []
        for item in checklist['items']:
            # Note that the order in which items are added to the dictionary is important, since yaml.dump is configured to not sort the keys
            # GUID/Name
            v2reco = {}
            if 'guid' in item:
                v2reco['guid'] = item['guid']
            v2reco['name']: ''          # To do: something more meaningful? (key phrase extraction?)
            # Title/description
            if 'text' in item:
                v2reco['title'] = item['text']
            if 'description' in item:
                v2reco['description'] = item['description']
            # Source (subfields file, type and timestamp)
            if 'source' in item:
                if item['source'].lower() == 'aprl' or item['source'].lower() == 'wafsg':
                    v2reco['source'] = {'type': item['source'].lower()}
                elif '.yaml' in item['source']:   # If it was imported from YAML it is coming from APRL
                    v2reco['source'] = {'type': 'aprl'}
                elif '.md' in item['source']:   # If it was imported from Markdown it is coming from a WAF service guide
                    v2reco['source'] = {'type': 'wafsg'}
            elif 'sourceType' in item:
                v2reco['source'] = {'type': item['sourceType'].lower()}
                if 'sourceFile' in item:
                    v2reco['source']['file'] = item['sourceFile']
            else:
                v2reco['source'] = {'type': 'revcl', 'file': input_file}
            if 'timestamp' in item:
                v2reco['source']['timestamp'] = item['timestamp']
            # Services
            if 'service' in item:
                v2reco['services'] = []
                v2reco['services'].append(get_standard_service_name(item['service'], service_dictionary=service_dictionary))
            # Resource types
            v2reco['resourceTypes'] = []
            if 'recommendationResourceType' in item:
                v2reco['resourceTypes'].append(item['recommendationResourceType'])
            else:   # Else try to get the resourceType from the service dictionary
                if 'service' in item:
                    resource_type = get_resource_type_name(item['service'], service_dictionary=service_dictionary)
                    if resource_type:
                        v2reco['resourceTypes'].append(resource_type)
                        # if verbose: print("DEBUG: resource type {0} identified for service {1}.".format(resource_type, item['service']))
                    # else:
                    #     if verbose: print("WARNING: not able to get resource type from service", item['service'])
            # WAF
            if 'waf' in item:
                # Normalize WAF
                if 'operation' in item['waf'].lower():
                    v2reco['waf'] = 'Operations'
                elif 'reliability' in item['waf'].lower() or 'resiliency' in item['waf'].lower():
                    v2reco['waf'] = 'Reliability'
                elif 'cost' in item['waf'].lower():
                    v2reco['waf'] = 'Cost'
                elif 'performance' in item['waf'].lower():
                    v2reco['waf'] = 'Performance'
                elif 'security' in item['waf'].lower():
                    v2reco['waf'] = 'Security'
                else:
                    if verbose: print("DEBUG: WAF value {0} in file {1} unknown".format(input_file, item['waf']))
            # Severity
            if 'severity' in item:
                if item['severity'].lower() == 'high':
                    v2reco['severity'] = 0
                elif item['severity'].lower() == 'medium':
                    v2reco['severity'] = 1
                elif item['severity'].lower() == 'low':
                    v2reco['severity'] = 2
            # Labels
            v2reco['labels'] = {}
            if 'category' in item:
                v2reco['labels'][cat_label] = item['category']
            if 'subcategory' in item:
                v2reco['labels'][subcat_label] = item['subcategory']
            if 'id' in item:
                v2reco['labels'][id_label] = item['id']
            # Links
            v2reco['links'] = []
            if 'link' in item:
                v2reco['links'].append(item['link'])
            if 'training' in item:
                v2reco['links'].append(item['training'])
            # If additional labels were specified as parameter, add them to the object
            if labels:
                for key in labels.keys():
                    v2reco['labels'][key] = labels[key]
            # Queries
            v2reco['queries'] = []
            if 'graph' in item:
                v2reco['queries'] = {}
                v2reco['queries']['arg'] = item['graph']
            # Add to the list of v2 objects
            v2recos.append(v2reco)
        return v2recos
    else:
        print("ERROR: No items found in JSON file", input_file)
        return None

# Function that removes empty directories
def remove_empty_dirs(path):
    for root, dirnames, filenames in os.walk(path, topdown=False):
        for dirname in dirnames:
            remove_empty_dirs(os.path.realpath(os.path.join(root, dirname)))

# Function that stores an object generated by generate_v2 in files in the output folder
def store_v2(output_folder, checklist, output_format='yaml', overwrite=False, verbose=False):
    if verbose: print("DEBUG: Storing v2 objects in folder", output_folder)
    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Add representer to yaml for multiline strings, see https://github.com/yaml/pyyaml/issues/240
    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter) # to use with safe_dum
    # Store each object in a separate YAML file
    for item in checklist:
        # Use the reco's name as the file name, otherwise the guid
        if 'name' in item:
            file_name = item['name']
        elif 'guid' in item:
            file_name = item['guid']
        else:
            file_name = None
        if file_name:
            # Append service and WAF pillar to output folder if available
            this_output_folder = output_folder
            if 'service' in item:
                this_output_folder = os.path.join(output_folder, item['service'].replace(" ", ""))
            else:
                this_output_folder = os.path.join(output_folder, "cross-service")
            if 'waf' in item:
                this_output_folder = os.path.join(this_output_folder, item['waf'].replace(" ", ""))
            # Create the output folder if it doesn't exist
            if not os.path.exists(this_output_folder):
                os.makedirs(this_output_folder)
            # Export JSON or YAML, depending on the output format
            # NOTE: we always overwrite, the parameter 'overwrite' is not used
            if output_format in ['yaml', 'yml']:
                output_file = os.path.join(this_output_folder, file_name + ".yaml")
                # Delete any existing file for the same GUID
                cl_analyze_v2.delete_v2_reco(output_folder, item['guid'], output_format, verbose=verbose)
                # Create the new file
                with open(output_file, 'w') as f:
                    yaml.dump(item, f, sort_keys=False)
                if verbose: print("DEBUG: Stored YAML recommendation in", output_file)
            elif output_format == 'json':
                output_file = os.path.join(this_output_folder, item['guid'] + ".json")
                # Delete any existing file for the same GUID
                cl_analyze_v2.delete_v2_reco(output_folder, item['guid'], output_format, verbose=verbose)
                # Create the new file
                with open(output_file, 'w') as f:
                    json.dump(item, f, sort_keys=False)
            else:
                print("ERROR: Unsupported output format", output_format)
                sys.exit(1)
        else:
            print("ERROR: No name could be derived for recommendation (missing name and GUID), skipping", item['text'])
            continue
    # Clean up all empty folders that might exist in the output folder, recursively
    if overwrite:
        try:
            if verbose: print("DEBUG: Removing empty directories in output folder", output_folder)
            [os.removedirs(p) for p in Path(output_folder).glob('**/*') if p.is_dir() and len(list(p.iterdir())) == 0]
        except Exception as e:
            print("ERROR: Error when removing empty directories in output folder", output_folder, ":", str(e))

# Function that guesses a reco name from a reco v2 object by querying Azure Cognitive Services for key phrases
def guess_reco_name(reco, cognitive_services_key, cognitive_services_endpoint, verbose=False):
    # Dependencies
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    if verbose: print("DEBUG: Guessing recommendation name for reco", reco['guid'])
    # Authenticate
    ta_credential = AzureKeyCredential(cognitive_services_key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=cognitive_services_endpoint, 
            credential=ta_credential)
    # Extract key phrases
    try:
        documents = [reco['title'] + '. ' + reco['description']]
        response = text_analytics_client.extract_key_phrases(documents = documents)[0]
        if not response.is_error:
            # The first key phrase is used as the guessed name
            guessed_name = response.key_phrases[0].title().replace(' ', '')
            # The source is used as prefix, if there is one
            if 'source' in reco:
                if 'type' in reco['source']:
                    guessed_name = reco['source']['type'].lower() + '-' + guessed_name
            if verbose:
                print("DEBUG: Key Phrases for reco:", str(response.key_phrases), '- Guessed name:', guessed_name)
            return guessed_name
        else:
            print(response.id, response.error)
            return None
    except Exception as err:
        print("Encountered exception. {}".format(err))
        return None

