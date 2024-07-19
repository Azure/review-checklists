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
import cl_analyze_v2

# Function that returns a data structure with the objects in v1 format
def generate_v1(checklist_file, input_folder, verbose=False):
    # Get selectors from checklist file
    labels, services, waf_pillars = cl_analyze_v2.get_checklist_selectors(checklist_file)
    # Get recos from v2 files
