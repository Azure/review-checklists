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
from collections import Counter

# Function that returns true if a given reco matches the criteria specified by a label selector, a service selector and a WAF selector
def reco_matches_criteria(reco, labels=None, services=None, resource_types=None, waf_pillars=None, sources=None, guids=None, names=None, arg=False):
    # Check if the reco fulfills the criteria
    # GUID
    if guids:
        guid_match = False
        if 'guid' in reco:
            guids_lower = [x.lower() for x in guids]
            if reco['guid'].lower() in guids_lower:
                return True
    else:
        guid_match = True
    # Names
    if names:
        name_match = False
        if 'name' in reco:
            names_lower = [x.lower() for x in names]
            if reco['name'].lower() in names_lower:
                return True
    else:
        name_match = True
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
    else:
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
    return (guid_match and name_match and label_match and service_match and resource_type_match and waf_match and arg_match and src_match)

# Extracts certain recos based on include and optionally exclude selectors
def filter_v2_recos(input_recos, include=None, exclude=None):
    if include:
        waf_pillars = include['waf']
        services = include['service']
        resource_types = include['resourceType']
        guids = include['guid']
        names = include['name']
        labels = include['label']
        sources = include['source']
        output_recos_include = [x for x in input_recos if reco_matches_criteria(x, waf_pillars=waf_pillars, services=services, resource_types=resource_types, guids=guids, names=names, sources=sources, labels=labels)]
        # There might be exclude selectors too
        if exclude:
            waf_pillars = exclude['waf']
            services = exclude['service']
            resource_types = exclude['resourceType']
            guids = exclude['guid']
            names = include['name']
            labels = exclude['label']
            sources = exclude['source']
            output_recos = [x for x in output_recos_include if not reco_matches_criteria(x, waf_pillars=waf_pillars, services=services, resource_types=resource_types, guids=guids, names=names, sources=sources, labels=labels)]
        else:
            output_recos = output_recos_include
        return output_recos
    else:
        # If no include selectors specified, return nothing
        return None

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
def load_v2_files(input_folder, format='yaml', labels=None, services=None, waf_pillars=None, sources=None, guids=None, arg=False, open_editor=False, text_editor=None, verbose=False):
    # Banner
    if verbose: print("DEBUG: Loading v2 files from folder", input_folder)
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
                            if reco_matches_criteria(v2reco, labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, guids=guids):
                                if verbose: print("DEBUG: reco in file", file, "matches criteria.")
                                v2recos.append(v2reco)
                                if open_editor:
                                    open_file_with_editor(file, text_editor=text_editor, verbose=verbose)
                    except Exception as e:
                        print("ERROR: Error when loading JSON reco file {0} - {1}". format(file, str(e)))
            # YAML
            if format == 'yaml' or format == 'yml':
                if (file.suffix == '.yaml') or (file.suffix == '.yml'):
                    # if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = yaml.safe_load(f)
                            if reco_matches_criteria(v2reco, labels=labels, services=services, waf_pillars=waf_pillars, guids=guids, arg=arg):
                                if verbose: print("DEBUG: reco in file", file, "matches criteria.")
                                v2recos.append(v2reco)
                                if open_editor:
                                    open_file_with_editor(file, text_editor=text_editor, verbose=verbose)
                    except Exception as e:
                        print("ERROR: Error when loading YAML reco file {0} - {1}". format(file, str(e)))
        # Return the object with all the v2 objects
        return v2recos
    else:
        print("ERROR: Input folder", input_folder, "does not exist.")
        return None

# Return an object with some statistics about the v2 objects 
def v2_stats_from_object(v2recos, verbose=False):
    # Banner
    if verbose: print("DEBUG: Analyzing v2 objects...")
    # Create a dictionary with the stats
    stats = {}
    if v2recos:
        stats['total_items'] = len(v2recos)
    else:
        stats['total_items'] = 0
    stats['severity'] = {}
    stats['labels'] = {}
    stats['services'] = {}
    stats['waf'] = {}
    stats['sources'] = {}
    stats['resourceTypes'] = {}
    stats['areas'] = {}
    if v2recos:
        # Find GUID and name duplicates
        guid_list = [reco['guid'] for reco in v2recos if 'guid' in reco]
        guid_counts = Counter(guid_list)
        stats['duplicate_guids'] = [item for item, count in guid_counts.items() if count > 1]
        name_list = [reco['name'] for reco in v2recos if 'name' in reco]
        name_counts = Counter(name_list)
        stats['duplicate_names'] = [item for item, count in name_counts.items() if count > 1]
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
            if 'services' in reco:
                for service in reco['services']:
                    if service in stats['services']:
                        stats['services'][service] += 1
                    else:
                        stats['services'][service] = 1
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
            # Areas / subareas
            if 'area' in reco:
                if 'subarea' in reco:
                    if reco['area'] + ' | ' + reco['subarea'] in stats['areas']:
                        stats['areas'][reco['area'] + ' | ' + reco['subarea']] += 1
                    else:
                        stats['areas'][reco['area'] + ' | ' + reco['subarea']] = 1
                else:
                    if reco['area'] in stats['areas']:
                        stats['areas'][reco['area']] += 1
                    else:
                        stats['areas'][reco['area']] = 1
            else:
                if 'undefined' in stats['areas']:
                    stats['areas']['undefined'] += 1
                else:
                    stats['areas']['undefined'] = 1
        # Return the stats object
        return stats
    else:
        print("ERROR: no recos to analyze for statistics.")
        return stats

# Return an object with some statistics about the v2 objects in a checklist
def v2_stats_from_checklist(checklist_file, input_folder, format='yaml', verbose=False):
    # Load the v2 objects from the checklist
    v2recos = get_recos_from_checklist(checklist_file, input_folder, verbose)
    if v2recos:
        if verbose: print("DEBUG: {0} v2 objects extracted, calculating stats...".format(len(v2recos)))
        # Get the stats from the v2 objects
        stats = v2_stats_from_object(v2recos, verbose=verbose)
        # Return the stats object
        return stats
    else:
        print("ERROR: no recos could be loaded from checklist", checklist_file)
        return None

# Return an object with some statistics about the v2 objects in a folder
def v2_stats_from_folder(input_folder, format='yaml', labels=None, services=None, waf_pillars=None, sources=None, verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, verbose=verbose)
    # Get the stats from the v2 objects
    stats = v2_stats_from_object(v2recos, verbose=verbose)
    # Return the stats object
    return stats

# Return an object with the recos fulfilling the specified criteria
# ToDo: the parameter guid should be an array, to support a list of guids
def get_recos(input_folder, labels=None, services=None, waf_pillars=None, sources=None, guids=None, arg=False, format='yaml', verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, verbose=verbose)
    if v2recos:
        # Create a list of recos that fulfill the criteria
        recos = []
        for reco in v2recos:
            if reco_matches_criteria(reco, labels=labels, services=services, waf_pillars=waf_pillars, sources=sources, guids=guids, arg=arg):
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
    v2recos = load_v2_files(input_folder, guids=[guid], format='yaml', verbose=verbose)
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
def get_object_selectors(checklist_object, verbose=False):
    # Label
    if 'labelSelector' in checklist_object:
        labelSelector = checklist_object['labelSelector']
        for key in labelSelector.keys():
            print ("DEBUG: Label selector found:", key + ":" + labelSelector[key])
    else:
        labelSelector = None
    # Service
    if 'serviceSelector' in checklist_object:
        serviceSelector = checklist_object['serviceSelector']
        for service in serviceSelector:
            print ("DEBUG: Service selector found:", service)
    else:
        serviceSelector = None
    # ResourceType
    if 'resourceTypeSelector' in checklist_object:
        resourceTypeSelector = checklist_object['resourceTypeSelector']
        for resourceType in resourceTypeSelector:
            print ("DEBUG: resourceType selector found:", resourceType)
    else:
        resourceTypeSelector = None
    # WAF
    if 'wafSelector' in checklist_object:
        wafSelector = checklist_object['wafSelector']
        for waf in wafSelector:
            print ("DEBUG: WAF selector found:", waf)
    else:
        wafSelector = None
    # GUID
    if 'guidSelector' in checklist_object:
        guidSelector = checklist_object['guidSelector']
        for guid in guidSelector:
            print ("DEBUG: GUID selector found:", guid)
    else:
        guidSelector = None
    # Names
    if 'nameSelector' in checklist_object:
        nameSelector = checklist_object['nameSelector']
        for name in nameSelector:
            print ("DEBUG: name selector found:", name)
    else:
        nameSelector = None
    # Source
    if 'sourceSelector' in checklist_object:
        sourceSelector = checklist_object['sourceSelector']
        for source in sourceSelector:
            print ("DEBUG: source selector found:", source)
    else:
        sourceSelector = None
    # Return the selectors
    return {
        'label': labelSelector,
        'source': sourceSelector,
        'service': serviceSelector,
        'waf': wafSelector,
        'resourceType': resourceTypeSelector,
        'guid': guidSelector,
        'name': nameSelector
    }

# Loads a checklist file in YAML format
def get_checklist_object(checklist_file, verbose=False):
    # Load the checklist file
    try:
        if verbose: print("DEBUG: Loading checklist file", checklist_file)
        with open(checklist_file) as f:
            checklist = yaml.safe_load(f)
            return checklist
    except Exception as e:
        print("ERROR: Error when loading checklist file {0} - {1}". format(checklist_file, str(e)))
        return None

# Return v2 recos that match the selectors included in a checklist file
def get_recos_from_checklist(checklist_file, input_folder, verbose=False):
    # Get checklist object and full reco list
    checklist_v2 = get_checklist_object(checklist_file, verbose)
    if not checklist_v2:
        print("ERROR: Checklist file could not be loaded.")
        return None
    if verbose: print("DEBUG: Loading recos from folder", input_folder)
    recos_v2_full = get_recos(input_folder, verbose=False)  # Loading all recos, verbose not needed
    recos_v2 = []
    # Selectors can be at the checklist root, in an area, or a subarea
    if 'include' in checklist_v2:
        root_include_selectors = get_object_selectors(checklist_v2['include'])
        if 'exclude' in checklist_v2:
            root_exclude_selectors = get_object_selectors(checklist_v2['exclude'])
        else:
            root_exclude_selectors = None
        # Filter all recos according to the selectors
        root_recos_v2 = filter_v2_recos(recos_v2_full, include=root_include_selectors, exclude=root_exclude_selectors)
        recos_v2 += root_recos_v2
        if verbose: print("DEBUG: {0} recos extracted at root level, reco list at {1} elements".format(len(root_recos_v2), len(recos_v2)))
    if 'areas' in checklist_v2:
        for area in checklist_v2['areas']:
            if 'name' in area:
                if 'include' in area:
                    area_include_selectors = get_object_selectors(area['include'])
                    if 'exclude' in area:
                        area_exclude_selectors = get_object_selectors(area['exclude'])
                    else:
                        area_exclude_selectors = None
                    # Filter all recos according to the selectors
                    area_recos_v2 = filter_v2_recos(recos_v2_full, include=area_include_selectors, exclude=area_exclude_selectors)
                    recos_v2 += [x | {'area': area['name']} for x in area_recos_v2]
                    if verbose: print("DEBUG: {0} recos extracted at area {1}, reco list at {2} elements".format(len(area_recos_v2), area['name'], len(recos_v2)))
                if 'subareas' in area:
                    for subarea in area['subareas']:
                        if 'name' in subarea:
                            if 'include' in subarea:
                                subarea_include_selectors = get_object_selectors(subarea['include'])
                                if 'exclude' in subarea:
                                    subarea_exclude_selectors = get_object_selectors(subarea['exclude'])
                                else:
                                    subarea_exclude_selectors = None
                                # Filter all recos according to the selectors
                                subarea_recos_v2 = filter_v2_recos(recos_v2_full, include=subarea_include_selectors, exclude=subarea_exclude_selectors)
                                recos_v2 += [x | {'area': area['name'], 'subarea': subarea['name']} for x in subarea_recos_v2]
                                if verbose: print("DEBUG: {0} recos extracted at area '{1}', subarea '{2}', reco list at {3} elements".format(len(subarea_recos_v2), area['name'], subarea['name'], len(recos_v2)))
                            else:
                                if verbose: print("WARNING: skipping subarea '{0}' in area '{1}, no include specified.".format(subarea['name'], area['name']))
                        else:
                            if verbose: print("WARNING: Skipping subarea in area {0}, no name specified.".format(area['name']))
            else:
                if verbose: print("WARNING: Skipping area, no name specified.")
    # Return the recos object
    return recos_v2

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
                                if verbose: print('DEBUG: Deleting reco', guid, 'in file', file)
                                os.remove(file)
                                reco_found = True
                    except Exception as e:
                        print("ERROR: Error when loading reco file {0} - {1}". format(file, str(e)))
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
                        print("ERROR: Error when loading reco file {0} - {1}". format(file, str(e)))
        # Return the object with all the v2 objects
        return reco_found

# Function that returns a reco name provided its GUID. It takes as argument an object with the full list of recos
def get_reco_name_from_guid(recos, guid):
    for reco in recos:
        if 'guid' in reco:
            if reco['guid'].lower() == guid.lower():
                if 'name' in reco:
                    return reco['name']
                else:
                    return None
    return None