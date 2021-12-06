#app.py
from flask import Flask, request, render_template, jsonify
from flaskext.mysql import MySQL #pip install flask-mysql
import pymysql
import os
  
app = Flask(__name__)

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
    mysql_server_username += '@' + mysql_server_name
mysql_server_password = os.environ.get("MYSQL_PASSWORD")
if mysql_server_password == None:
    print("ERROR: Please define an environment variable 'MYSQL_PASSWORD' with the FQDN of the MySQL password")
    sys.exit(1)

# Open connection
mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = mysql_server_username
app.config['MYSQL_DATABASE_PASSWORD'] = mysql_server_password
app.config['MYSQL_DATABASE_DB'] = 'checklist'
app.config['MYSQL_DATABASE_HOST'] = mysql_server_fqdn
mysql.init_app(app)
  
@app.route('/')
def home():
    app.logger.info("DEBUG: Connecting to database...") 
    try:
        category_filter  = request.args.get('category', None)
        status_filter  = request.args.get('status', None)
        severity_filter  = request.args.get('severity', None)
    except Exception as e:
        app.logger.info("ERROR reading query parameters for filters: {0}".format(str(e)))
        pass
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
    except Exception as e:
        app.logger.info("ERROR opening cursor to DB connection: {0}".format(str(e)))
        return jsonify(str(e))
    try:
        sqlquery = "SELECT * from items"
        filter1_added = False
        # category filter
        if category_filter:
            if filter1_added:
                sqlquery += " AND "
            else:
                sqlquery += " WHERE "
                filter1_added = True
            sqlquery += "category = '{0}'".format(category_filter)
        # status filter
        if status_filter:
            if filter1_added:
                sqlquery += " AND "
            else:
                sqlquery += " WHERE "
                filter1_added = True
            sqlquery += "status = '{0}'".format(status_filter)
        # severity filter
        if severity_filter:
            if filter1_added:
                sqlquery += " AND "
            else:
                sqlquery += " WHERE "
                filter1_added = True
            sqlquery += "severity = '{0}'".format(severity_filter)
        # send queries
        app.logger.info ("Retrieving checklist items with query '{0}'".format(sqlquery))
        cursor.execute(sqlquery)
        itemslist = cursor.fetchall()
        cursor.execute("SELECT DISTINCT category FROM items")
        categorylist = cursor.fetchall()
        cursor.execute("SELECT DISTINCT severity FROM items")
        severitylist = cursor.fetchall()
        cursor.execute("SELECT DISTINCT status FROM items")
        statuslist = cursor.fetchall()
        return render_template('index.html', itemslist=itemslist, categorylist=categorylist, severitylist=severitylist, statuslist=statuslist)
    except Exception as e:
        app.logger.info("ERROR sending query: {0}".format(str(e)))
        return jsonify(str(e))
 
@app.route("/update",methods=["POST","GET"])
def update():
    app.logger.info("Processing {0} with request.form {1}".format(str(request.method), str(request.form))) 
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        if request.method == 'POST':
            field = request.form['field'] 
            value = request.form['value']
            editid = request.form['id']
            app.logger.info("Processing POST for field '{0}', editid '{1}' and value '{2}'".format(field, value, editid)) 
             
            if field == 'comment' and value != '':
                sql = "UPDATE items SET comments=%s WHERE guid=%s"
                data = (value, editid)
                conn = mysql.connect()
                cursor = conn.cursor()
                app.logger.info ("Sending SQL query '{0}' with data '{1}'".format(sql, str(data)))
                cursor.execute(sql, data)
                conn.commit()
            elif field == 'status' and value != '':
                sql = "UPDATE items SET status=%s WHERE guid=%s"
                data = (value, editid)
                conn = mysql.connect()
                cursor = conn.cursor()
                app.logger.info ("Sending SQL query '{0}' with data '{1}'".format(sql, str(data)))
                cursor.execute(sql, data)
                conn.commit()
            else:
                app.logger.info ("Field is '{0}', value is '{1}': not doing anything".format(field, value))
        success = 1
        return jsonify(success)
    except Exception as e:
        app.logger.info("Oh oh, there is an error: {0}".format(str(e)))
        success = 0
        return jsonify(success)
    finally:
        cursor.close() 
        conn.close()
  
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)

