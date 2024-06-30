#################################################################################
#
# This script tries to merge different WAF checklists (WAF, review, svc guides).
# It tries to find duplicates calculating the distance between strings with embeddings.
# 
# Last updated: June 2024
#
#################################################################################

import json
import argparse
import sys
from sentence_transformers import SentenceTransformer

# Get input arguments
parser = argparse.ArgumentParser(description='Merge different WAF checklists and removes duplicates')
parser.add_argument('--review_checklist-file', dest='review_checklist_file', action='store',
                    help='You need to supply the name of the JSON file with the review checklist to be merged')
parser.add_argument('--aprl_checklist-file', dest='aprl_checklist_file', action='store',
                    help='You need to supply the name of the JSON file with the APRL checklist to be merged')
parser.add_argument('--sg_checklist-file', dest='sg_checklist_file', action='store',
                    help='You need to supply the name of the JSON file with the Service Guide checklist to be merged')
parser.add_argument('--max-recos', dest='max_recos', action='store',
                    default=0,
                    help='You can optionally define a maximum of recos to process. If 0 (default), no limit is set.')
parser.add_argument('--save', dest='save', action='store_true',
                    default=False,
                    help='Whether results will be stored in the provided files (default: False)')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='Run in verbose mode (default: False)')
args = parser.parse_args()

# Function to load a checklist stored in a JSON file
def load_json_file(filename):
    try:
        with open(filename) as f:
            checklist = json.load(f)
    except Exception as e:
        print("ERROR: Error when loading review checklist JSON file", args.review_checklist_file, "-", str(e))
        sys.exit(1)
    if 'items' in checklist:
        if args.verbose: print('DEBUG: {0} recos loaded from {1}'.format(len(checklist['items']), filename))
    else:
        print('ERROR: checklist in file {0} does not have an "items" element.'.format(filename))
    return checklist

# Dump JSON object to file
def dump_json_file(json_object, filename):
    if args.verbose:
        print("DEBUG: dumping JSON object to file", filename)
    json_string = json.dumps(json_object, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(json_string)
        f.close()


# Function to calculate text embeddings
# See https://stackoverflow.com/questions/65199011/is-there-a-way-to-check-similarity-between-two-full-sentences-in-python
def calculate_embeddings(checklist, model):
    for reco in checklist['items']:
        if not ('embeddings' in reco):
            if 'text' in reco:
                embeddings = model.encode(reco['text'])
                reco['embeddings'] = embeddings
                if args.verbose: print('DEBUG: calculated embeddings for {0}: {1}'.format(reco['text'], str(embeddings))) 

    # texts = [x['text'] for x in checklist['items']]
    # text_embeddings = model.encode(texts)

###############
#    Begin    #
###############

# Load the checklists
review_checklist = load_json_file(args.review_checklist_file)
aprl_checklist = load_json_file(args.aprl_checklist_file)
# sg_checklist = load_json_file(args.sg_checklist_file)

# Calculate the embeddings for each reco
model = SentenceTransformer('distilbert-base-nli-mean-tokens')
# model = SentenceTransformer("all-MiniLM-L6-v2")
if (args.verbose): print('Calculating embeddings for review checklist...')
review_checklist = calculate_embeddings(review_checklist, model)
if (args.verbose): print('Calculating embeddings for APRL checklist...')
aprl_checklist = calculate_embeddings(aprl_checklist, model)
# if (args.verbose): print('Calculating embeddings for Service Guide checklist...')
# sg_checklist = calculate_embeddings(sg_checklist, model)

# If we want to save the results so that we don't calculate again
dump_json_file(review_checklist, args.review_checklist_file)
dump_json_file(aprl_checklist, args.aprl_checklist_file)
dump_json_file(sg_checklist, args.sg_checklist_file)
