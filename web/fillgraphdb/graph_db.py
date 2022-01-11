import os
import sys
import pymysql
import json
import time
import requests
import azure.mgmt.resourcegraph as arg
from datetime import datetime
from azure.mgmt.resource import SubscriptionClient
from azure.identity import AzureCliCredential
from azure.identity import DefaultAzureCredential
from azure.identity import ClientSecretCredential

# Database and table name
mysql_db_name = "checklist"
mysql_db_table = "items"
use_ssl = "yes"

# Format a string to be included in a SQL query as value
def escape_quotes (this_value):
    return str(this_value).replace("'", "\\'")

# Function to send an Azure Resource Graph query
def get_resources (graph_query, argClient, subsList, argQueryOptions):
    # TO DO: Authentication should probably happen outside of this function
    try:
        # Create query
        argQuery = arg.models.QueryRequest(subscriptions=subsList, query=graph_query, options=argQueryOptions)
        # Run query and return results
        argResults = argClient.resources(argQuery)
        print("DEBUG: query results: {0}".format(str(argResults)))
        return argResults
    except Exception as e:
        print("ERROR: Error sending Azure Resource Graph query to Azure: {0}".format(str(e)))
        # sys.exit(0)   # Debugging.... Probably this should be exit(1)
        return ''

# Wait for IMDS endpoint to be available
try:
    wait_max_intervals = int(os.environ.get("WAIT_INTERVALS"))
    print ("DEBUG: WAIT_INTERVALS read from environment variable: {0}".format(str(wait_max_intervals)))
except:
    wait_max_intervals = 5
    print ("DEBUG: WAIT_INTERVALS set to default value: {0}".format(str(wait_max_intervals)))
wait_interval = 10.0
imds_url = 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/'
imds_headers = {
    "Metadata" : "true"
}
imds_tries = 0
break_loop = False
print ('DEBUG: Going into waiting loop to make sure the metadata endpoint is active...')
while not break_loop:
    imds_tries += 1
    print ("DEBUG: We are in the loop, pass {0}/{1} ({2}). Trying the IMDS endpoint...".format(str(imds_tries), str(wait_max_intervals), str(datetime.now())))
    if imds_tries > wait_max_intervals:
        print("ERROR: max wait intervals exceeded when waiting for IMDS to answer, hopefully you specified some SP credentials as SP variables...")
        break_loop = True
    else:
        print ("DEBUG: Sending GET request to {0}...".format(imds_url))
        try:
            imds_response = requests.get(imds_url, headers=imds_headers, timeout=1)
            if imds_response.status_code >= 200 and imds_response.status_code <= 299:
                print ("DEBUG: IMDS endpoint seems to be working, received status code {0} and answer {1}".format(str(imds_response.status_code), str(imds_response.text)))
                break_loop = True
            else:
                print ("DEBUG: IMDS endpoint doesnt seem to be working, received status code {0} and answer {1}".format(str(imds_response.status_code), str(imds_response.text)))
        except Exception as e:
            print("DEBUG: Error sending request to IMDS endpoint: {0}".format(str(e)))
            pass
        if not break_loop:
            print("DEBUG: Going to sleep {0} seconds before next try...".format(str(wait_interval)))
            time.sleep (wait_interval)

# Authenticate to Azure, either with Managed Identity or SP
print('DEBUG: Authenticating to Azure...')
try:
    print('DEBUG: Getting environment variables...')
    # credential = AzureCliCredential()          # Get your credentials from Azure CLI (development only!) and get your subscription list
    tenant_id = os.environ.get("AZURE_TENANT_ID")
    client_id = os.environ.get("AZURE_CLIENT_ID")
    client_secret = os.environ.get("AZURE_CLIENT_SECRET")
except Exception as e:
    print("ERROR: Error getting environment variables: {0}".format(str(e)))
    tenant_id = None
    client_id = None
    client_secret = None
    pass    
try:
    if tenant_id and client_id and client_secret:
        print("DEBUG: Service principal credentials (client ID {0}, tenant ID {1}) retrieved from environment variables, trying SP-based authentication now...".format(str(client_id), str(tenant_id)))
        credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    else:
        print('DEBUG: Service principal credentials could not be retrieved from environment variables, trying default authentication method with Managed Identity...')
        credential = DefaultAzureCredential()        # Managed identity
except Exception as e:
    print("ERROR: Error during Azure Authentication: {0}".format(str(e)))
    sys.exit(1)
try:
    print('DEBUG: Getting subscriptions...')
    subsClient = SubscriptionClient(credential)
    subsRaw = []
    for sub in subsClient.subscriptions.list():
        subsRaw.append(sub.as_dict())
    subsList = []
    for sub in subsRaw:
        subsList.append(sub.get('subscription_id'))
    print ("DEBUG: provided credentials give access to {0} subscription(s)".format(str(len(subsList))))
    # Create Azure Resource Graph client and set options
    print('DEBUG: Creating client object...')
    argClient = arg.ResourceGraphClient(credential)
    argQueryOptions = arg.models.QueryRequestOptions(result_format="objectArray")
except Exception as e:
    print("ERROR: Error creating resource graph client object: {0}".format(str(e)))
    sys.exit(1)

# Get database credentials from environment variables
mysql_server_fqdn = os.environ.get("MYSQL_FQDN")
if mysql_server_fqdn == None:
    print("ERROR: Please define an environment variable 'MYSQL_FQDN' with the FQDN of the MySQL server")
    sys.exit(1)
else:
    print("DEBUG: mysql FQDN retrieved from environment variables: '{0}'".format(mysql_server_fqdn))
mysql_server_name = mysql_server_fqdn.split('.')[0]
mysql_server_username = os.environ.get("MYSQL_USER")
if mysql_server_username == None:
    print("ERROR: Please define an environment variable 'MYSQL_USER' with the FQDN of the MySQL username")
    sys.exit(1)
else:
    print("DEBUG: mysql authentication username retrieved from environment variables: '{0}'".format(mysql_server_username))
if not mysql_server_username.__contains__('@'):
    mysql_server_username +=  '@' + mysql_server_name
mysql_server_password = os.environ.get("MYSQL_PASSWORD")
if mysql_server_password == None:
    print("ERROR: Please define an environment variable 'MYSQL_PASSWORD' with the FQDN of the MySQL password")
    sys.exit(1)
else:
    print("DEBUG: mysql authentication password retrieved from environment variables: {0}".format("********"))

# Create connection to MySQL server and number of records
print ("DEBUG: Connecting to '{0}' with username '{1}'...".format(mysql_server_fqdn, mysql_server_username))
if use_ssl == 'yes':
    db = pymysql.connect(host=mysql_server_fqdn, user = mysql_server_username, database = mysql_db_name, passwd = mysql_server_password, ssl = {'ssl':{'ca': 'BaltimoreCyberTrustRoot.crt.pem'}})
else:
    db = pymysql.connect(host=mysql_server_fqdn, user = mysql_server_username, database = mysql_db_name, passwd = mysql_server_password)
sql_query = "SELECT * FROM {0} WHERE graph_query_success IS NOT null AND graph_query_failure IS NOT null AND graph_query_success != 'None' AND graph_query_failure != 'None';".format (mysql_db_table)
cursor = db.cursor()
cursor.execute(sql_query)
rows = cursor.fetchall()
row_cnt = 0
if len(rows) > 0:
    for row in rows:
        row_cnt += 1
        result_text = ''
        item_guid = row[0]
        item_success_query = row[10]
        item_failure_query = row[11]
        # print ("DEBUG {0}: '{1}', '{2}'".format(item_guid, item_success_query, item_failure_query))
        success_resources = str(get_resources(item_success_query, argClient, subsList, argQueryOptions)).replace("'", '"')
        success_resources = success_resources.replace(': None', ': "None"')
        # print ("DEBUG: SUCCESS QUERY: {0}".format(success_resources))
        if success_resources:
            try:
                success_resources_object = json.loads(success_resources)
            except:
                print("ERROR: JSON returned from Azure Graph Query not valid: {0}".format(success_resources))
            for resource in success_resources_object['data']:
                if result_text: result_text += '\n'
                result_text += "SUCCESS: {0}".format(resource["id"])
        failure_resources = str(get_resources(item_failure_query, argClient, subsList, argQueryOptions)).replace("'", '"')
        failure_resources = failure_resources.replace(': None', ': "None"')
        # print ("DEBUG: FAILURE QUERY: {0}".format(failure_resources))
        if failure_resources:
            try:
                failure_resources_object = json.loads(failure_resources)
            except:
                print("ERROR: JSON returned from Azure Graph Query not valid: {0}".format(failure_resources))
            for resource in failure_resources_object['data']:
                if result_text: result_text += '\n'
                result_text += "FAILURE: {0}".format(resource["id"])
        # print ("DEBUG: Result summary: \n{0}".format(result_text))
        if result_text:
            update_query = "UPDATE items SET graph_query_result = '{0}' WHERE guid = '{1}';".format(result_text, item_guid)
            print ("DEBUG: sending SQL query '{0}'".format(update_query))
            try:
                cursor.execute(update_query)
                db.commit()
            except Exception as e:
                print("ERROR: Error sending SQL query to MySql server: {0}".format(str(e)))
                pass
        else:
            print("DEBUG: No results could be retrieved for the success and failure queries of checklist item {0}".format(item_guid))
else:
    row_count = 0
print ("INFO: Processed table {0} in database {1} with {2} records with graph queries. Happy review!".format(mysql_db_table, mysql_db_name, str(row_cnt)))

# Bye
db.close()