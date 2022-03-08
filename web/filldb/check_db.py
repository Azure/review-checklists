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
print ("Connecting to {0} with username {1}...".format(mysql_server_fqdn, mysql_server_username))
if use_ssl == 'yes':
    db = pymysql.connect(host=mysql_server_fqdn, user = mysql_server_username, database = mysql_db_name, passwd = mysql_server_password, ssl = {'ssl':{'ca': 'BaltimoreCyberTrustRoot.crt.pem'}})
else:
    db = pymysql.connect(host=mysql_server_fqdn, user = mysql_server_username, database = mysql_db_name, passwd = mysql_server_password)
sql_query = "SELECT COUNT(*) FROM {0};".format (mysql_db_table)
cursor = db.cursor()
cursor.execute(sql_query)
rows = cursor.fetchall()
if len(rows) > 0:
    row_count = rows[0][0]
else:
    row_count = 0
print ("Table {0} in database {1} contains {2} records".format(mysql_db_table, mysql_db_name, str(row_count)))

# Bye
db.close()