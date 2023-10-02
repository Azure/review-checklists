import json
import os
import sys
import uuid
import argparse
import time
from azure.data.tables import TableServiceClient

# Get input arguments
parser = argparse.ArgumentParser(description='Translate a JSON file')
parser.add_argument('--account', dest='storage_account_name', action='store',
                    help='You need to supply the storage account name')
parser.add_argument('--key', dest='storage_account_key', action='store',
                    help='You need to supply the key for the storage account')
parser.add_argument('--input-file', dest='input_file', action='store',
                    help='You need to supply file name where the JSON checklist is located')

args = parser.parse_args()

# Variables
table_name = "checklist"
create_table_wait_interval = 10

# Get JSON
try:
    with open(args.input_file) as f:
        checklist = json.load(f)
except Exception as e:
    print("ERROR: Error when processing JSON file", args.file_name_in, "-", str(e))
    sys.exit(1)

# Create client
connection_string = "DefaultEndpointsProtocol=https;AccountName={0};AccountKey={1};EndpointSuffix=core.windows.net".format(args.storage_account_name, args.storage_account_key)
table_service_client = TableServiceClient.from_connection_string(conn_str=connection_string)

# Delete table
try:
    print("DEBUG: Deleting table {0}...".format(table_name))
    table_service_client.delete_table(table_name=table_name)
except Exception as e:
    print("INFO: Error deleting table {0}: {1}".format(table_name, str(e)))

# Create table
table_created = False
while not table_created:
    try:
        print("DEBUG: Creating table {0}...".format(table_name))
        table_client = table_service_client.create_table(table_name=table_name)
        table_created = True
    except Exception as e:
        print("ERROR: Error creating table {0}. Retrying in {2} seconds...".format(table_name, str(e), create_table_wait_interval))
    time.sleep(create_table_wait_interval)

# Upload checklist items
print ("DEBUG: adding items, this can take a few minutes...")
item_counter = 0
for item in checklist['items']:
    # print("DEBUG: uploading item #{0}: {1}".format(item_counter, str(item)))
    item["PartitionKey"] = item['category']
    item["RowKey"] = item['guid']
    try:
        entity = table_client.create_entity(entity=item)
    except Exception as e:
        print("ERROR: Error creating entity for item #{0} {1}: {2}".format(item_counter, str(item), str(e)))
        pass
    item_counter += 1

# Finish
print("{0} items were uploaded to {1}".format(item_counter, args.storage_account_name))