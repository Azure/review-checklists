import requests
import json
import os
import sys
import pymysql

# Database and table name
mysql_db_name = "checklist"
mysql_db_table = "items"
use_ssl = "yes"

# Format a string to be included in a SQL query as value
def escape_quotes(this_value):
    return str(this_value).replace("'", "\\'")

# Get database credentials from environment variables
mysql_server_fqdn = os.environ.get("MYSQL_FQDN")
if mysql_server_fqdn == None:
    print("ERROR: Please define an environment variable 'MYSQL_FQDN' with the FQDN of the MySQL server")
    sys.exit(1)
mysql_server_name = mysql_server_fqdn.split('.')[0]
mysql_server_username = os.environ.get("MYSQL_USER")
if mysql_server_username == None:
    print("ERROR: Please define an environment variable 'MYSQL_USER' with the FQDN of the MySQL username")
    sys.exit(1)
if not mysql_server_username.__contains__('@'):
    mysql_server_username +=  '@' + mysql_server_name
mysql_server_password = os.environ.get("MYSQL_PASSWORD")
if mysql_server_password == None:
    print("ERROR: Please define an environment variable 'MYSQL_PASSWORD' with the FQDN of the MySQL password")
    sys.exit(1)

# Create connection to MySQL server and get version
print ("INFO: Connecting to {0} with username {1}...".format(mysql_server_fqdn, mysql_server_username))
if use_ssl == 'yes':
    db = pymysql.connect(host=mysql_server_fqdn, user = mysql_server_username, passwd = mysql_server_password, ssl = {'ssl':{'ca': 'BaltimoreCyberTrustRoot.crt.pem'}})
else:
    db = pymysql.connect(host=mysql_server_fqdn, user = mysql_server_username, passwd = mysql_server_password)
sql_query = "SELECT VERSION();"
cursor = db.cursor()
cursor.execute(sql_query)
rows = cursor.fetchall()
data = ""
if len(rows) > 0:
    for row in rows:
        if len(data) > 0:
            data += ', '
        data += str(''.join(row))
print ("INFO: Connected to MySQL server {0} with version {1}".format(mysql_server_fqdn, data))

# Delete db if existed
sql_query = "DROP DATABASE IF EXISTS {0};".format(mysql_db_name)
# print ("Sending query: {0}".format(sql_query))
cursor.execute(sql_query)
db.commit()

# Create database
sql_query = "CREATE DATABASE IF NOT EXISTS {0};".format(mysql_db_name)
# print ("Sending query: {0}".format(sql_query))
cursor.execute(sql_query)
db.commit()
sql_query = "USE {0}".format(mysql_db_name)
# print ("Sending query: {0}".format(sql_query))
cursor.execute(sql_query)
db.commit()

# Create table
sql_query = """CREATE TABLE {0} (
    guid varchar(40),
    text varchar(1024),
    description varchar(1024),
    link varchar(255),
    training varchar(255),
    comments varchar(1024),
    severity varchar(10),
    status varchar(15),
    category varchar(255),
    subcategory varchar(255),
    graph_query_success varchar(1024),
    graph_query_failure varchar(1024),
    graph_query_result varchar(4096)
);""".format(mysql_db_table)
# print ("DEBUG: Sending query: {0}".format(sql_query))
cursor.execute(sql_query)
db.commit()

# Download checklist
technology = os.environ.get("CHECKLIST_TECHNOLOGY")
if technology:
    checklist_url = "https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/" + technology + "_checklist.en.json"
else:
    checklist_url = "https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/lz_checklist.en.json"
response = requests.get(checklist_url)

# If download was successful
if response.status_code == 200:
    print ("INFO: File {0} downloaded successfully".format(checklist_url))
    try:
        # Deserialize JSON to object variable
        checklist_object = json.loads(response.text)
    except Exception as e:
        print("Error deserializing JSON content: {0}".format(str(e)))
        sys.exit(1)
    # Get default status from the JSON, default to "Not verified"
    try:
        status_list = checklist_object.get("status")
        default_status = status_list[0].get("name")
    except:
        default_status = "Not verified"
        pass
    # For each checklist item, add a row to mysql DB
    row_counter = 0
    for item in checklist_object.get("items"):
        guid = item.get("guid")
        category = item.get("category")
        subcategory = item.get("subcategory")
        text = escape_quotes(item.get("text"))
        description = escape_quotes(item.get("description"))
        severity = item.get("severity")
        link = item.get("link")
        training = item.get("training")
        status = default_status
        graph_query_success = escape_quotes(item.get("graph_success"))
        graph_query_failure = escape_quotes(item.get("graph_failure"))
        # print("DEBUG: Adding to table {0}: '{1}', '{2}', '{3}', '{4}', '{5}', '{6}', '{7}', '{8}', '{9}', '{10}'".format(mysql_db_table, category, subcategory, text, description, severity, link, training, graph_query_success, graph_query_failure, guid))
        sql_query = """INSERT INTO {0} (category,subcategory,text,description,severity,link,training,graph_query_success,graph_query_failure,guid,status) 
            VALUES ('{1}','{2}','{3}','{4}','{5}', '{6}','{7}','{8}','{9}','{10}', '{11}');""".format(mysql_db_table, category, subcategory, text, description, severity, link, training, graph_query_success, graph_query_failure, guid, status)
        # print ("DEBUG: Sending query: {0}".format(sql_query))
        cursor.execute(sql_query)
        db.commit()
        row_counter += 1
else:
    print ("Error downloading {0}".format(checklist_url))

# Bye
print("INFO: {0} rows added to database.".format(str(row_counter)))
db.close()