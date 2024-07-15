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
            for label in reco['labels']:
                for thislabelkey in label.keys():
                    labeltext = thislabelkey + ": " + label[thislabelkey]
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