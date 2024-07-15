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

# Function that loads all of the found v2 YAML/JSON files into a single object
def load_v2_files(input_folder, format='yaml', verbose=False):
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
                            v2recos.append(v2reco)
                    except Exception as e:
                        print("ERROR: Error when loading file {0} - {1}". format(file, str(e)))
            if format == 'yaml' or format == 'yml':
                if (file.suffix == '.yaml') or (file.suffix == '.yml'):
                    if verbose: print("DEBUG: Loading file", file)
                    try:
                        with open(file.resolve()) as f:
                            v2reco = yaml.safe_load(f)
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
    for reco in v2recos:
        # Count the number of items per severity
        if reco['severity'] in stats['severity']:
            stats['severity'][reco['severity']] += 1
        else:
            stats['severity'][reco['severity']] = 1
        # Count the number of items per area
        if 'labels' in reco:
                for thislabelkey in reco['labels'].keys():
                    labeltext = thislabelkey + ":" + reco['labels'][thislabelkey]
                    if labeltext in stats['labels']:
                        stats['labels'][labeltext] += 1
                    else:
                        stats['labels'][labeltext] = 1
    # Return the stats object
    return stats

# Return an object with some statistics about the v2 objects in a folder
def v2_stats_from_folder(input_folder, format='yaml', verbose=False):
    # Load the v2 objects from the folder
    v2recos = load_v2_files(input_folder, format=format, verbose=verbose)
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
            # Check if the reco fulfills the criteria
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
                if 'service' in reco:
                    if reco['service'].lower() in services:
                        service_match = True
            else:
                service_match = True
            if waf_pillars:
                waf_match = False
                if 'waf' in reco:
                    if reco['waf'].lower() in waf_pillars:
                        waf_match = True
            else:
                waf_match = True
            # If no selector was provided, add all recos to the list
            if label_match and service_match and waf_match:
                recos.append(reco)
        # Return the recos object
        return recos
    else:
        print("ERROR: no recos could be loaded from folder", input_folder)

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
