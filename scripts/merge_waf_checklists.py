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

# Get input arguments
parser = argparse.ArgumentParser(description='Merge different WAF checklists and removes duplicates')
parser.add_argument('--review-checklist-file', dest='review_checklist_file', action='store',
                    help='You need to supply the name of the JSON file with the review checklist to be merged (default: None)')
parser.add_argument('--aprl-checklist-file', dest='aprl_checklist_file', action='store',
                    help='You need to supply the name of the JSON file with the APRL checklist to be merged (default: None)')
parser.add_argument('--sg-checklist-file', dest='sg_checklist_file', action='store',
                    help='You need to supply the name of the JSON file with the Service Guide checklist to be merged (default: None)')
parser.add_argument('--output-file', dest='output_file', action='store',
                    help='The resulting checklist will be stored here (default: None)')
parser.add_argument('--service-dictionary', dest='service_dictionary', action='store',
                    help='JSON file with dictionary to map services to standard names and to ARM services')
parser.add_argument('--calculate-embeddings', dest='calculate_embeddings', action='store_true',
                    default=False,
                    help='Whether embeddings and reco mappings will be calculated (default: False)')
parser.add_argument('--save-embeddings', dest='save_embeddings', action='store_true',
                    default=False,
                    help='Whether calculated embeddings will be stored in the provided files (default: False)')
parser.add_argument('--max-recos', dest='max_recos', action='store',
                    type=int, default=0,
                    help='You can optionally define a maximum of recos to process for embeddings. If 0 (default), no limit is set.')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='Run in verbose mode (default: False)')
args = parser.parse_args()

# Only import module if we are going to use it
if (args.calculate_embeddings):
    from sentence_transformers import SentenceTransformer, util


# Function to load a checklist stored in a JSON file
def load_json_file(filename):
    try:
        with open(filename) as f:
            checklist = json.load(f)
    except Exception as e:
        print("ERROR: Error when loading review checklist JSON file", filename, "-", str(e))
        sys.exit(1)
    if 'items' in checklist:
        if args.verbose: print('DEBUG: {0} recos loaded from {1}'.format(len(checklist['items']), filename))
    else:
        print('ERROR: checklist in file {0} does not have an "items" element.'.format(filename))
        sys.exit(1)
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
    if (args.verbose): print('DEBUG: Calculating embeddings for checklist ({0} recos)...'.format(len(checklist['items'])))
    counter = 0
    for reco in checklist['items']:
        counter += 1
        if not ('embeddings' in reco):
            if (counter % 100 == 0):
                if (args.verbose): print('DEBUG: {0} recos processed'.format(counter))
            if 'text' in reco:
                embeddings = model.encode(reco['text'])
                reco['embeddings'] = embeddings
                # if args.verbose: print('DEBUG: calculated embeddings for {0}: {1}'.format(reco['text'], str(embeddings)))
            else:
                if args.verbose: print('DEBUG: Missing "text" tag in recommendation')
    # texts = [x['text'] for x in checklist['items']]
    # text_embeddings = model.encode(texts)
    return checklist

# Verify that text and embeddings are present in the items of a checklist
def verify_checklist(checklist):
    items_count = len(checklist['items'])
    items_with_text_count = len([x for x in checklist['items'] if 'text' in x])
    items_with_embeddings_count = len([x for x in checklist['items'] if 'embeddings' in x])
    if (args.verbose): print('DEBUG: checklist analysis: {0} elements in total, {1} elements with "text" key, {2} elements with "embeddings" key.'.format(items_count, items_with_text_count, items_with_embeddings_count))

# Get the standard service name from the service dictionary
def get_standard_service_name(service_name, service_dictionary=None):
    if service_name in service_dictionary:
        return service_dictionary[service_name]['service']
    else:
        return service_name

# Get the standard WAF pillar name (Title case)
def get_standard_waf_pillar_name(waf_pillar_name):
    if waf_pillar_name.lower() in ('reliability', 'resiliency'):
        return 'Reliability'
    elif waf_pillar_name.lower() in ('cost', 'cost optimization', 'cost efficiency'):
        return 'Cost'
    if waf_pillar_name.lower() in ('performance', 'scalability'):
        return 'Performance'
    if waf_pillar_name.lower() in ('operations', 'operational excellence'):
        return 'Operations'
    if waf_pillar_name.lower() in ('security'):
        return 'Reliability'
    else:
        return waf_pillar_name.title()


###############
#    Begin    #
###############

# Load the checklists
review_checklist = load_json_file(args.review_checklist_file)
aprl_checklist = load_json_file(args.aprl_checklist_file)
sg_checklist = load_json_file(args.sg_checklist_file)

# Calculate the embeddings for each reco and the closest reco in another checklist
if args.calculate_embeddings:
    model = SentenceTransformer('distilbert-base-nli-mean-tokens')
    # model = SentenceTransformer("all-MiniLM-L6-v2")
    review_checklist = calculate_embeddings(review_checklist, model)
    aprl_checklist = calculate_embeddings(aprl_checklist, model)
    sg_checklist = calculate_embeddings(sg_checklist, model)

    # Verify that we have all we need
    verify_checklist(review_checklist)
    verify_checklist(aprl_checklist)
    verify_checklist(sg_checklist)

    # For every reco of the WAF service guide checklist, try to find the one in the others which is closest
    sg_reco_count = 0
    for sg_reco in sg_checklist['items']:
        # It would be more efficient only running the distance algorithm in the recos matching service and WAF pillar,
        #  but especially the service might not match ('Azure Kubernetes Service' vs 'AKS', 'Reliability' vs 'Resiliency', etc)
        sg_reco_count += 1
        if (sg_reco_count <= args.max_recos) or (args.max_recos == 0):
            if 'embeddings' in sg_reco:
                min_distance = 100
                matching_reco = None
                for review_reco in review_checklist['items']:
                    if 'embeddings' in review_reco:
                        this_distance = util.pytorch_cos_sim(sg_reco['embeddings'], review_reco['embeddings'])
                        if this_distance < min_distance:
                            min_distance = this_distance
                            matching_reco = review_reco
                    else:
                        print('ERROR: Embeddings missing from review reco')
                if min_distance < 0.05:
                    if (args.verbose):
                        print('DEBUG: Match with distance {0}'.format(min_distance))
                        print('DEBUG:    SG reco    : {0}'.format(sg_reco['text']))
                        print('DEBUG:    Review reco: {0}'.format(matching_reco['text']))
            else:
                print('ERROR: Embeddings missing from SG reco')
        else:
            break
    if (sg_reco_count > args.max_recos) and (args.max_recos > 0):
        if (args.verbose): print('DEBUG: maximum number of recos provided ({0}) reached'.format(args.max_recos))

# Merge all three checklists in one
full_checklist = review_checklist
full_checklist['items'] += aprl_checklist['items']
full_checklist['items'] += sg_checklist['items']
# Standardize the service names with the service dictionary (if one provided)
if args.service_dictionary:
    service_dictionary = None
    try:
        with open(args.service_dictionary) as f:
            service_dictionary = json.load(f)
            if args.verbose:
                print("DEBUG: service dictionary loaded successfully")
    except Exception as e:
        print("ERROR: Error when loading service dictionary from", args.service_dictionary, "-", str(e))
    if service_dictionary:
        for item in full_checklist['items']:
            if 'service' in item:
                item['service'] = get_standard_service_name(item['service'], service_dictionary=service_dictionary)
# Standardize the WAF pillar names
for item in full_checklist['items']:
    if 'waf' in item:
        item['waf'] = get_standard_waf_pillar_name(item['waf'])
# If an output file was specified, save the resulting checklist
if args.output_file:
    dump_json_file(full_checklist, args.output_file)
    if (args.verbose): print('DEBUG: Merged checklist with {0} elements saved to {1}'.format(len(full_checklist['items']), args.output_file))

# If we want to save the results so that we don't calculate again
if args.save_embeddings:
    dump_json_file(review_checklist, args.review_checklist_file)
    dump_json_file(aprl_checklist, args.aprl_checklist_file)
    dump_json_file(sg_checklist, args.sg_checklist_file)
