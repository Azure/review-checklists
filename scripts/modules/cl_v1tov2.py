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
            svc_names = [x.lower for x in svc['names']]     # Case insensitive comparison
            if service_name.lower() in svc_names:
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
def generate_v2(input_file, text_analytics_endpoint=None, text_analytics_key=None, service_dictionary=None, labels=None, id_label=None, cat_label=None, subcat_label=None, verbose=False):
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
            # GUID
            v2reco = {}
            if 'guid' in item:
                v2reco['guid'] = item['guid']
            else:
                print("ERROR: No GUID found for reco in file", input_file)
                continue
            # If text analytics endpoint and key were supplied, try to guess a reco name
            if text_analytics_endpoint and text_analytics_key:
                v2reco['name'] = guess_reco_name(item, text_analytics_endpoint, text_analytics_key, version=1, verbose=verbose)
            else:
                v2reco['name'] = ''
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
                        if verbose: print("DEBUG: resource type {0} identified for service {1}.".format(resource_type, item['service']))
                    else:
                        if verbose: print("WARNING: not able to get resource type from service", item['service'])
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
    item_count = 0
    for item in checklist:
        # Use the reco's name as the file name, otherwise the guid
        item_count += 1
        if 'name' in item:
            file_name = item['name']
        elif 'guid' in item:
            file_name = item['guid']
        else:
            file_name = None
        if file_name:
            # Append service (pick the first one) and WAF pillar to output folder if available
            this_output_folder = output_folder
            if 'services' in item:
                if len(item['services']) > 0:
                    service_folder_name = item['services'][0].replace(" ", "")
                    service_folder_name = service_folder_name.replace("/", "")
                    service_folder_name = service_folder_name.replace('"', "")
                    service_folder_name = service_folder_name.replace("'", "")
                    this_output_folder = os.path.join(output_folder, service_folder_name)
                else:
                    this_output_folder = os.path.join(output_folder, "cross-service")
                    if verbose: print("DEBUG: No services found for reco", item['guid'])
            else:
                this_output_folder = os.path.join(output_folder, "cross-service")
                if verbose: print("DEBUG: 'services' field missing from reco", item['guid'])
            if 'waf' in item:
                this_output_folder = os.path.join(this_output_folder, item['waf'].replace(" ", ""))
            # Create the output folder if it doesn't exist
            if not os.path.exists(this_output_folder):
                os.makedirs(this_output_folder)
            # Export JSON or YAML, depending on the output format
            if output_format in ['yaml', 'yml']:
                output_file = os.path.join(this_output_folder, file_name + ".yaml")
                # Delete any existing file for the same GUID
                if overwrite:
                    cl_analyze_v2.delete_v2_reco(output_folder, item['guid'], output_format, verbose=verbose)
                # If the new file exists, append a number to the name
                i = 1
                while os.path.exists(output_file):
                    output_file = os.path.join(this_output_folder, file_name + "-" + str(i) + ".yaml")
                    i += 1
                # Create the new file
                try:
                    with open(output_file, 'w') as f:
                        yaml.dump(item, f, sort_keys=False)
                    if verbose: print("DEBUG: Stored YAML recommendation {0}/{1} in file {2}.".format(item_count, len(checklist), output_file))
                except Exception as e:
                    print("ERROR: Error when writing YAML file", output_file, ":", str(e))
            # JSON not finished (not using JSON for now)
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
            print("ERROR: No file name could be derived for recommendation '{0}' (missing name and GUID), skipping. Full reco object: '{1}'".format(item['title'], str(item)))
            continue
    # Clean up all empty folders that might exist in the output folder, recursively
    if overwrite:
        try:
            if verbose: print("DEBUG: Removing empty directories in output folder", output_folder)
            [os.removedirs(p) for p in Path(output_folder).glob('**/*') if p.is_dir() and len(list(p.iterdir())) == 0]
        except Exception as e:
            print("ERROR: Error when removing empty directories in output folder", output_folder, ":", str(e))

# Function that guesses a reco name from a reco v2 object by querying Azure Cognitive Services for key phrases
def guess_reco_name(reco, cognitive_services_endpoint, cognitive_services_key, version=2, verbose=False):
    # Dependencies
    from azure.ai.textanalytics import TextAnalyticsClient
    from azure.core.credentials import AzureKeyCredential
    # Authenticate
    ta_credential = AzureKeyCredential(cognitive_services_key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=cognitive_services_endpoint, 
            credential=ta_credential)
    # Prepare the document (either the title, the description or both), depending on the version being used (the field names vary)
    if version == 1:
        if 'text' in reco and 'description' in reco:
            documents = [reco['text'] + '. ' + reco['description']]
        elif 'text' in reco:
            documents = [reco['text']]
        elif 'description' in reco:
            documents = [reco['description']]
        else:
            if verbose: print("ERROR: No title or description found for reco {0} that can be used to derive name".format(reco['guid']))
            return ''
    elif version == 2:
        if 'title' in reco and 'description' in reco:
            documents = [reco['title'] + '. ' + reco['description']]
        elif 'title' in reco:
            documents = [reco['title']]
        elif 'description' in reco:
            documents = [reco['description']]
        else:
            if verbose: print("ERROR: No title or description found for reco {0} that can be used to derive name".format(reco['guid']))
            return ''
    else:
        print("ERROR: Unsupported version for name guessing", version)
    # Extract key phrases
    if verbose: print("DEBUG: Guessing recommendation name for reco '{0}'. Using endpoint {2} and string '{1}'...".format(reco['guid'], documents[0], cognitive_services_endpoint))
    try:
        response = text_analytics_client.extract_key_phrases(documents = documents)[0]
    except Exception as err:
        print("Encountered exception. {}".format(err))
        return None
    # Return first key phrase as the guessed name formated without blanks
    if not response.is_error:
        # The first key phrase is used as the guessed name
        guessed_name = response.key_phrases[0].title().replace(' ', '')
        # Replace other special characters that might be present in the key phrase
        guessed_name = guessed_name.replace('/', '')
        guessed_name = guessed_name.replace('\\', '')
        guessed_name = guessed_name.replace('"', '')
        guessed_name = guessed_name.replace("'", '')
        guessed_name = guessed_name.replace('-', '')
        guessed_name = guessed_name.replace('_', '')
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
    
# Load a v1 checklist and generate a v2 checklist YAML file
# If use_names = True, it will add a name selector instead of a GUID selector. Recos folder needs to be specified
# Try to match the subarea sections with services if possible, if not use a guid selector
def checklist_v1_to_v2(input_file, output_file, use_names=False, v2recos_folder=None, verbose=None):
    # Load the v1 checklist
    try:
        if verbose: print("DEBUG: Loading v1 checklist from file", input_file)
        with open(input_file) as f:
            checklist_v1 = json.load(f)
    except Exception as e:
        print("ERROR: Error when processing JSON file", input_file, ":", str(e))
        return None
    # If use_names is True, load the v2 recos
    if use_names:
        if not v2recos_folder:
            print("ERROR: Recos folder needs to be specified when using names")
            return None
        if verbose: print("DEBUG: Loading v2 recos from folder {0}, since using names...".format(v2recos_folder))
        v2recos = cl_analyze_v2.load_v2_files(v2recos_folder, verbose=False)
        if verbose: print("DEBUG: {0} v2 recos loaded.".format(len(v2recos)))
    # Create the v2 checklist
    checklist_v2 = {}
    # Add the metadata
    checklist_v2['metadata'] = {}
    if 'metadata' in checklist_v1:
        if 'name' in checklist_v1['metadata']:
            checklist_v2['name'] = checklist_v1['metadata']['name']
        else:
            checklist_v2['name'] = 'Name missing from checklist YAML file'
    else:
        checklist_v2['name'] = 'Name missing from checklist YAML file'
    # Create a dictionary with areas/subareas
    area_list = list(set([x['category'] for x in checklist_v1['items'] if 'category' in x]))
    if verbose: print("DEBUG: {0} areas found in v1 checklist.".format(len(area_list)))
    area_dict = {}
    for area in area_list:
        area_dict[area] = list(set([x['subcategory'] for x in checklist_v1['items'] if ('subcategory' in x) and ('category' in x) and (x['category'] == area)]))
        if verbose: print("DEBUG: {0} subareas found in area {1}.".format(len(area_dict[area]), area))
    # For each area/subarea, add a guid selector
    checklist_v2['areas'] = []
    for area in area_dict.keys():
        checklist_v2_area_object = {'name': area, 'subareas': []}
        for subarea in area_dict[area]:
            guids = [x['guid'] for x in checklist_v1['items'] if ('guid' in x) and ('category' in x) and (x['category'] == area) and ('subcategory' in x) and (x['subcategory'] == subarea)]
            if verbose: print("DEBUG: {0} GUIDs found in area {1} and subarea {2}.".format(len(guids), area, subarea))
            if use_names:
                names = [cl_analyze_v2.get_reco_name_from_guid(v2recos, x) for x in guids]
                names = [x for x in names if x] # Remove empty names
                if verbose: print("DEBUG: {0} names found in area {1} and subarea {2}.".format(len(names), area, subarea))
                if names and len(names) > 0:
                    checklist_v2_subarea_object = {'name': subarea, 'include': {'nameSelector': names}}
                    checklist_v2_area_object['subareas'].append(checklist_v2_subarea_object)
            else:
                if guids and len(guids) > 0:
                    checklist_v2_subarea_object = {'name': subarea, 'include': {'guidSelector': guids}}
                    checklist_v2_area_object['subareas'].append(checklist_v2_subarea_object)
        checklist_v2['areas'].append(checklist_v2_area_object)
    # Write the output file
    if verbose: print("DEBUG: Writing v2 checklist to file", output_file)
    with open(output_file, 'w') as f:
        yaml.dump(checklist_v2, f, indent=4)
    return checklist_v2

