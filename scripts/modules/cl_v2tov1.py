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
from . import cl_v1tov2
import datetime


# Function that returns a data structure with the objects in v1 format
def generate_v1(checklist_file, input_folder, output_file, service_dictionary=None, verbose=False):
    # Get checklist object and full reco list
    checklist_v2 = cl_analyze_v2.get_checklist_object(checklist_file)
    recos_v2_full = cl_analyze_v2.get_recos(input_folder, verbose=False)
    recos_v1 = []
    area_index = 0
    subarea_index = 0
    reco_index = 0
    # Selectors can be at the checklist root, in an area, or a subarea
    if 'include' in checklist_v2:
        root_include_selectors = cl_analyze_v2.get_object_selectors(checklist_v2['include'])
        if 'exclude' in checklist_v2:
            root_exclude_selectors = cl_analyze_v2.get_object_selectors(checklist_v2['exclude'])
        else:
            root_exclude_selectors = None
        # Filter all recos according to the selectors
        root_recos_v2 = cl_analyze_v2.filter_v2_recos(recos_v2_full, include=root_include_selectors, exclude=root_exclude_selectors)
        if verbose: print("{0} recos extracted at root level".format(len(root_recos_v2)))
        recos_v1 += [get_v1_from_v2(x, service_dictionary=service_dictionary) | {'id': i+1} for i, x in enumerate(root_recos_v2)]
    if 'areas' in checklist_v2:
        for area in checklist_v2['areas']:
            if 'name' in area:
                area_index += 1
                subarea_index = 0
                if 'include' in area:
                    area_include_selectors = cl_analyze_v2.get_object_selectors(area['include'])
                    if 'exclude' in area:
                        area_exclude_selectors = cl_analyze_v2.get_object_selectors(area['exclude'])
                    else:
                        area_exclude_selectors = None
                    # Filter all recos according to the selectors
                    area_recos_v2 = cl_analyze_v2.filter_v2_recos(recos_v2_full, include=area_include_selectors, exclude=area_exclude_selectors)
                    if verbose: print("{0} recos extracted at area {1}".format(len(area_recos_v2), area['name']))
                    recos_v1 += [get_v1_from_v2(x, service_dictionary=service_dictionary) | {'category': area['name'], 'id': get_reco_id(i+1, subarea_index=None, area_index=area_index)} for i, x in enumerate(area_recos_v2)]
                else:
                    if verbose: print("WARNING: skipping area '{0}', no include specified.".format(area['name']))
                if 'subareas' in area:
                    for subarea in area['subareas']:
                        if 'name' in subarea:
                            subarea_index += 1
                            if 'include' in subarea:
                                subarea_include_selectors = cl_analyze_v2.get_object_selectors(subarea['include'])
                                if 'exclude' in subarea:
                                    subarea_exclude_selectors = cl_analyze_v2.get_object_selectors(subarea['exclude'])
                                else:
                                    subarea_exclude_selectors = None
                                # Filter all recos according to the selectors
                                subarea_recos_v2 = cl_analyze_v2.filter_v2_recos(recos_v2_full, include=subarea_include_selectors, exclude=subarea_exclude_selectors)
                                if verbose: print("{0} recos extracted at area '{1}', subarea '{2}'".format(len(subarea_recos_v2), area['name'], subarea['name']))
                                recos_v1 += [get_v1_from_v2(x, service_dictionary=service_dictionary) | {'category': area['name'], 'subcategory': subarea['name'], 'id': get_reco_id(i+1, subarea_index=subarea_index, area_index=area_index)} for i, x in enumerate(subarea_recos_v2)]
                            else:
                                if verbose: print("WARNING: skipping subarea '{0}' in area '{1}, no include specified.".format(subarea['name'], area['name']))
                        else:
                            if verbose: print("WARNING: Skipping subarea in area {0}, no name specified.".format(area['name']))
            else:
                if verbose: print("WARNING: Skipping area, no name specified.")
    # Build the rest of the checklist structure
    categories = list(set([x['category'] for x in recos_v1 if 'category' in x]))
    cat_object = [{'name': x.title()} for x in categories]
    waf_pillars = list(set([x['waf'] for x in recos_v1 if 'waf' in x]))
    waf_pillars_object = [{'name': x} for x in waf_pillars]
    checklist_v1 = {
        'items': recos_v1,
        'yesno': ({'name': 'Yes'}, {'name': 'No'}),
        'waf': waf_pillars_object,
        'categories': cat_object,
        'metadata': {'timestamp': datetime.date.today().strftime("%B %d, %Y")}
    }
    if 'name' in checklist_v2:
        checklist_v1['metadata']['name'] = checklist_v2['name']
    else:
        checklist_v1['metadata']['name'] = 'Name missing from checklist YAML file'
    # Write the output file
    if verbose: print("DEBUG: Writing file", output_file)
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(checklist_v1, f, indent=4)

# Function that returns a string ID for a reco of the format A01.01
# Area and subarea are optional, but the reco_index is mandatory
def get_reco_id (reco_index, subarea_index=None, area_index=None):
    if reco_index:
        reco_id = str(reco_index).zfill(2)
        if subarea_index:
            reco_id = str(subarea_index).zfill(2) + '.' + reco_id
        if area_index:
            reco_id = chr(area_index + 64) + reco_id
        return reco_id
    else:
        return None

# Function that returns a single v1 reco out of a single v2 reco:
def get_v1_from_v2(reco_v2, service_dictionary=None):
    reco_v1 = {}
    # GUID (not mandatory in v2)
    if 'guid' in reco_v2:
        reco_v1['guid'] = reco_v2['guid']
    elif 'labels' in reco_v2 and 'guid' in reco_v2['labels']:
        reco_v1['guid'] = reco_v2['labels']['guid']
    # Mandatory fields
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
    # Services not there in v2
    if 'services' in reco_v2:
        reco_v1['service'] = reco_v2['service'][0]
    elif 'resourceTypes' in reco_v2 and len(reco_v2['resourceTypes']) > 0:
        reco_v1['service'] = cl_v1tov2.get_standard_service_name(reco_v2['resourceTypes'][0], service_dictionary=service_dictionary)
    if 'waf' in reco_v2:
        reco_v1['waf'] = reco_v2['waf']
    return reco_v1