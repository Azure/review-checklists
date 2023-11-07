#################################################################################
#
# This script verifies a specific checklist for correctness.
# 
# Last updated: November 2023
#
#################################################################################

import json
import argparse
import sys
import requests

# Get input arguments
parser = argparse.ArgumentParser(description='Verify a JSON checklist for correctness')
parser.add_argument('--input-file', dest='input_file', action='store',
                    help='You need to supply the name of the JSON file with the checklist to be filtered')
parser.add_argument('--verbose', dest='verbose', action='store_true',
                    default=False,
                    help='run in verbose mode (default: False)')
args = parser.parse_args()

# We need an input file
if not args.input_file:
    print("ERROR: no input file specified, not doing anything")

# Look for non-unicode characters in the file
print("Verifying all characters are Unicode-8...")
f1 = open (args.input_file, "r")
text = f1.read()
for line in text:
    for character in line:
        if ord(character) > 127:
            print("ERROR: non-unicode character found in file", args.input_file, "-", character)
            sys.exit(1)
print("OK: All characters are Unicode-8")

# Reading into JSON
print("Verifying JSON can be loaded up...")
try:
    with open(args.input_file) as f:
        checklist = json.load(f)
except Exception as e:
    print("ERROR: Error when processing JSON file, nothing changed", args.input_file, "-", str(e))
    sys.exit(1)
print("OK: JSON can be loaded up")
