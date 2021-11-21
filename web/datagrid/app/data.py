import sqlalchemy
import sqlalchemy_utils
import json, string
import os, sys, math
from app import app
from flask import request, session
from pprint import pprint
import logging
from collections import OrderedDict

class PythonGridDbData():

    def __init__(self, sql):

        self.__gridName        = request.args['gn'] if 'gn' in request.args.keys() else sys.exit('PYTHONGRID_ERROR: ULR parameter "gn" is not defined.');
        self.__data_type       = request.args['dt'] if 'dt' in request.args.keys() else 'json'
        self.__grid_sql        = sql
        self.__sql_filter      = '' #TODO filter from set_query_filter()
        self.__has_pagecount = True

        self.__page  = int(request.args['page']) if 'page' in request.args.keys() else 1
        self.__limit = int(request.args['rows']) if 'page' in request.args.keys() else 1      # get how many rows we want to have into the grid - rowNum parameter in the grid
        self.__sidx  = str(request.args['sidx']) if 'page' in request.args.keys() else 1     # get index row - i.e. user click to sort. At first time sortname parameter - // after that the index from colModel
        self.__sord  = request.args['sord'] if 'page' in request.args.keys() else 'asc'        # sorting order - at first time sortorder
        
        self.__rs = None
        self.__count = 0
        self.__total_pages = 0
        self.__num_fields = 0
        self.__field_names = []
        self.__field_types = []

        engine = sqlalchemy.create_engine(app.config['PYTHONGRID_DB_TYPE']+'://'+app.config['PYTHONGRID_DB_USERNAME']+':'+app.config['PYTHONGRID_DB_PASSWORD']+'@'+app.config['PYTHONGRID_DB_HOSTNAME']+'/'+app.config['PYTHONGRID_DB_NAME']+'?unix_socket='+app.config['PYTHONGRID_DB_SOCKET']).connect()
        md = sqlalchemy.MetaData()
        
        table = sqlalchemy.Table(self.__gridName, md, autoload=True, autoload_with=engine)
        columns = table.c

        # get table total row count (Not using Query API)
        self.__count = engine.execute('SELECT COUNT(*) FROM '+ self.__gridName).scalar()

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
        if 'AND ' in sqlWhere:
            sqlWhere = sqlWhere[len('AND '):]
        if 'OR ' in sqlWhere:
            sqlWhere = sqlWhere[len('OR '):]


        app.logger.info(sqlWhere)


        # (MySql only) escape column name contains '-' for sorting 
        if '-' in self.__sidx :
            self.__sidx = '`' + self.__sidx.upper() + '`'
        
        # set ORDER BY. Don't use if user hasn't select a sort
        sqlOrderBy = ''
        if not self.__sidx:
            pass
        elif self.__sidx == "1":
            pass
        else:
            sqlOrderBy = f" ORDER BY {sqlalchemy_utils.functions.quote(engine, self.__sidx)} {self.__sord}"


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


        # ******************* execute query finally *****************
        # calculate the starting position of the rows 
        start = self.__limit * self.__page - self.__limit

        # if for some reasons start position is negative set it to 0. typical case is that the user type 0 for the requested page 
        if start < 0: start = 0

        # get records
        SQL += ' LIMIT ' + str(self.__limit) + ' OFFSET ' + str(start)


        app.logger.info(SQL)


        with engine.connect() as conn:
            self.__rs = conn.execute(sqlalchemy.text(SQL)).fetchall() 

        # total record count used for pagination (unfortunate performance penality).
        self.__count = self.__count if self.__has_pagecount else 1000000000
        self.__num_fields = len(self.__field_names)

        # calculate the total pages for the query 
        if self.__count > 0 and self.__limit > 0 : 
            self.__total_pages = math.ceil(self.__count / self.__limit) 
        else: 
            self.__total_pages = 0

        # if for some reasons the requested page is greater than the total set the requested page to total page 
        if self.__page > self.__total_pages:
            self.__page = self.__total_pages


    def getData(self):

        data             = {}
        data['page']     = self.__page
        data['total']     = self.__total_pages
        data['records'] = self.__count
        data['rows']     = []

        # ********* return results in JSON *********
        rows              = []     # rows is an array of dictionaries
        rowsdict         = OrderedDict() # dictionary of row plus id 
        row              = []
        i = 0
        for id, rs in enumerate(self.__rs):

            rowsdict['id'] = id  #TODO - not a real sql key value
            
            j = 0

            while j < self.__num_fields:                
                row.append(rs[j])
                j += 1

            rowsdict['cell'] = row
            rows.append(dict(rowsdict))
            row = []  #clear list before iterate

            i += 1


        data['rows'].extend(rows)

        # print(json.dumps(data)) #app.logger.info(data)    

        # should return the format like this 
        # #'{"page":' + str(self.__page) + ',"total":' + str(self.__total_pages) + ',"records":' + str(self.__count) + ',"rows":[{"id":"1002","cell":["1002","Diane","Murphy"]},{"id":"1056","cell":["1056","Mary","Patterson"]},{"id":"1076","cell":["1076","Jeff","Firrelli"]},{"id":"1088","cell":["1088","William","Patterson"]},{"id":"1102","cell":["1102","Gerard","Bondur"]},{"id":"1165","cell":["1165","Leslie","Jennings"]},{"id":"1166","cell":["1166","Leslie","Thompson"]},{"id":"1188","cell":["1188","Julie","Firrelli"]},{"id":"1216","cell":["1216","Steve","Patterson"]},{"id":"1286","cell":["1286","Foon Yue","Tseng"]},{"id":"1323","cell":["1323","George","Vanauf"]},{"id":"1337","cell":["1337","Loui","Bondur"]},{"id":"1370","cell":["1370","Gerard","Hernandez"]},{"id":"1401","cell":["1401","Pamela","Castillo"]},{"id":"1501","cell":["1501","Larry","Bott"]},{"id":"1504","cell":["1504","Barry","Jones"]},{"id":"1611","cell":["1611","Andy","Fixter"]},{"id":"1612","cell":["1612","Peter","Marsh"]},{"id":"1619","cell":["1619","Tom","King"]},{"id":"1621","cell":["1621","Mami","Nishi"]},{"id":"1625","cell":["1625","Yoshimi","Kato"]},{"id":"1702","cell":["1702","Martin","Gerard"]}]}'
        return json.dumps(data, default=str) 

