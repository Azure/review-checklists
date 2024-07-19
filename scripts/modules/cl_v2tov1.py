#######################################
#
# Module to generate v1-formatted checklists
#   from v2-formatted recommendations.
#
#######################################

# Dependencies
import sys
import yaml
import json
import os
from pathlib import Path
from . import cl_analyze_v2
import datetime

# Function that returns a data structure with the objects in v1 format
def generate_v1(checklist_file, input_folder, output_file, verbose=False):
    # Get selectors from checklist file
    labels, services, waf_pillars, variables = cl_analyze_v2.get_checklist_selectors(checklist_file)
    checklist_v2 = cl_analyze_v2.get_checklist_object(checklist_file)
    # Get recos from v2 files
    recos_v2 = cl_analyze_v2.get_recos(input_folder, labels=labels, services=services, waf_pillars=waf_pillars, verbose=verbose)
    # Convert them to v1 format
    recos_v1 = []
    for reco_v2 in recos_v2:
        reco_v1 = {}
        # Main fields
        reco_v1['guid'] = reco_v2['guid']
        if 'title' in reco_v2:
            reco_v1['text'] = reco_v2['title']
        elif 'text' in reco_v2:     # Legacy
            reco_v1['text'] = reco_v2['text']
        if 'description' in reco_v2:
            reco_v1['description'] = reco_v2['description']
        if 'severity' in reco_v2:
            if reco_v2['severity'] == 0:
                reco_v1['severity'] = 'High'
            elif reco_v2['severity'] == 1:
                reco_v1['severity'] = 'Medium'
            elif reco_v2['severity'] == 2:
                reco_v1['severity'] = 'Low' 
        if 'service' in reco_v2:
            reco_v1['service'] = reco_v2['service']
        if 'waf' in reco_v2:
            reco_v1['waf'] = reco_v2['waf']
        # ID, area and subarea
        if 'idLabel' in variables:
            if variables['idLabel'] in reco_v2['labels']:
                reco_v1['id'] = reco_v2['labels'][variables['idLabel']]
        if 'catLabel' in variables:
            if variables['catLabel'] in reco_v2['labels']:
                reco_v1['category'] = reco_v2['labels'][variables['catLabel']]
        if 'subcatLabel' in variables:
            if variables['subcatLabel'] in reco_v2['labels']:
                reco_v1['subcategory'] = reco_v2['labels'][variables['subcatLabel']]
        recos_v1.append(reco_v1)
    # Build the whole checklist structure
    categories = list(set([x['category'] for x in recos_v1 if 'category' in x]))
    cat_object = [{'name': x.title()} for x in categories]
    waf_pillars = list(set([x['waf'] for x in recos_v1 if 'waf' in x]))
    waf_pillars_object = [{'name': x} for x in waf_pillars]
    checklist_v1 = {
        'items': recos_v1,
        'yesno': ({'name': 'Yes'}, {'name': 'No'}),
        'waf': waf_pillars_object,
        'categories': cat_object,
        'metadata': {'name': checklist_v2['name'], 'timestamp': datetime.date.today().strftime("%B %d, %Y")}
    }
    # Write the output file
    if verbose: print("DEBUG: Writing file", output_file)
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(checklist_v1, f, indent=4)

