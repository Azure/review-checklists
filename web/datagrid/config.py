import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    ABS_PATH = '/'
    # mysql 
    PYTHONGRID_DB_HOSTNAME = os.environ.get("MYSQL_FQDN")
    PYTHONGRID_DB_USERNAME = os.environ.get("MYSQL_USER")
    PYTHONGRID_DB_PASSWORD = os.environ.get("MYSQL_PASSWORD")
    PYTHONGRID_DB_NAME = 'checklist'
    PYTHONGRID_DB_TYPE = 'mysql+pymysql'
    PYTHONGRID_DB_SOCKET = '/Applications/MAMP/tmp/mysql/mysql.sock'
    PYTHONGRID_DB_CHARSET = 'utf-8'
