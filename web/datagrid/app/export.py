import sqlalchemy
import sqlalchemy_utils
import json, string
import os, sys, math
from app import app
from flask import request, session
import logging
from collections import OrderedDict

class PythonGridDbExport():
    
    def __init__(self, sql):

        self.__gridName     = request.args['gn'] if 'gn' in request.args.keys() else sys.exit('PYTHONGRID_ERROR: ULR parameter "gn" is not defined.')
        self.__export_type  = request.args['export_type'] if 'export_type' in request.args.keys() else None
        self.__grid_sql     = sql
        self.__sql_filter   = '' #TODO  set_query_filter()
        self.__sql_fkey	    = '' #TODO  session->get(SESSION_KEY.'_'.gridName.'_sql_fkey');

        self.__rs = None # grid header
        self.__result = None # grid body
        self.__count = 0
        self.__total_pages = 0
        self.__num_fields = 0
        self.__field_names = []
        self.__field_types = []

        if self.__export_type is None:
            sys.exit('Cannot export the grid. Please use enable_export() method to enable this feature.')

        engine = sqlalchemy.create_engine(app.config['PYTHONGRID_DB_TYPE']+'://'+app.config['PYTHONGRID_DB_USERNAME']+':'+app.config['PYTHONGRID_DB_PASSWORD']+'@'+app.config['PYTHONGRID_DB_HOSTNAME']+'/'+app.config['PYTHONGRID_DB_NAME']+'?unix_socket='+app.config['PYTHONGRID_DB_SOCKET']).connect()
        md = sqlalchemy.MetaData()
        
        table = sqlalchemy.Table(self.__gridName, md, autoload=True, autoload_with=engine)
        columns = table.c

        #TODO if it is a masterdetail/subgrid, obtain the value of the foreign key to used later for filtering



        sord = request.args['sord'] if 'sord' in request.args.keys() else 'asc'
        sidx = request.args['sidx'] if 'sidx' in request.args.keys() else 1

        if not sidx:
            sidx = 1

        SQL = 'SELECT * FROM '+ self.__gridName + ' LIMIT 1 OFFSET 1'

        with engine.connect() as conn:
            self.__rs = conn.execute(sqlalchemy.text(SQL)).fetchall() 

        for column in columns:
            self.__field_names.append(column.name)
            self.__field_types.append(column.type)


        fm_type = self.__field_types[0]

        sqlWhere = ''

        if '_search' in request.args.keys() and request.args['_search'] == 'true':
            searchOn = True
        else:
            searchOn = False

        if searchOn:
            col_dbnames = []
            col_dbnames = self.__field_names

            # check if the key is an actual database field. If so, add it to SQL Where (sqlWhere) statement
            for key, value in enumerate(request.args):
                if key in col_dbnames:
                
                    field_index = self.__field_names.index(key)
                    fm_type = self.__field_types[field_index]

                    # only add single to non-numeric value
                    if type(fm_type) == sqlalchemy.sql.sqltypes.INTEGER or \
                        type(fm_type) == sqlalchemy.sql.sqltypes.NUMERIC or \
                        type(fm_type) == sqlalchemy.sql.sqltypes.Float:
                        sqlWhere += " AND " + sqlalchemy_utils.functions.quote(engine, key) + " = " + value
                    else:
                        sqlWhere += " AND " + sqlalchemy_utils.functions.quote(engine, key) + " LIKE '" + value + "%'"

            # integrated toolbar and advanced search    
            if 'filters' in request.args.keys() and request.args['filters'] != '' :
                operation = {
                    "eq": " ='%s' ","ne": " !='%s' ","lt": " < %s ",
                    "le": " <= %s ","gt": " > %s ","ge": " >= %s ",
                    "bw": " like '%s%%' ","bn": " not like '%s%%' " ,
                    "in":  " in (%s) ","ni":  " not in (%s) ",
                    "ew":  " like '%%%s' ","en":  " not like '%%%s' ",
                    "cn":  " like '%%%s%%' ","nc":  " not like '%%%s%%' "
                }

                filters = json.loads(request.args['filters'])                        
                groupOp = filters['groupOp']    # AND/OR
                rules = filters['rules']

                for i in range(0, len(rules)):
                    filter = operation[rules[i]['op']]

                    # surround date fields with quotes for SQL date comparison
                    field_index = self.__field_names.index(rules[i]['field'])
                    fm_type = self.__field_types[field_index]
                    
                    if type(fm_type) == sqlalchemy.sql.sqltypes.DATE or type(fm_type) == sqlalchemy.sql.sqltypes.TIMESTAMP \
                        or type(fm_type) == sqlalchemy.sql.sqltypes.DATETIME or type(fm_type) == sqlalchemy.sql.sqltypes.TIME:
                        
                        dateOps = ['eq', 'ne', 'lt', 'le', 'gt', 'ge']

                        op = rules[i]['op']
                        if op in dateOps :
                            filter = filter.replace("'", "")
                            filter = filter.replace("%s", "'%s'")

                    if not type(fm_type) == sqlalchemy.sql.sqltypes.VARCHAR and \
                        not type(fm_type) == sqlalchemy.sql.sqltypes.CHAR and \
                        not type(fm_type) == sqlalchemy.sql.sqltypes.TEXT and \
                        not type(fm_type) == sqlalchemy.sql.sqltypes.String:

                        sqlStrType = 'CHAR' if app.config['PYTHONGRID_DB_TYPE'].find('mysql') != -1 else 'VARCHAR'

                        sqlWhere += groupOp + " CAST(" + sqlalchemy_utils.functions.quote(engine, rules[i]['field']) + " AS " + sqlStrType + ")" + \
                                (filter % rules[i]['data'])
                    else:
                        
                        sqlWhere += groupOp + " " + sqlalchemy_utils.functions.quote(engine, rules[i]['field']) + \
                                (filter % rules[i]['data'])

        # remove leading sql AND/OR
        if sqlWhere.find('AND '):
            sqlWhere = sqlWhere[len('AND '):]
        if sqlWhere.find('OR '):
            sqlWhere = sqlWhere[len('OR '):]


        app.logger.info(sqlWhere)


        # (MySql only) escape column name contains '-' for sorting 
        # if str(sidx).find('-') :
        #    sidx = '`' + str(sidx).upper() + '`'
        
        # set ORDER BY. Don't use if user hasn't select a sort
        sqlOrderBy = ''
        if not sidx:
            pass
        elif str(sidx) == "1":
            pass
        else:
            sqlOrderBy = f" ORDER BY {sqlalchemy_utils.functions.quote(engine, sidx)} {sord}"


        app.logger.info(sqlOrderBy)


        # ****************** prepare the final query ***********************
        # Store GROUP BY Position 
        groupBy_Position = sql.upper().find("GROUP BY")

        if self.__sql_filter != '' and searchOn :
            SQL = self.__grid_sql + ' WHERE ' + self.__sql_filter + ' AND (' + sqlWhere + ')' + sqlOrderBy
        elif self.__sql_filter != '' and not searchOn :
            SQL = self.__grid_sql + ' WHERE ' + self.sql_filter + sqlOrderBy
        elif self.__sql_filter == '' and searchOn :
            SQL = self.__grid_sql + ' WHERE ' + sqlWhere + sqlOrderBy
        else:
            SQL = self.__grid_sql + sqlOrderBy


        app.logger.info(SQL)


        with engine.connect() as conn:
            self.__result = conn.execute(sqlalchemy.text(SQL)).fetchall()
            self.__count = len(self.__rs)
            self.__num_fields = len(self.__field_names)


    def export(self):
        output = ''

        if self.__export_type.upper() == 'CSV':
            row_header = []

            #header
            for j in range(0,  self.__num_fields):
                col_name = self.__field_names[j]
                row_header.append(col_name)
            output = ','.join([str(i) for i in row_header]) + '\n'

            #body
            for row in self.__result:
                output += ','.join([str(i) for i in row]) + '\n'

        return output, 200, {'Content-Type': 'text/csv; charset=utf-8', 'Pragma':'no-cache', 'Expires':'0', 'Content-Disposition': 'attachment; filename="'+ self.__gridName +'_export.csv"'}
