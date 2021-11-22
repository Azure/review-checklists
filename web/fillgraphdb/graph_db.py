import os
import sys
import pymysql
import json
import azure.mgmt.resourcegraph as arg
from azure.mgmt.resource import SubscriptionClient
from azure.identity import AzureCliCredential

# Database and table name
mysql_db_name = "checklist"
mysql_db_table = "items"
use_ssl = "yes"

# Format a string to be included in a SQL query as value
def escape_quotes (this_value):
    return str(this_value).replace("'", "\\'")

# Send an Azure Resource Graph query
def getResources (strQuery):
    # Get your credentials from Azure CLI (development only!) and get your subscription list
    credential = AzureCliCredential()
    subsClient = SubscriptionClient(credential)
    subsRaw = []
    for sub in subsClient.subscriptions.list():
        subsRaw.append(sub.as_dict())
    subsList = []
    for sub in subsRaw:
        subsList.append(sub.get('subscription_id'))
    # Create Azure Resource Graph client and set options
    argClient = arg.ResourceGraphClient(credential)
    argQueryOptions = arg.models.QueryRequestOptions(result_format="objectArray")
    # Create query
    argQuery = arg.models.QueryRequest(subscriptions=subsList, query=strQuery, options=argQueryOptions)
    # Run query
    argResults = argClient.resources(argQuery)
    # Show Python object
    # print(argResults)
    return argResults

# Get database credentials from environment variables
mysql_server_fqdn = os.environ.get("MYSQL_FQDN")
if mysql_server_fqdn == None:
    print("Please define an environment variable 'MYSQL_FQDN' with the FQDN of the MySQL server")
    sys.exit(1)
mysql_server_name = mysql_server_fqdn.split('.')[0]
mysql_server_username = os.environ.get("MYSQL_USER")
if mysql_server_username == None:
    print("Please define an environment variable 'MYSQL_USER' with the FQDN of the MySQL username")
    sys.exit(1)
if not mysql_server_username.__contains__('@'):
    mysql_server_username +=  '@' + mysql_server_name
mysql_server_password = os.environ.get("MYSQL_PASSWORD")
if mysql_server_password == None:
    print("Please define an environment variable 'MYSQL_PASSWORD' with the FQDN of the MySQL password")
    sys.exit(1)

# Create connection to MySQL server and number of records
print ("DEBUG: Connecting to {0} with username {1}...".format(mysql_server_fqdn, mysql_server_username))
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
        item_guid=row[0]
        item_success_query=row[10]
        item_failure_query=row[11]
        # print ("DEBUG {0}: '{1}', '{2}'".format(item_guid, item_success_query, item_failure_query))
        success_resources = str(getResources(item_success_query)).replace("'", '"')
        success_resources = success_resources.replace(': None', ': "None"')
        # print ("DEBUG: SUCCESS QUERY: {0}".format(success_resources))
        success_resources_object = json.loads(success_resources)
        failure_resources = str(getResources(item_failure_query)).replace("'", '"')
        failure_resources = failure_resources.replace(': None', ': "None"')
        # print ("DEBUG: FAILURE QUERY: {0}".format(failure_resources))
        failure_resources_object = json.loads(failure_resources)
        for resource in success_resources_object['data']:
            if result_text: result_text += '\n'
            result_text += "DEBUG: SUCCESS - {0}".format(resource["id"])
        for resource in failure_resources_object['data']:
            if result_text: result_text += '\n'
            result_text += "DEBUG: FAILURE - {0}".format(resource["id"])
        # print ("DEBUG: Result summary: \n{0}".format(result_text))
        update_query = "UPDATE items SET graph_query_result = '{0}' WHERE guid = '{1}';".format(result_text, item_guid)
        print ("DEBUG: sending SQL query '{0}'".format(update_query))
        cursor.execute(update_query)
        db.commit()
else:
    row_count = 0
print ("INFO: Processed table {0} in database {1} with {2} records with graph queries".format(mysql_db_table, mysql_db_name, str(row_cnt)))

# Bye
db.close()