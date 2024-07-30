#######################################
#
# Module to analyze v2 checklist
#   folder structures.
#
#######################################

# Dependencies
import sys
import yaml
import json
import os
from pathlib import Path

# Function that returns true if a given reco matches the criteria specified by a label selector, a service selector and a WAF selector
def reco_matches_criteria(reco, labels=None, services=None, resource_types=None, waf_pillars=None, sources=None, arg=False, guid=None):
    # Check if the reco fulfills the criteria
    # GUID
    if guid:
        guid_match = False
        if 'guid' in reco:
            if reco['guid'].lower() == guid.lower():
                return True
    else:
        guid_match = True
    # Labels
    if labels:
        label_match = False
        if 'labels' in reco:
            for key in labels.keys():
                if key in reco['labels']:
                    if labels[key] == reco['labels'][key]:
                        label_match = True
    else:
        label_match = True
    # Services
    if services:
        service_match = False
        services = [x.lower() for x in services]        # Transform to lower case for case-insensitive comparison
        if 'none' in services:
            service_match = ('services' not in reco)
        if 'services' in reco:
            for reco_service in reco['services']:
                if reco_service.lower() in services:
                    service_match = True
    # Resource Types
    if resource_types:
        resource_type_match = False
        resource_types = [x.lower() for x in resource_types]        # Transform to lower case for case-insensitive comparison
        if 'none' in resource_types:
            resource_type_match = ('resourceTypes' not in reco)
        if 'resourceTypes' in reco:
            for reco_resource_type in reco['resourceTypes']:
                if reco_resource_type.lower() in resource_types:
                    resource_type_match = True
    else:
        resource_type_match = True
    # WAF
    if waf_pillars:
        waf_match = False
        if 'none' in waf_pillars:
            waf_match = ('waf' not in reco)
        if 'waf' in reco:
            if reco['waf'].lower() in waf_pillars:
                waf_match = True
    else:
        waf_match = True
    # Sources
    if sources:
        src_match = False
        if 'none' in sources:
            src_match = ('source' not in reco)
        if 'source' in reco:
            if 'type' in reco['source']:
                if reco['source']['type'].lower() in sources:
                    src_match = True
    else:
        src_match = True
    arg_match = ((not arg) or ('queries' in reco and 'arg' in reco['queries']))
    # If no selector was provided, add all recos to the list
    return (guid_match and label_match and service_match and resource_type_match and waf_match and arg_match and src_match)

# Opens a file with a text editor
def open_file_with_editor(file, text_editor=None, verbose=False):
    if text_editor:
        if verbose: print("DEBUG: Opening file", file.resolve(), "with text editor", text_editor)
        os.system(text_editor + ' ' + str(file.resolve()))
    else:
        if os.name == 'nt':
            if verbose: print("DEBUG: Opening file", file.resolve(), "with default Windows text editor")
            os.system(str(file.resolve()))
        elif os.name == 'posix':
            if os.getenv('EDITOR'):
                if verbose: print("DEBUG: Opening file", file, "with default Linux text editor")
                os.system('%s %s' % (os.getenv('EDITOR'), str(file.resolve())))
            else:
                print("ERROR: No text editor found in the EDITOR environment variable")
        else:
            print("ERROR: Unsupported OS", os.name)

# Function that loads all of the found v2 YAML/JSON files into a single object
# labels, services and waf_pillars are selectors with object structure
def load_v2_files(input_folder, format='yaml', labels=None, services=None, waf_pillars=None, sources=None, guid=None, arg=False, open_editor=False, text_editor=None, verbose=False):
    # Banner
    if verbose:
        print("DEBUG: ======================================================================")
        print("DEBUG: Loading v2 files from folder", input_folder)
    # Look for files in the input folder
    v2recos = []
    # If the input folder exists
    if os.path.exists(input_folder):
        files = list(Path(input_folder).rglob( '*.*' ))
        for file in files:
            # JSON
            if format == 'json':
                if file.suffix == '.json':
                    # if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = json.safe_load(f)
                            if reco_matches_criteria(v2reco, labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, guid=guid):
                                if verbose: print("DEBUG: reco in file", file, "matches criteria.")
                                v2recos.append(v2reco)
                                if open_editor:
                                    open_file_with_editor(file, text_editor=text_editor, verbose=verbose)
                    except Exception as e:
                        print("ERROR: Error when loading file {0} - {1}". format(file, str(e)))
            # YAML
            if format == 'yaml' or format == 'yml':
                if (file.suffix == '.yaml') or (file.suffix == '.yml'):
                    # if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = yaml.safe_load(f)
                            if reco_matches_criteria(v2reco, labels=labels, services=services, waf_pillars=waf_pillars, guid=guid, arg=arg):
                                if verbose: print("DEBUG: reco in file", file, "matches criteria.")
                                v2recos.append(v2reco)
                                if open_editor:
                                    open_file_with_editor(file, text_editor=text_editor, verbose=verbose)
                    except Exception as e:
                        print("ERROR: Error when loading file {0} - {1}". format(file, str(e)))
        # Return the object with all the v2 objects
        return v2recos
    else:
        print("ERROR: Input folder", input_folder, "does not exist.")
        return None

# Return an object with some statistics about the v2 objects 
def v2_stats_from_object(v2recos, verbose=False):
    # Banner
    if verbose:
        print("DEBUG: ======================================================================")
        print("DEBUG: Analyzing v2 objects...")
    # Create a dictionary with the stats
    stats = {}
    stats['total_items'] = len(v2recos)
    stats['severity'] = {}
    stats['labels'] = {}
    stats['services'] = {}
    stats['waf'] = {}
    stats['sources'] = {}
    stats['resourceTypes'] = {}
    for reco in v2recos:
        # Count the number of items per severity
        if 'severity' in reco:
            if reco['severity'] in stats['severity']:
                stats['severity'][reco['severity']] += 1
            else:
                stats['severity'][reco['severity']] = 1
        else:
            if 'undefined' in stats['severity']:
                stats['severity']['undefined'] += 1
            else:
                stats['severity']['undefined'] = 1
        # Count the number of items per area
        if 'labels' in reco:
                for thislabelkey in reco['labels'].keys():
                    labeltext = thislabelkey + ":" + reco['labels'][thislabelkey]
                    if labeltext in stats['labels']:
                        stats['labels'][labeltext] += 1
                    else:
                        stats['labels'][labeltext] = 1
        # Count the number of items per service
        if 'service' in reco:
            if reco['service'] in stats['services']:
                stats['services'][reco['service']] += 1
            else:
                stats['services'][reco['service']] = 1
        else:
            if 'undefined' in stats['services']:
                stats['services']['undefined'] += 1
            else:
                stats['services']['undefined'] = 1
        # Count the number of items per WAF pillar
        if 'waf' in reco:
            if reco['waf'] in stats['waf']:
                stats['waf'][reco['waf']] += 1
            else:
                stats['waf'][reco['waf']] = 1
        else:
            if 'undefined' in stats['waf']:
                stats['waf']['undefined'] += 1
            else:
                stats['waf']['undefined'] = 1
        # Count the number of items per source
        if 'source' in reco:
            if 'type' in reco['source']:
                if reco['source']['type'] in stats['sources']:
                    stats['sources'][reco['source']['type']] += 1
                else:
                    stats['sources'][reco['source']['type']] = 1
        # Resource types
        if 'resourceTypes' in reco:
            for resourceType in reco['resourceTypes']:
                if resourceType in stats['resourceTypes']:
                    stats['resourceTypes'][resourceType] += 1
                else:
                    stats['resourceTypes'][resourceType] = 1
    # Return the stats object
    return stats

# Return an object with some statistics about the v2 objects in a folder
def v2_stats_from_folder(input_folder, format='yaml', labels=None, services=None, waf_pillars=None, sources=None, verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, verbose=verbose)
    # Get the stats from the v2 objects
    stats = v2_stats_from_object(v2recos, verbose=verbose)
    # Return the stats object
    return stats

# Return an object with the recos fulfilling the specified criteria
def get_recos(input_folder, labels=None, services=None, waf_pillars=None, sources=None, guid=None, arg=False, format='yaml', verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, verbose=verbose)
    if v2recos:
        # Create a list of recos that fulfill the criteria
        recos = []
        for reco in v2recos:
            if reco_matches_criteria(reco, labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, guid=guid, arg=arg):
                recos.append(reco)
        # Return the recos object
        return recos
    else:
        print("ERROR: no recos could be loaded from folder", input_folder)

# Return a single reco per GUID from a list of recos. The file can be identified by the file name
# We could look for a file with the GUID in the name, but Linux file systems are case sensitive, plus
#   errors where the file name is incorrect would be hard to debug
def get_reco(input_folder, guid, verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, guid=guid, format='yaml', verbose=verbose)
    if v2recos:
        # Return the reco object
        return v2recos
    else:
        print("ERROR: no reco could be loaded from folder", input_folder)
    return None

# Function to modify yaml.dump for multiline strings, see https://github.com/yaml/pyyaml/issues/240
def str_presenter(dumper, data):
    if data.count('\n') > 0:
        data = "\n".join([line.rstrip() for line in data.splitlines()])  # Remove any trailing spaces, then put it back together again
        return dumper.represent_scalar('tag:yaml.org,2002:str', data, style='|')
    return dumper.represent_scalar('tag:yaml.org,2002:str', data)

# Print in screen a single v2 recommendation
def print_reco(reco):
    # Add representer to yaml for multiline strings, see https://github.com/yaml/pyyaml/issues/240
    yaml.add_representer(str, str_presenter)
    yaml.representer.SafeRepresenter.add_representer(str, str_presenter) # to use with safe_dum
    print(yaml.safe_dump(reco, default_flow_style=False, sort_keys=False))

# Print in screen a v2 recommendation in one line with fixed width columns
def print_recos(recos, show_labels=False, show_arg=False):
    print("{0:<37} {1:<80} {2:<30} {3:<15}".format('GUID', 'TITLE', 'SERVICE', 'WAF'), end="")
    if show_labels:
        print("{0:<40}".format("LABELS"), end="")
    if show_arg:
        print("{0:<40}".format("AZURE RESOURCE GRAPH QUERY"), end="")
    print()
    print("{0:<37} {1:<80} {2:<30} {3:<15}".format('====', '=====', '=======', '==='), end="")
    if show_labels:
        print("{0:<40}".format("======"), end="")
    if show_arg:
        print("{0:<40}".format("=========================="), end="")
    print()
    for reco in recos:
        guid=reco['guid'] if 'guid' in reco else ''
        title=reco['title'] if 'title' in reco else ''
        service=reco['service'] if 'service' in reco else ''
        waf=reco['waf'] if 'waf' in reco else ''
        print("{0:<37} {1:<80} {2:<30} {3:<15}".format(guid, title[:79], service[:29], waf), end="")
        if show_labels:
            if 'labels' in reco:
                print("{0:<40}".format(str(reco['labels'])), end="")
        if show_arg:
            if 'queries' in reco and 'arg' in reco['queries']:
                print("{0:<40}".format(reco['queries']['arg'][:39]), end="")
        print()
    print("   {0} recommendations listed".format(len(recos)))

# Get selectors from a checklist file in YAML format
# Returns the label, service and WAF selectors, and the variables, in this order
def get_checklist_selectors(checklist_file, verbose=False):
    # Load the checklist file
    try:
        with open(checklist_file) as f:
            checklist = yaml.safe_load(f)
    except Exception as e:
        print("ERROR: Error when loading file {0} - {1}". format(checklist_file, str(e)))
        return None, None, None
    # Get the selectors
    if 'labelSelector' in checklist:
        labelSelector = checklist['labelSelector']
        for key in labelSelector.keys():
            print ("DEBUG: Label selector found:", key + ":" + labelSelector[key])
    else:
        labelSelector = None
    if 'serviceSelector' in checklist:
        serviceSelector = checklist['serviceSelector']
        for service in serviceSelector:
            print ("DEBUG: Service selector found:", service)
    else:
        serviceSelector = None
    if 'wafSelector' in checklist:
        wafSelector = checklist['wafSelector']
        for waf in wafSelector:
            print ("DEBUG: WAF selector found:", waf)
    else:
        wafSelector = None
    if 'variables' in checklist:
        variables = checklist['variables']
        for variable_key in variables.keys():
            print ("DEBUG: Variable found:", variable_key + ":" + variables[variable_key])
    else:
        variables = None
    # Return the selectors
    return labelSelector, serviceSelector, wafSelector, variables

# Loads a checklist file in YAML format
def get_checklist_object(checklist_file, verbose=False):
    # Load the checklist file
    try:
        with open(checklist_file) as f:
            checklist = yaml.safe_load(f)
            return checklist
    except Exception as e:
        print("ERROR: Error when loading file {0} - {1}". format(checklist_file, str(e)))
        return None

# Function that finds the file with a specific GUID and deletes it
def delete_v2_reco(input_folder, guid, format='yaml', verbose=False):
    # Whether the reco was found
    reco_found = False
    # If the input folder exists
    if os.path.exists(input_folder):
        files = list(Path(input_folder).rglob( '*.*' ))
        for file in files:
            # JSON
            if format == 'json':
                if file.suffix == '.json':
                    # if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = json.safe_load(f)
                        f.close()
                        if 'guid' in v2reco:
                            if v2reco['guid'].lower() == guid.lower():
                                if verbose: print('DEBUG: deleting reco', guid, 'in file', file)
                                os.remove(file)
                                reco_found = True
                    except Exception as e:
                        print("ERROR: Error when loading file {0} - {1}". format(file, str(e)))
            # YAML
            if format == 'yaml' or format == 'yml':
                if (file.suffix == '.yaml') or (file.suffix == '.yml'):
                    # if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = yaml.safe_load(f)
                        f.close()
                        if 'guid' in v2reco:
                            if v2reco['guid'].lower() == guid.lower():
                                if verbose: print('DEBUG: deleting reco', guid, 'in file', file)
                                os.remove(file)
                                reco_found = True
                    except Exception as e:
                        print("ERROR: Error when loading file {0} - {1}". format(file, str(e)))
        # Return the object with all the v2 objects
        return reco_found
