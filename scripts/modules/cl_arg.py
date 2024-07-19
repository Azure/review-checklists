#######################################
#
# Module to run ARG queries
#
#######################################

# Dependencies
import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph.models import *


# Function that takes an array of recos as argument and runs the ARG query specified in each of the elements (if existing)
# Code from https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/resourcegraph/resources_query.py
# ToDo: add mgmt group support
def run_arg_queries(reco_array, subscription_id=None, verbose=False):
    # Initialize the ARG client
    if not subscription_id:
        subscription_id = os.environ.get("SUBSCRIPTION_ID", None)
    # Create client. For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    if verbose: print("DEBUG: Running ARG queries for subscription {0}".format(subscription_id))
    arg_client = ResourceGraphClient(
        credential=DefaultAzureCredential(),
        subscription_id=subscription_id
    )
    # Initialize the list of results
    results = []
    # Iterate over all recos
    for reco in reco_array:
        # If the reco has a query, run it
        if 'queries' in reco:
            if 'arg' in reco['queries']:
                # Run the query
                if verbose:
                    print("DEBUG: Running ARG query for reco {0}: {1}".format(reco['guid'], reco['queries']['arg']))
                query = QueryRequest(
                        query=reco['queries']['arg'],
                        subscriptions=[subscription_id],
                        options=QueryRequestOptions(
                            result_format=ResultFormat.object_array
                        )
                    )
                result = arg_client.resources(query)
                # Append the result to the list
                if 'data' in result:
                    results.append({"guid": reco['guid'], "title": reco['title'], "argResult": result['data']})
    # Return the list of results
    return results