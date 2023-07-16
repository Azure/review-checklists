import json
import os
import sys
import uuid
import argparse
from azure.core.exceptions import AzureError
from azure.cosmos import CosmosClient, PartitionKey
import azure.cosmos.exceptions as exceptions

# Get input arguments
parser = argparse.ArgumentParser(description='Translate a JSON file')
parser.add_argument('--cosmosdb-url', dest='cosmosdb_url', action='store',
                    help='You need to supply the URL to access your Cosmos DB')
parser.add_argument('--cosmosdb-key', dest='cosmosdb_key', action='store',
                    help='You need to supply a read/write key to access your CosmosDB')
parser.add_argument('--input-file', dest='input_file', action='store',
                    help='You need to supply file name where the JSON checklist is located')

args = parser.parse_args()

# Variables
db_name = "checklist"
container_name = "checklist"

# Get JSON
try:
    with open(args.input_file) as f:
        checklist = json.load(f)
except Exception as e:
    print("ERROR: Error when processing JSON file", args.file_name_in, "-", str(e))
    sys.exit(1)

# Create client
try:
    client = CosmosClient(url=args.cosmosdb_url, credential=args.cosmosdb_key)
except Exception as e:
    print("ERROR: Error when connecting to Cosmos DB", args.cosmosdb_url, "-", str(e))
    sys.exit(1)

# Delete database
try:
    database = client.delete_database(db_name)
    print(f"DEBUG: Database {db_name} deleted")
except exceptions.CosmosResourceNotFoundError:
    print('INFO: A database with id {db_name} does not exist')

# Create database
try:
    database = client.create_database(id=db_name)
    print(f"DEBUG: Database created: {database.id}")
except exceptions.CosmosResourceExistsError:
    print("ERROR: Database", db_name, "already exists.")

# Create container
try:
    partition_key_path = PartitionKey(path="/guid", kind="Hash")
    container = database.create_container(
        id=container_name,
        partition_key=partition_key_path
        # offer_throughput=400,
    )
    print(f"DEBUG: Container created: {container.id}")
except exceptions.CosmosResourceExistsError:
    print("ERROR: Container", container_name, "already exists.")

# Upload checklist items
print ("DEBUG: adding items, this can take a few minutes...")
item_counter = 0
for item in checklist['items']:
    # print("DEBUG: uploading item: {0}".format(str(item)))
    item['id'] = item['guid']
    container.create_item(body=item)
    item_counter += 1

# Finish
print("{0} items were uploaded to {1}".format(item_counter, cosmosdb_url))