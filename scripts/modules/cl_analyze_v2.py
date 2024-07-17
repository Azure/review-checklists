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
def reco_matches_criteria(reco, labels=None, services=None, waf_pillars=None, guid=None):
    # Check if the reco fulfills the criteria
    if guid:
        guid_match = False
        if 'guid' in reco:
            if reco['guid'].lower() == guid.lower():
                return True
    else:
        guid_match = True
    if labels:
        label_match = False
        if 'labels' in reco:
            for key in labels.keys():
                if key in reco['labels']:
                    if labels[key] == reco['labels'][key]:
                        label_match = True
    else:
        label_match = True
    if services:
        service_match = False
        if 'none' in services:
            service_match = ('service' not in reco)
        if 'service' in reco:
            if reco['service'].lower() in services:
                service_match = True
    else:
        service_match = True
    if waf_pillars:
        waf_match = False
        if 'none' in waf_pillars:
            waf_match = ('waf' not in reco)
        if 'waf' in reco:
            if reco['waf'].lower() in waf_pillars:
                waf_match = True
    else:
        waf_match = True
    # If no selector was provided, add all recos to the list
    return (guid_match and label_match and service_match and waf_match)

# Function that loads all of the found v2 YAML/JSON files into a single object
def load_v2_files(input_folder, format='yaml', labels=None, services=None, waf_pillars=None, guid=None, verbose=False):
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
            if format == 'json':
                if file.suffix == '.json':
                    if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = json.safe_load(f)
                            if reco_matches_criteria(v2reco, labels=labels, services=services, waf_pillars=waf_pillars, guid=guid):
                                v2recos.append(v2reco)
                    except Exception as e:
                        print("ERROR: Error when loading file {0} - {1}". format(file, str(e)))
            if format == 'yaml' or format == 'yml':
                if (file.suffix == '.yaml') or (file.suffix == '.yml'):
                    if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = yaml.safe_load(f)
                            if reco_matches_criteria(v2reco, labels=labels, services=services, waf_pillars=waf_pillars, guid=guid):
                                v2recos.append(v2reco)
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
    # Return the stats object
    return stats

# Return an object with some statistics about the v2 objects in a folder
def v2_stats_from_folder(input_folder, format='yaml', labels=None, services=None, waf_pillars=None, verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, labels=labels, services=services, waf_pillars=waf_pillars, verbose=verbose)
    # Get the stats from the v2 objects
    stats = v2_stats_from_object(v2recos, verbose=verbose)
    # Return the stats object
    return stats

# Return an object with the recos fulfilling the specified criteria
def get_recos(input_folder, labels=None, services=None, waf_pillars=None, format='yaml', verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, verbose=verbose)
    if v2recos:
        # Create a list of recos that fulfill the criteria
        recos = []
        for reco in v2recos:
            if reco_matches_criteria(reco, labels=labels, services=services, waf_pillars=waf_pillars):
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

# Print in screen a v2 recommendation in one line with fixed width columns
def print_recos(recos, show_labels=False):
    print("{0:<37} {1:<80} {2:<30} {3:<15}".format('GUID', 'TEXT', 'SERVICE', 'WAF'), end="")
    if show_labels:
        print("{0:<40}".format("LABELS"), end="")
    print()
    print("{0:<37} {1:<80} {2:<30} {3:<15}".format('====', '====', '=======', '==='), end="")
    if show_labels:
        print("{0:<40}".format("======"), end="")
    print()
    for reco in recos:
        guid=reco['guid'] if 'guid' in reco else ''
        text=reco['text'] if 'text' in reco else ''
        service=reco['service'] if 'service' in reco else ''
        waf=reco['waf'] if 'waf' in reco else ''
        print("{0:<37} {1:<80} {2:<30} {3:<15}".format(guid, text[:79], service[:29], waf), end="")
        if show_labels:
            if 'labels' in reco:
                print("{0:<40}".format(str(reco['labels'])), end="")
        print()
    print("   {0} recommendations listed".format(len(recos)))
