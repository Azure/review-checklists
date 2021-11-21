from sqlalchemy import create_engine
import json, string, re
from app import app
from collections import OrderedDict


class PythonGrid():

    # STATIC these values need to persist across different classes
    has_autocomplete = False
    has_wysiwyg = False
    has_fileupload = False
    load_ajaxComplete = False
    has_rating = False
    
    def __init__(self, sql, sql_key='', sql_table='', db_connection=[]):


        self.__jq_gridName = 'list1' if sql_table == '' else sql_table.replace('.', '_')
        self.__sql = sql
        self.__sql_key = sql_key
        self.__sql_table = sql_table
        self.__jq_pagerName = '"#' + self.__jq_gridName + '_pager1"'  # Notice the double quote
        self.__jq_caption = sql_table + '&nbsp'

        self.jq_colModel = [] # [{"autoResizable":True,"name":"employeeNumber","index":"employeeNumber","hidden":False,"headerTitle":"employeeNumber","edittype":"text","editable":False,"editoptions":{"size":"30"},"editrules":{"edithidden":False,"required":False,"number":False}},{"autoResizable":True,"name":"firstName","index":"firstName","hidden":False,"headerTitle":"firstName","edittype":"text","editable":False,"editoptions":{"size":"30"},"editrules":{"edithidden":False,"required":False}},{"autoResizable":True,"name":"lastName","index":"lastName","hidden":False,"headerTitle":"lastName","edittype":"text","editable":False,"editoptions":{"size":"30"},"editrules":{"edithidden":False,"required":False}}]
        self.before_script_end = ''

        self.pdf_logo = ''            # PDF logo property (PDF export and file must be jpg only)
        self.debug = False            # TODO - will be deprecated next version
        
        self.db = create_engine(app.config['PYTHONGRID_DB_TYPE']+'://'+app.config['PYTHONGRID_DB_USERNAME']+':'+app.config['PYTHONGRID_DB_PASSWORD']+'@'+app.config['PYTHONGRID_DB_HOSTNAME']+'/'+app.config['PYTHONGRID_DB_NAME']+'?unix_socket='+app.config['PYTHONGRID_DB_SOCKET'], encoding=app.config['PYTHONGRID_DB_CHARSET'])
        
        self.db_connection = []
        self.obj_subgrid = []        # subjgrid object
        self.obj_md = []             # master detail object
        self.data_local = []         # used to hold values of local array data when jq_atatype is 'local'
        self.session = None                 # session object
        self.autoencode = True                # preventing from XSS
        self.cust_prop_jsonstr = ''        # JSON string, custom JSON properties. This supersets cust_grid_properties which is json_encoded eventually

        # grid columns
        # self.__sql = ''
        # self.__sql_table = ''
        # self.__sql_key = ''
        self.__sql_fkey = None          # foreign key (used by when grid is a subgrid)
        self.__sql_mfkey = None         # master key (used by when grid is a master grid in masterdetail)
        self.__col_dbnames = ''       # original database field names
        self.__col_hiddens = OrderedDict()        # columns that are hidden
        self.__col_titles  = OrderedDict()        # descriptive titles
        self.__col_readonly = []      # columns read only
        self.__col_required = []      # required when editing
        self.__col_links = []         # hyplinks (formatter:link)
        self.__col_dynalinks = []     # dynamic hyplinks (formmatter:showLink)
        self.__col_edittypes = []     # editype -> HTML control used in edit
        self.__col_formats = OrderedDict()         # format types
        self.__col_datatypes = []     # data type used in editrule
        self.__col_imgs = []          # image columns
        self.__col_custom = []        # custom formatted columns
        self.__col_custom_css = []    # custom formatted columns
        self.__col_wysiwyg = []        # wysiwyg column (textara only)
        self.__col_default = []        # column default value
        self.__col_frozen = OrderedDict()        # column frozen
        self.__col_widths = OrderedDict()        # columns width
        self.__col_aligns = OrderedDict()        # columns alignment
        self.__col_edit_dimension = [] # size attribuet for input text, or cols and rows for textarea
        self.__col_fileupload = []     # file upload
        self.__col_virtual = []        # virtual columns
        self.__col_customrule = []    # custom validation/rule
        self.__col_autocomplete = []  # autocomplete with Chosen
        self.__col_nested_dd = []     # nested dropdown
        self.__col_headerTitles = []  # header tooltip
        self.__sql_filter = []        #  set filter
        self.__jq_summary_col_name = []
        self.__jq_summary_type = ''
        self.__jq_showSummaryOnHide = False

        # jqgrid
        # self.__jq_gridName = ''
        self.__jq_datatype = 'json'
        self.__jq_url = '"' + app.config['ABS_PATH'] + 'data?dt=' + self.__jq_datatype + '&gn=' + self.__jq_gridName + '"'  # Notice double quote
        self.__jq_mtype = 'GET'
        self.__jq_colNames = []
        # self.__jq_pagerName = ''
        self.__jq_rowNum = 10
        self.__jq_rowList = [10, 25, 50, 100, 200, 500, "10000:All"]
        self.__jq_sortname = 1
        self.__jq_sortorder = 'asc'
        self.__jq_viewrecords = True    # display recornds count in pager
        self.__jq_pgtext = 'Page {0} of {1}'         # e.g. Page {current page} of {total pages}
        self.__jq_multiselect = False    # display checkbox for each row
        self.__jq_multipage = True      # keep selected rows during pagination
        self.__jq_multiselectPosition = 'right'    # leflt or right
        self.__jq_autowidth = False      # when true the width is set to 100%
        self.__jq_width = 'auto'
        self.__jq_height = 'auto'         

        # START all the variables for the group
        self.__jq_grouping = False
        self.__jq_group_name = ''
        self.__jq_group_summary_show = False
        self.__jq_direction = 'ltr'
        self.__jq_groupcollapse = False
        self.__jq_summary_type =''
        self.__jq_showSummaryOnHide = False
        self.__jq_is_group_summary = False
        self.__jq_autoresizeOnLoad = True
        
        # END all the variables for the group

        # self.__jq_caption = ''
        self.__jq_cellEdit = False       # cell edit when true
        self.__jq_altRows = True            # can have alternative row, or zebra, color
        self.__jq_scrollOffset = 0       # horizontal scroll bar offset
        self.__jq_editurl = ''            # inline edit url
        self.__jq_rownumbers = False     # row index
        self.__jq_forceFit = ''           # maintain overall grid width when resizing a column
        self.__jq_shrinkToFit = True
        self.__jq_loadtext = 'Loading...'       # load promote text
        self.__jq_scroll = False         # use vertical scrollbar to load data. pager is disabled automately if true. height MUST NOT be 100% if true.
        self.__jq_hiddengrid = False     # hide grid initially
        self.__jq_gridview = True           # load all the data at once result in faster rendering. However, if set to true No Subgrid, treeGrid, afterInsertRow
        self.__jq_autoresizeOnLoad = True # Auto resize on load (requires autoresize flag set to true in colum property)
    
        # jquery ui
        self.__jqu_resize = {'is_resizable' : False, 'min_width' : 300, 'min_height' : 100}         # resize grid
        
        # others
        self.__num_rows = 0
        self.__num_fields = 0
        self.__ver_num = 'pythonGrid(v1.2) {free-jqGrid:v4.13.6, jQuery:v3.3.1, jQuery UI:1.11.2}'
        self.__form_width = 580        # FORM edit dialog width. jqgrid defaults to 300, so does 
        self.__form_height = '100%'       # FORM edit dialog height. the height default to -1 (an invalid #, so jqgrid will automatically resize based on # of lines
        self.__edit_mode  = 'NONE'        # CELL, INLINE, FORM, or NONE
        self.__edit_options = None      # CRUD options
        self.__has_tbarsearch = False    # integrated toolbar
        self.__auto_filters = []      # Excel like auto filter in toolbar search
        self.__advanced_search = False
        self.__sys_msg = None           # system message, e.g. error, alert
        self.__alt_colors = {'hover' : '#F2FC9C', 'highlight' : 'yellow !important', 'altrow' : '#F5FAFF'}        # row color class: ui-priority-secondary, ui-state-highlight, ui-state-hover
        self.__theme_name = 'bootstrap'        # jQuery UI theme name
        self.__locale = 'en'
        self.__auto_resize = False       # resize grid when browser resizes
        self.__kb_nav = False            # keyboard navigation (jqgrid 4.x)
        self.__pivotoptions = []      # array holds pivot grid options?
        self.__dnd_grouping = False      # drag and drop grouping
        self.__persist_state = False     # boolean - persist grid states with HTML5 localStorage
        self.__can_copyow = False        # copy/clone row

        # conditional formatting
        self.__jq_rowConditions = []
        self.__jq_cellConditions = []

        # grid elements for display
        self.__script_includeonce = ''     # jqgrid js include file
        self.__script_body = ''            # jqgrid everything else
        self.__script_editEvtHandler = ''  # jquery edit event handler script

        self.__script_ude_handler = ''     # user defined event handler
        self.__cust_col_properties = []    # Array, custom user defined custom column property
        self.__cust_grid_properties = []   # Array, custom user defined grid property
        self.__img_baseUrl = ''           # image base URL to image column. Only a SINGLE image base url is supported in a datagrid
        self.__grid_methods = []          # array. jqGrid methods
        self.__edit_file = 'edit.py'             # used in jq_editurl. Set by enable_edit 3rd parameter. default to 'edit.php'

        # ------ form only --------
        self.__formonly = False              # form only flag
        self.__load_pk = None                  # PK to load a record in form only mode
        self.__form_group_header = []
        self.__form_tooltip = []
        self.__iconSet = 'fontAwesome'
        self.__guiStyle = 'bootstrap' if self.__theme_name == 'bootstrap' else 'jQueryUI'

        # ------- export ----------
        self.export_type    = None    # Export to EXCEL, HTML, PDF
        self.export_url = app.config['ABS_PATH'] + 'export?dt=' + self.__jq_datatype + '&gn=' + self.__jq_gridName 

        return


    def __del__(self):
        if self.db.open:
            self.db.close()

    
    def display_script_includeonce(self):
        return """<link rel="stylesheet" id="theme-custom-style" type="text/css" media="screen" href="/static/css/bootstrap/jquery-ui.css" />
            <link rel="stylesheet" href="/static/js/multiselect/ui.multiselect.min.css">
            <link rel="stylesheet" type="text/css" media="screen" href="/static/css/ui.jqgrid.css" />
            <link rel="stylesheet" type="text/css" href="/static/css/datagrid.css">
            <link rel="stylesheet" type="text/css" media="screen" href="/static/js/datetimepicker/jquery-ui-timepicker-addon.css" />
            <script src="/static/js/jquery-3.3.1.min.js" type="text/javascript"></script>
            <script src="/static/js/jquery-migrate-3.0.1.min.js" type="text/javascript"></script>
            <script src="/static/js/jquery-ui-1.11.2.min.js" type="text/javascript"></script>
            <script src="/static/js/multiselect/ui.multiselect.min.js" type="text/javascript"></script>
            <script src="/static/js/i18n/grid.locale-en.js" type="text/javascript"></script>
            <script src="/static/js/jquery.jqgrid.min.js" type="text/javascript"></script>
            <script src="/static/js/grid.import.fix.js" type="text/javascript"></script>
            <script src="/static/js/datetimepicker/jquery-ui-timepicker-addon.js" type="text/javascript"></script>
            <script src="/static/js/jquery.browser.min.js" type="text/javascript"></script>
            <script src="/static/js/notify.min.js" type="text/javascript"></script>
            <script type="text/javascript">
                if (typeof $().modal != "function"){document.write("<link rel='stylesheet' href='/static/css/bootstrap.min.css'>") }
            </script>
            <link rel="stylesheet" href="/static/css/bootstrap/pg-jqgrid-bootstrap.css">
            <script type="text/javascript">
                if (typeof $().modal != "function"){document.write("<link rel='stylesheet' href='/static/css/font-awesome.min.css'>") }
            </script>"""
    

    def display_properties_main(self):
        props = ''

        if self.__jq_datatype != "local":
            props += 'url:' + self.__jq_url + ",\n"
        else:
            props += 'data: _grid_' + self.__jq_gridName  + ",\n"

        props += 'datatype:"' + self.__jq_datatype + "\",\n"
        props += 'mtype:"' + self.__jq_mtype + "\",\n"
        props += 'colNames:' + json.dumps(self.__jq_colNames) + ",\n"
        props += 'colModel:' + json.dumps(self.jq_colModel) + ",\n"
        props += 'pager: ' + self.__jq_pagerName + ",\n"
        props += 'rowNum:' + str(self.__jq_rowNum).lower() + ",\n"
        props += 'rowList:' + json.dumps(self.__jq_rowList) + ",\n"
        props += 'sortname:"' + str(self.__jq_sortname).lower() + "\",\n"
        props += 'sortorder:"' + self.__jq_sortorder + "\",\n"
        props += 'viewrecords:' + str(self.__jq_viewrecords).lower() + ",\n"
        props += 'pgtext:"' + self.__jq_pgtext + "\",\n"
        props += 'multiselect:'+ str(self.__jq_multiselect).lower() + ",\n"
        props += 'multiPageSelection:'+ str(self.__jq_multipage).lower() + ",\n"
        props += 'multiselectPosition:"' + self.__jq_multiselectPosition + "\",\n"
        props += 'caption:"' + string.capwords(self.__jq_caption) + "\",\n"
        props += 'altRows:'+ str(self.__jq_altRows).lower() + ",\n"
        props += 'scrollOffset:' + str(self.__jq_scrollOffset).lower() + ",\n"
        props += 'rownumbers:'+ str(self.__jq_rownumbers).lower() + ",\n"
        props += 'shrinkToFit:'+ str(self.__jq_shrinkToFit).lower() + ",\n"
        props += 'autowidth:'+ str(self.__jq_autowidth).lower() + ",\n"
        props += 'hiddengrid:'+ str(self.__jq_hiddengrid).lower() + ",\n"
        props += 'scroll:'+ str(self.__jq_scroll).lower() + ",\n"
        props += 'height:"' + str(self.__jq_height) + "\",\n"
        props += 'autoresizeOnLoad:'+ str(self.__jq_autoresizeOnLoad).lower() + ",\n"
        props += 'iconSet:"' + self.__iconSet + "\",\n"
        props += 'guiStyle:"' + ('bootstrap' if self.__theme_name.lower() == 'bootstrap' else 'jQueryUI') + "\",\n"
        props += 'autoencode:'+ str(self.autoencode).lower() + ",\n"
        props += 'checkOnUpdate:true' + ",\n"
        props += 'singleSelectClickMode:"selectonly"' + ",\n"

        props += 'widthOrg:"' + str(self.__jq_width) + '"' + ",\n"
        if not self.__jq_autoresizeOnLoad:
            props += 'width:"' + str(self.__jq_width) + '"' + ",\n"
        
        props += 'sortable:' + str(len(self.__col_frozen)==0).lower() + ",\n"
        props += 'loadError:' + """ 
                    function(xhr,status, err) {
                        try{
                            jQuery.jgrid.info_dialog(
                                jQuery.jgrid.errors.errcap,
                                "<div style='font-size:10px;text-align:left;width:300px;height:150px;overflow:auto;color:red;'>"+ xhr.responseText +"</div>",
                                jQuery.jgrid.edit.bClose,{buttonalign:"center"});
                        }
                        catch(e) { alert(xhr.responseText)};
                    }""" + ",\n"

         # START Grouping
        if self.__jq_grouping:
            props += 'direction:"' + self.__jq_direction + "\",\n"
            props += 'grouping:' + str(self.__jq_grouping).lower() + ",\n"
            props += 'groupingView:{ groupField :["' + self.__jq_group_name + '"], ' \
                        'groupSummary : ["' + str(self.__jq_is_group_summary).lower() + '"], ' \
                        'showSummaryOnHide : "' + str(self.__jq_showSummaryOnHide).lower() + '" ' \
                        'groupColumnShow : ["' + str(self.__jq_group_summary_show).lower() + '"] ' \
                        'groupCollapse  : "' + str(self.__jq_groupcollapse).lower()  + '", ' \
                        'groupText : ["<b>{0} - {1} Item(s)</b>"] }' \
                        ",\n"
        # End Grouping

        props += 'gridview:' + str(self.__jq_gridview).lower() + ",\n"

        if self.__edit_mode == 'CELL':
            props += 'cellEdit:true,' + "\n"
            props += 'cellsubmit:"remote",' + "\n"
            props += 'cellurl:"' + app.config['ABS_PATH'] + 'edit?dt=json&gn=' + self.__jq_gridName  + '",' + "\n"


        elif self.__edit_mode == 'INLINE':
            props += """onSelectRow: function(id, status, e){
                var grid = $(this);
                    if(id && id!==lastSel){
                        grid.restoreRow(lastSel);
                        lastSel=id;
                    }""" + "\n"

            if self.__edit_options.rfind('U') != -1:

                props += """grid.jqGrid("editRow", id, {
                        focusField: function(){ return((e) ? e.target : null) },
                        keys:true,
                        oneditfunc:function(){""" + "\n";

                if not self.__col_autocomplete:
                    for col_name in self.__col_autocomplete:
                        props += '$("#' + self.__jq_gridName + ' tr#"+id+" td select[id="+id+"_' + col_name + ']").select2({width:"100%",minimumInputLength:0});' + "\n"
                        # props += $this->get_nested_dropdown_js($col_name);

                for key, value in enumerate(self.__col_wysiwyg):
                    props += '$("#"+id+"_' + key + '").wysiwyg({' \
                            """plugins: {
                                autoload: true,
                                i18n: { lang: "en" },
                                rmFormat: { rmMsWordMarkup: true }
                            },
                            autoSave:true,
                            controls: {
                                html: {visible: true},
                                colorpicker: {
                                    groupIndex: 11,
                                    visible: true,
                                    css: {
                                        "color": function (cssValue, Wysiwyg) {
                                            var document = Wysiwyg.innerDocument(),
                                                defaultTextareaColor = $(document.body).css("color");

                                            if (cssValue !== defaultTextareaColor) {
                                                return true;
                                            }

                                            return false;
                                        }
                                    },
                                    exec: function() {
                                        if ($.wysiwyg.controls.colorpicker) {
                                            $.wysiwyg.controls.colorpicker.init(this);
                                        }
                                    },
                                    tooltip: "Colorpicker"
                                }
                            }

                    });"""


                props += '},' + "\n" # oneditfunc,
                props += """aftersavefunc:function(id, result){
                                setTimeout(function(){
                                    grid.focus();  // set focus after save
                                    // displayCrudServerErr(result);
                                },100);

                        },""" + "\n"
                props += 'errorfunc:function(){}' + "\n" # errorfunc - only called when status code is not 200.
                props += '});' + "\n" # grid.jqGrid("editRow"...
                
                # do not focus selected cell when keybaord nav is enabled 
                if not self.__kb_nav:
                    props += 'if(e){ setTimeout(function(){$("input, select, textarea",e.target).focus();}, 0) }' + "\n"


            props += '},// onSelectRow' + "\n"
            props += 'editurl:"' + self.__jq_editurl + '"' + ",\n"

        elif self.__edit_mode == 'FORM':
            props += ''

        
        props += self.cust_prop_jsonstr + "\n"

        if not self.__cust_grid_properties:
            props += '' # substr(substr(json.dumps(self.__cust_grid_properties),1),0,-1) + ",\n"

        # conditional formatting 
        # ...

        return props


    def prepare_grid(self):

        connection = self.db.raw_connection()

        try:
            with connection.cursor() as cursor:
                cursor.execute(self.__sql)
                result = cursor.fetchall()

                field_names = [i[0] for i in cursor.description]

                self.__num_fields = len(cursor.description)    
                self.__num_rows = 0


                self.set_colNames(result, field_names)            
                self.set_colModels(result, cursor.description)            
                
        finally:
            pass #connection.close()

        return


    def set_colNames(self, result, field_names):

        col_names = []

        for col_name in field_names:
            # check descriptive titles
            if col_name in self.__col_titles:
                col_names.append(self.__col_titles[col_name])
            else:
                col_names.append(col_name.replace('_', ' '))

        self.__jq_colNames = col_names

        return col_names



    def set_colModels(self, result, meta_data):

        self.jq_colModel = [] # must reset each time, Flask keeps the list in memory somehow
        connection = self.db
        colModel = []

        field_names = [i[0] for i in meta_data]
        field_types = [i[1] for i in meta_data]


        """ 
        meta atrributes (https://www.python.org/dev/peps/pep-0249/#cursor-attributes)
        mysql field type constants (http://mysql-python.sourceforge.net/MySQLdb-1.2.2/public/MySQLdb.constants.FIELD_TYPE-module.html)
        
        name
        type_code
        display_size
        internal_size
        precision
        scale
        null_ok
        """
        # app.logger.info(meta_data)

        """
        # sample meta atrribute output above
        app:(('employeeNumber', 3, None, 11, 11, 0, False), ('lastName', 253, None, 200, 200, 0, False), ('firstName', 253, None, 200, 200, 0, False), ('isActive', 1, None, 1, 1, 0, True), ('extension', 253, None, 40, 40, 0, False), ('email', 253, None, 400, 400, 0, False), ('officeCode', 253, None, 40, 40, 0, False), ('reportsTo', 3, None, 11, 11, 0, True), ('jobTitle', 253, None, 200, 200, 0, False))
        """


        i = 0
        
        

        while i < self.__num_fields:
            cols = OrderedDict()

            col_name = field_names[i]
            col_type = field_types[i]

            cols['autoResizable'] = True
            cols['name'] = col_name
            cols['index'] = col_name
            cols['hidden'] = True if col_name in self.__col_hiddens.keys() else False
            #cols['headerTitle'] = isset($this->col_headerTitles[$col_name]) ? $this->col_headerTitles[$col_name] : $col_name;

            # set freeze coulmns
            if col_name in self.__col_frozen.keys():
                cols['fronze'] = self.__col_frozen[col_name]

            # set width of coulmns
            if col_name in self.__col_widths.keys():
                cols['width'] = self.__col_widths[col_name]['width']

            # set column alignments
            if col_name in self.__col_aligns.keys():
                cols['align'] = self.__col_aligns[col_name]['align']


            if self.__edit_mode == 'CELL' or self.__edit_mode == 'INLINE':
                cols['editable'] = False if col_name in self.__col_readonly else True
            elif self.__edit_mode == 'FORM':
                cols['editable'] = True
            else:
                cols['editable'] = False

            # --------------- editoptions ----------------
            # set default text input width, the default edit type is text
            editoptions =  OrderedDict()
            editoptions['size'] = '30'

            # --------------- editrules ----------------
            editrules = OrderedDict()

            # $editrules['edithidden'] = (isset($this->col_hiddens[$col_name]['edithidden']) && $this->col_hiddens[$col_name]['edithidden']==true)?true:false;
            editrules['required'] = True if col_name in self.__col_required else False

            if col_type == 10 or col_type == 12 or col_type == 14:
                editrules['date'] = True
            elif col_type == 3:
                editrules['number'] = True
            else:
                pass

            cols['editrules'] = dict(editrules)

            colModel.append(dict(cols))
            cols = []

            i += 1

        #app.logger.info(json.dumps(colModel))
        self.jq_colModel.extend(colModel)

        return


    def display_events(self):
        events  = '<script type="text/javascript">' + "\n"
        events += 'jQuery(document).ready(function($){ ' + "\n"

        events += self.__script_ude_handler

        if len(self.__col_frozen) > 0 :
            events += '$("#' + self.__jq_gridName + '").jqGrid("setFrozenColumns");' + "\n"

        events += '}); // jQuery("#table1").jqGrid({' + "\n"
        events += '</script>' + "\n"

        return events


    def display_script_begin(self):
        script_begin = ''
        
        script_begin += '<script type="text/javascript">' + "\n";
        script_begin += '//<![CDATA[' + "\n"
        script_begin += 'var lastSel;' + "\n"       
        script_begin += 'var pg_' + self.__jq_gridName + ';' + "\n"
        script_begin += 'jQuery(document).ready(function($){ ' + "\n"

        if self.__has_tbarsearch and len(self.__auto_filters) > 0:
            script_begin += """var getUniqueNames = function (columnName) {
                var texts = this.jqGrid("getCol", columnName), uniqueTexts = [],
                    textsLength = texts.length, text, textsMap = {}, i;
                for (i = 0; i < textsLength; i++) {
                    text = texts[i];
                    if (text !== undefined && textsMap[text] === undefined) {
                        // to test whether the texts is unique we place it in the map.
                        textsMap[text] = true;
                        uniqueTexts.push(text);
                    }
                }

                return uniqueTexts;
            },
            buildSearchSelect = function (uniqueNames) {
                var values = ":All";
                $.each(uniqueNames, function () {
                    values += ";" + this + ":" + this;
                });

                return values;
            },
            setSearchSelect = function (columnName) {
                this.jqGrid("setColProp", columnName, {
                    stype: "select",
                    searchoptions: {
                        value: buildSearchSelect(getUniqueNames.call(this, columnName)),
                        sopt: ["eq"]
                    }
                });
            };\n """ 

        return script_begin


    def display_style(self):
        style = '<style type="text/css">' + "\n"

        if self.__alt_colors is not None:
            
            if self.__alt_colors['altrow'] is not None:
                style += '#' + self.__jq_gridName + ' .ui-priority-secondary{background-image: none;background:' + self.__alt_colors['altrow'] + ';}' + "\n"
            style += '#' + self.__jq_gridName + ' .ui-state-hover{background-image: none;background:' + self.__alt_colors['hover'] + ';color:black}' + "\n"
            
            if self.__alt_colors['highlight'] is not None:
                style += '#' + self.__jq_gridName + ' .ui-state-highlight{background-image: none;background:' + self.__alt_colors['highlight'] + ';}' + "\n"
            style += 'table#' + self.__jq_gridName + ' tr{ opacity: 1}' + "\n"

        # overwrite frozen column transparenncy
        if len(self.__col_frozen) > 0 :
            style += 'table#' + self.__jq_gridName + '_frozen{background-color:white};'

        style += '</style>' + "\n"

        return style

    def display_properties_begin(self):
        return 'pg_' + self.__jq_gridName + ' = jQuery("#' + self.__jq_gridName + '").jqGrid({' + "\n"


    # Desc: end of main jqGrid (before toolbar)
    def display_properties_end(self):
        properties_end = 'loadtext:"' + self.__jq_loadtext + "\"\n"  # last properties - no ending comma.
        properties_end += '});' + "\n"

        return properties_end


    def display_toolbar(self):
        toolbar = ''

        if self.__edit_mode == 'FORM' or self.__edit_mode == 'INLINE':
            pass
        elif self.__edit_mode == 'NONE':
            exp_type = 'true' if self.export_type is not None else 'false'

            toolbar += 'jQuery("#' + self.__jq_gridName + '").jqGrid("navGrid", ' + self.__jq_pagerName + ","
            toolbar += '{edit:false,add:false,del:false,view:false,search:false,excel:' + exp_type +'}, {});' + "\n"

        # resizable grid (beta - jQuery UI)
        if self.__jqu_resize['is_resizable']:
            toolbar += 'jQuery("#' + self.__jq_gridName + '").jqGrid("gridResize",{minWidth:'. self.__jqu_resize['min_width'] + ',minHeight:' + self.__jqu_resize['min_height'] + '});' + "\n"

        # inline search
        if self.__has_tbarsearch:
            search_icon = 'fa-search' if (self.__iconSet == 'fontAwesome') else 'ui-icon-search'

            toolbar += f"jQuery('#{self.__jq_gridName}').jqGrid('navButtonAdd', {self.__jq_pagerName}, {{caption:'',title:'Toggle inline search', buttonicon :'{search_icon}',\n \
                        onClickButton:function(){{\n \
                            pg_{self.__jq_gridName}[0].toggleToolbar();\n \
                        }}\n \
                    }});\n"

            toolbar += 'jQuery("#' + self.__jq_gridName + '").jqGrid("filterToolbar", {searchOnEnter: false, stringResult: true, defaultSearch: "cn"}); ' + "\n"
            toolbar += 'pg_' + self.__jq_gridName + '[0].toggleToolbar();' + "\n"   # hide inline search by default

        # advanced search
        if self.__advanced_search:
            icon_set = 'fa-search-plus' if self.__iconSet == 'fontAwesome' else 'ui-icon-search'

            toolbar += f"jQuery('#{self.__jq_gridName}') \n \
                .navGrid('{self.__jq_pagerName}',{{edit:false,add:false,del:false,search:false,refresh:false}}) \n \
                .navButtonAdd({self.__jq_pagerName},{{ \n \
                    caption:'', \n \
                    buttonicon:'{icon_set}', \n \
                    onClickButton: function(){{ \n \
                        jQuery('#{self.__jq_gridName}').jqGrid('searchGrid', {{multipleSearch:true}}) \n \
                }}, \n \
                position:'first' \n \
            }});\n"

        # Excel export
        if self.export_type is not None:
            toolbar += 'jQuery("#' + self.__jq_gridName + '").jqGrid("navButtonAdd",' + self.__jq_pagerName + ',{caption:"",title:"' + self.export_type + '", \n \
                        onClickButton:function(e){ \n \
                                window.location= "' + self.export_url + '&export_type=' + self.export_type + '"; \n  \
                        } \
                    });' + "\n"
        
        return toolbar


    def display_before_script_end(self):
        return self.before_script_end


    def display_script_end(self):
        script_end = ''

        # function call required for toolbar search dynamic filter dropdown based on unique column values
        if self.__has_tbarsearch and len(self.__auto_filters) > 0:
            for col_name in self.__auto_filters:
                script_end += 'setSearchSelect.call(pg_' + self.__jq_gridName + ', ' + col_name + ');' + "\n"

            script_end += f"pg_{self.__jq_gridName}.jqGrid('setColProp', 'Name', {{ \n \
                searchoptions: {{ \n \
                    sopt: ['cn'], \n \
                    dataInit: function (elem) {{ \n \
                        $(elem).autocomplete({{ \n \
                            source: getUniqueNames.call($(this), 'Name'), \n \
                            delay: 0, \n \
                            minLength: 0, \n \
                            select: function (event, ui) {{ \n \
                                var $myGrid, grid; \n \
                                $(elem).val(ui.item.value); \n \
                                if (typeof elem.id === 'string' && elem.id.substr(0, 3) === 'gs_') {{ \n \
                                    $myGrid = $(elem).closest('div.ui-jqgrid-hdiv').next('div.ui-jqgrid-bdiv').find('table.ui-jqgrid-btable').first(); \n \
                                    if ($myGrid.length > 0) {{  \n \
                                        grid = $myGrid[0]; \n \
                                        if ($.isFunction(grid.triggerToolbar)) {{ \n \
                                            grid.triggerToolbar(); \n \
                                        }}  \n \
                                    }} \n \
                                }} else {{  \n \
                                    // to refresh the filter \n \
                                    $(elem).trigger('change'); \n \
                                }} \n \
                            }} \n \
                        }}); \n \
                    }} \n \
                }} \n \
            }});" + "\n"

            script_end += 'pg_' + self.__jq_gridName + '.jqGrid("destroyFilterToolbar");'
            script_end += 'pg_' + self.__jq_gridName + '.jqGrid("filterToolbar",{stringResult: true, searchOnEnter: true, defaultSearch: "cn"});' + "\n"
            script_end += 'pg_' + self.__jq_gridName + '[0].triggerToolbar();' + "\n";


        script_end += "\n" + '}); // jQuery(document).ready(function($){ ' + "\n"

        script_end += f"function getSelRows() \n \
             {{ \n \
                var rows = jQuery('#{self.__jq_gridName}').jqGrid('getGridParam','selarrrow'); \n \
                return rows; \n \
             }}" + "\n"

        script_end += '//]]>' + "\n"
        script_end += '</script>' + "\n"

        return script_end

    # Desc: html element as grid placehoder
    # Must strip out # sign
    def __display_container(self):
        container = '<table id="' + self.__jq_gridName + '"></table>' + "\n"
        container += '<div id=' + self.__jq_pagerName.replace('#', '') + '></div>' + "\n"
        container += '<br />' + "\n"

        return container



    def display(self):
        
        self.prepare_grid()
        
        disp = ''
        disp += self.display_script_includeonce()
        disp += self.display_style()
        disp += self.display_script_begin()
        disp += self.display_properties_begin()
        disp += self.display_properties_main()
        
        #disp += display_subgrid($subgrid_count);
        #disp += display_masterdetail();
        disp += self.display_properties_end()
        #disp += display_extended_properties();
        disp += self.display_toolbar()
        disp += self.display_before_script_end();
        disp += self.display_script_end();

        disp += self.__display_container();

        disp += self.display_events()
        
        return disp


    def set_col_title(self, col_name, new_title):
        self.__col_titles[col_name] = new_title

        return self


    def set_caption(self, capition):
        if capition == '':
            caption = '&nbsp'

        self.__jq_caption = capition

        return self


    # Note: pagination is disabled when set_scroll is set to true.
    # The grid height is set in the 2nd param of set_scroll(). See method for more info
    def set_pagesize(self, pagesize):
        self.__jq_rowNum = pagesize

        return self

    # 2nd parameter indicates whether it's also hidden during form edit
    def set_col_hidden(self, col_name, edithidden=True):
        if isinstance(col_name, list):
            for col in col_name:
                self.__col_hiddens[col] = OrderedDict()
                self.__col_hiddens[col]['edithidden'] = edithidden

        else:
            col_names = re.split("/[\s]*[,][\s]*/", col_name)
            for col in col_names:
                self.__col_hiddens[col] = OrderedDict()
                self.__col_hiddens[col]['edithidden'] = edithidden

        return self

    # set grid height and width, the default height is 100%
    def set_dimension(self, w, h='100%', shrinkToFit = True):
        self.__jq_width = w
        self.__jq_height = h
        self.__jq_shrinkToFit = shrinkToFit
        self.enable_autoresizeOnLoad(False)

        return self

    '''
    * support of auto-adjustment of the column width based on the content of data in the column 
    * and the content of the column header. To use the feature one should specify 
    * autoResizable: true property in the column
    * @param boolean $autoresizeonload whether to autoresize during page load 
    '''
    def enable_autoresizeOnLoad(self, autoresizeonload=False):
        self.__jq_autoresizeOnLoad = autoresizeonload

        return self

    def set_col_readonly(self, arr):
        if isinstance(arr, list):
            self.__col_readonly = self.__col_readonly + arr
        else:
            self.__col_readonly = self.__col_readonly + re.split("/[\s]*[,][\s]*/", arr)

        return self

    # TODO - not finished, can't test without finishing EDIT first
    def set_col_required(self, arr):
        self.__col_required = re.split("/[\s]*[,][\s]*/", arr)

        '''for col_name in self.__col_required:
            $this->cust_col_properties[$col_name] = array("formoptions"=>
                array("elmsuffix"=>"<span style='color:red;'> *</span>")
            );
        '''

        return self
    
    # Desc: formatter: integer, number, currency, date, link, showlink, email, select (special case)
    def set_col_format(self, col_name, format, formatoptions=[]):
        self.__col_formats[col_name][format] = formatoptions

         # rating formatter. Limitation. Only a single column can has rating. 2/2/2017
        if format == 'rating':
            PythonGrid.has_rating = True

            loadComplete = \
                'function() { \
                    var ids = $(' + self.__jq_gridName + ').getDataIDs(); \
                    for (var i = 0; i < ids.length; i++) { initRaty(ids[i]);} \
                }'

            self.add_event("jqGridLoadComplete", loadComplete)

        return self

    # advanced function
    # set event. new event model in jqgrid 4.3.2 will not overwrite previous handler of the same event
    def add_event(self, event_name, js_event_handler):
        self.__script_ude_handler += 'pg' + self.__jq_gridName + '.bind("' + event_name + '", ' + js_event_handler + ');' + "\n"

        return self


    '''
    * Enable integrated toolbar search
    * @param  boolean $can_search      Enable integrated toolbar search
    * @param  Array $auto_filter     Excel-like auto filter
    * @return grid object              
    '''
    def enable_search(self, can_search, auto_filters = []):
        self.__has_tbarsearch   = can_search
        self.__auto_filters     = auto_filters

        return self

    # Desc: boolean whether display sequence number to each row
    def enable_rownumbers(self, has_rownumbers):
        self.__jq_rownumbers = has_rownumbers

        return self

    def enable_pagecount(self, has_pagecount = True):
        if not has_pagecount:
            self.__jq_viewrecords = False
            self.__jq_pgtext = "Page {0}"

        return self

    # set column width
    def set_col_width(self, col_name, width):
        self.__col_widths[col_name] = OrderedDict()
        self.__col_widths[col_name]['width'] = width
        # self.set_col_property(col_name, {'autoResizable' : False})

        return self

    # set column text alignment
    def set_col_align(self, col_name, align='left'):
        self.__col_aligns[col_name] = OrderedDict()
        self.__col_aligns[col_name]['align'] = align

        return self

    # set column frozen
    def set_col_frozen(self, col_name, value=True):
        self.__col_frozen[col_name] = value # doesn't really need a value

        return self

    def enable_export(self, type='CSV'):
        self.export_type = type

        return self
