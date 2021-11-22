#app.py
from flask import Flask, request, render_template, jsonify
from flaskext.mysql import MySQL #pip install flask-mysql
import pymysql
import os
  
app = Flask(__name__)
    
mysql = MySQL()
   
app.config['MYSQL_DATABASE_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DATABASE_DB'] = 'checklist'
app.config['MYSQL_DATABASE_HOST'] = os.environ.get("MYSQL_FQDN")
mysql.init_app(app)
  
@app.route('/')
def home():
    try:
        conn = mysql.connect()
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * from items")
        itemslist = cursor.fetchall()
        cursor.execute("SELECT DISTINCT category FROM items")
        categorylist = cursor.fetchall()
        return render_template('index.html', itemslist=itemslist, categorylist=categorylist)
    except Exception as e:
        print(e)
    finally:
        cursor.close() 
        conn.close()
 
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
            app.logger.info("Processing POST for field {0}, editid {1} and value {2}".format(field, value, editid)) 
             
            if field == 'comment' and value != '':
                sql = "UPDATE items SET comments=%s WHERE guid=%s"
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

