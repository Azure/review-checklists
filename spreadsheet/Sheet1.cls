VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit
Option Base 0
Private Declare PtrSafe Function URLDownloadToFile Lib "urlmon" Alias "URLDownloadToFileA" (ByVal pCaller As Long, ByVal szURL As String, ByVal szFileName As String, ByVal dwReserved As Long, ByVal lpfnCB As Long) As Long

'Constants
Const line_break = vbCrLf
Const category_column = 1
Const subcategory_column = 2
Const text_column = 3
Const description_column = 4
Const severity_column = 5
Const status_column = 6
Const comments_column = 7
Const link_column = 8
Const training_column = 9
Const graph_success_column = 10
Const graph_failure_column = 11
Const guid_column = 12
Const checklist_name_row = 2
Const checklist_name_col = 1
Const values_sheet = "values"
Const values_sev_column = 1
Const values_status_column = 2
Const values_category_column = 3
Const values_technology_selection_column = 6
Const values_language_selection_column = 7
Const row1 = 5
Const row_limit = 2000   'Safety net
Const user_info_guid_index = 1
Const user_info_comments_index = 2
Const user_info_status_index = 3
Const technology_selection_row = 1
Const technology_selection_col = 5
Const language_selection_row = 1
Const language_selection_col = 6

'Global variables
Dim user_checks() As String     'To hold the user's comments/status
Dim selected_language As String
Dim selected_technology As String
Dim import_graph_queries As Boolean

'Modifies text so that it can be stored in JSON format
' * Removes line breaks (chr10 and chr13)
' * Replaces doublequotes with single quotes
' * Eliminates blanks (replaces with &nbsp)
Function correct_format_for_JSON(ByVal input_text As String) As String
    'Remove breaks
    input_text = Replace(Replace(input_text, Chr(10), ""), Chr(13), "")
    'Replace double quotes with single quotes
    input_text = Replace(input_text, Chr(34), Chr(39))
    'If it is a link, remove localization
    input_text = Replace(input_text, "en-us/", "")
    'Escape control characters such as "?"
    'input_text = escape_character(input_text, "?")
    input_text = escape_character(input_text, "\")
    'Avoid empty fields, the Azure translate API doesnt work well with then
    If input_text = "" Then input_text = "&nbsp"
    correct_format_for_JSON = input_text
End Function

'Escapes a character in a string, and gives out the resulting string
Function escape_character(ByVal input_text As String, search_char As String) As String
    'First we remove any possible escape signs for that character that might be already there
    input_text = Replace(input_text, "\" + search_char, search_char)
    'Now we escape all occurrences of the character
    input_text = Replace(input_text, search_char, "\" + search_char)
    'And return the output
    escape_character = input_text
End Function

'Exports current checklist from excel to a json-formated text file
Sub export_json()
    On Error GoTo errh
    ' Constants
    Const export_file_name = "checklist.json"
    Const values_sheet = "values"
    Const values_category_column = 3
    ' Variables
    Dim row As Integer
    Dim json As String
    Dim check_category, check_subcategory, check_text, check_description, check_severity, check_status, check_link, check_training, check_graph_success, check_graph_failure, check_guid As String
    Dim category_name, severity_name, status_name As String
    Dim export_file_path As Variant
    Dim double_quote As String
    Dim item_count, category_count, status_count As Integer
    ' Initialization
    double_quote = Chr(34) ' double quote as a variable
    row = row1
    json = "{" + line_break
    json = json + "  " + double_quote + "items" + double_quote + ": ["
    item_count = 0
    category_count = 0
    status_count = 0
    ' Loop through all rows as long as there is content
    Do While row < row_limit And Len(Cells(row, category_column)) > 0
        If row > row1 Then json = json + ","
        json = json + line_break
        check_category = Cells(row, category_column)
        check_subcategory = Cells(row, subcategory_column)
        check_text = Cells(row, text_column)
        check_description = Cells(row, description_column)
        check_severity = Cells(row, severity_column)
        check_graph_success = Cells(row, graph_success_column)
        check_graph_failure = Cells(row, graph_failure_column)
        check_guid = LCase(Cells(row, guid_column))
        'If there was no GUID, generate one
        If Len(check_guid) = 0 Then check_guid = generate_guid()
        'Only read More Info hyperlink if the cell contains one
        If Cells(row, link_column).Hyperlinks.Count > 0 Then
            check_link = Cells(row, link_column).Hyperlinks(1).Address
        Else
            check_link = Cells(row, link_column)
        End If
        'Only read Training hyperlink if the cell contains one
        If Cells(row, training_column).Hyperlinks.Count > 0 Then
            check_training = Cells(row, training_column).Hyperlinks(1).Address
        Else
            check_training = Cells(row, training_column)
        End If
        row = row + 1
        json = json + "    {" + line_break
        json = json + "      " + double_quote + "category" + double_quote + ": " + double_quote + correct_format_for_JSON(check_category) + double_quote + ","
        json = json + line_break + "      " + double_quote + "subcategory" + double_quote + ": " + double_quote + correct_format_for_JSON(check_subcategory) + double_quote
        json = json + "," + line_break + "      " + double_quote + "text" + double_quote + ": " + double_quote + correct_format_for_JSON(check_text) + double_quote
        If Len(check_description) > 0 Then json = json + "," + line_break + "      " + double_quote + "description" + double_quote + ": " + double_quote + correct_format_for_JSON(check_description) + double_quote
        If Len(check_guid) > 0 Then json = json + "," + line_break + "      " + double_quote + "guid" + double_quote + ": " + double_quote + check_guid + double_quote
        If Len(check_severity) > 0 Then json = json + "," + line_break + "      " + double_quote + "severity" + double_quote + ": " + double_quote + check_severity + double_quote
        If Len(check_graph_success) > 0 Then json = json + "," + line_break + "      " + double_quote + "graph_success" + double_quote + ": " + double_quote + correct_format_for_JSON(check_graph_success) + double_quote
        If Len(check_graph_failure) > 0 Then json = json + "," + line_break + "      " + double_quote + "graph_failure" + double_quote + ": " + double_quote + correct_format_for_JSON(check_graph_failure) + double_quote
        If Len(check_training) > 0 Then json = json + "," + line_break + "      " + double_quote + "training" + double_quote + ": " + double_quote + correct_format_for_JSON(check_training) + double_quote
        If Len(check_link) > 0 Then json = json + "," + line_break + "      " + double_quote + "link" + double_quote + ": " + double_quote + correct_format_for_JSON(check_link) + double_quote
        json = json + line_break + "    }"
        item_count = item_count + 1
    Loop
    ' Finish items section
    json = json + line_break + "  ]," + line_break
    ' Create categories section
    json = json + "  " + double_quote + "categories" + double_quote + ": ["
    row = 2
    Do While row < row_limit And Len(Sheets(values_sheet).Cells(row, values_category_column)) > 0
        If row > 2 Then json = json + ","
        json = json + line_break
        category_name = Sheets(values_sheet).Cells(row, values_category_column)
        json = json + "    {" + line_break
        json = json + "      " + double_quote + "name" + double_quote + ": " + double_quote + correct_format_for_JSON(category_name) + double_quote + line_break
        json = json + "    }"
        row = row + 1
        category_count = category_count + 1
    Loop
    ' Finish category section
    json = json + line_break + "  ]," + line_break
    ' Create status section
    json = json + "  " + double_quote + "status" + double_quote + ": ["
    row = 2
    Do While row < row_limit And Len(Sheets(values_sheet).Cells(row, values_status_column)) > 0
        If row > 2 Then json = json + ","
        json = json + line_break
        status_name = Sheets(values_sheet).Cells(row, values_status_column)
        json = json + "    {" + line_break
        json = json + "      " + double_quote + "name" + double_quote + ": " + double_quote + correct_format_for_JSON(status_name) + double_quote + line_break
        json = json + "    }"
        row = row + 1
        status_count = status_count + 1
    Loop
    ' Finish status section
    json = json + line_break + "  ]," + line_break
    ' Create severities section
    json = json + "  " + double_quote + "severities" + double_quote + ": ["
    row = 2
    Do While row < row_limit And Len(Sheets(values_sheet).Cells(row, values_sev_column)) > 0
        If row > 2 Then json = json + ","
        json = json + line_break
        severity_name = Sheets(values_sheet).Cells(row, values_sev_column)
        json = json + "    {" + line_break
        json = json + "      " + double_quote + "name" + double_quote + ": " + double_quote + correct_format_for_JSON(severity_name) + double_quote + line_break
        json = json + "    }"
        row = row + 1
    Loop
    ' Finish severities section
    json = json + line_break + "  ]," + line_break
    ' Create metadata section
    json = json + "  " + double_quote + "metadata" + double_quote + ": {" + line_break
    json = json + "    " + double_quote + "name" + double_quote + ": " + double_quote + correct_format_for_JSON(Cells(checklist_name_row, checklist_name_col)) + double_quote + line_break
    ' Finish metadata section
    json = json + "  }" + line_break
    ' Finish JSON
    json = json + "}" + line_break
    ' Write JSON to file
    ' MsgBox json
    'export_file_path = ActiveWorkbook.Path + "\" + export_file_name
    export_file_path = ""
    export_file_path = Application.GetSaveAsFilename(FileFilter:="JSON File (*.json), *.json", Title:="Exporting JSON checklist", InitialFileName:=ActiveWorkbook.Path + "\" + export_file_name)
    'checks to make sure the user hasn't canceled the dialog
    If export_file_path <> False Then
        'MsgBox "Exporting to " + export_file_path
        Open export_file_path For Output As #1
        Print #1, json
        Close #1
    End If
    MsgBox CStr(item_count) + " checklist items and " + CStr(category_count) + " categories exported to JSON file " + export_file_path, vbInformation
    Exit Sub
errh:
    If Err.Number <> 0 Then
        MsgBox "Error while exporting checklist to JSON " & Err.Description, vbCritical
    End If
End Sub

'Import JSON from URL (first download to a local file)
Sub import_checklist_fromurl()
    Const values_sheet = "values"
    Const values_url_column = 4
    Dim checklist_url, checklist_base_url As String
    Dim json_file As Variant
    Dim buf, ret As Long
    Dim url_split() As String
    Dim filename As String
    Dim objXmlHttpReq As Object
    Dim objStream As Object
    Dim msg As String
    'Get URL stored in the Values sheet
    checklist_base_url = Sheets(values_sheet).Cells(2, values_url_column)
    If Len(checklist_base_url) > 0 Then
        'Look at the option buttons to set global variables that control technology (LZ, AKS, AVD) and language
        set_checklist_variables
        'Append the technology and options variables (default to English and LZ)
        If Len(selected_technology) = 0 Then selected_technology = "lz"
        If Len(selected_language) = 0 Then selected_language = "en"
        checklist_url = checklist_base_url + selected_technology + "_checklist." + selected_language + ".json"
        'Get the filename of the URL
        url_split = Split(checklist_url, "/")
        filename = url_split(UBound(url_split))
        ' Instead of letting the user specify a download directory, picking up Downloads per default
        'ChDir ActiveWorkbook.Path
        'json_file = Application.GetOpenFilename(Title:="Please choose a file to open", FileFilter:="JSON Files *.json* (*.json),")
        json_file = Environ("USERPROFILE") + "\Downloads\checklist.json"
        msg = "Reference checklist will be downloaded from '" + checklist_url + "' to '" + CStr(json_file) + "'"
        If MsgBox(msg, vbOKCancel + vbQuestion, "Downloading reference checklist") = vbOK Then
            ret = URLDownloadToFile(0, checklist_url, json_file, 0, 0)
            If ret = 0 Then
                'Call the sub for actually doing the import
                import_checklist_fromfile json_file
            Else
                MsgBox "Checklist could not be downloaded from '" + checklist_url + "'", vbCritical
            End If
        End If
    Else
        MsgBox "Sorry, I could not found out the reference URL in sheet '" + values_sheet + "' at cell location 2," + CStr(values_url_column), vbCritical
    End If
End Sub

'Import from custom JSON file
Sub import_checklist()
    Dim json_file As Variant
    ChDir ActiveWorkbook.Path
    json_file = Application.GetOpenFilename(Title:="Please choose a file to open", FileFilter:="JSON Files *.json* (*.json),")
    If json_file = False Then
        MsgBox "No file selected.", vbExclamation, "Action canceled"
        Exit Sub
    Else
        import_graph_queries = True 'Always import graph queries in advanced mode.
        import_checklist_fromfile json_file
    End If
End Sub


'Import from a local JSON file
'Parse JSON code using the JsonConverter module
Sub import_checklist_fromfile(json_file As Variant)
    On Error GoTo import_checklist_fromfile_err
    ' Constants
    Const row1 = 5
    Const row_limit = 2000   'Safety net
    'Variables
    Dim json_ts As TextStream
    Dim FSO As New FileSystemObject
    Dim textline As String
    Dim json As String
    Dim json_object, json_item As Object
    Dim double_quote As String
    Dim line_elements() As String
    Dim row, item_count, category_count, status_count, i As Integer
    Dim notverified As String
    Dim get_user_info_successful As Boolean
    'Initialization
    row = row1
    double_quote = Chr(34) ' double quote as a variable
    json = ""
    item_count = 0
    category_count = 0
    status_count = 0
    'First of all, get the info entered by the user in a global variable
    get_user_info_successful = get_user_input()
    'Go through the file line by line
    Dim objStream
    Set objStream = CreateObject("ADODB.Stream")
    objStream.Charset = "utf-8"
    objStream.Open
    objStream.LoadFromFile (json_file)
    json = objStream.ReadText()
    
    objStream.Close
    Set objStream = Nothing

    json = Replace(json, vbCrLf, "")
    Set json_object = JsonConverter.ParseJson(json)  'This line might give Run-time error 10001 if there are JSON syntactic errors
    'Update checklist title
    If json_object.Exists("metadata") Then
        If json_object("metadata").Exists("name") Then
            Cells(checklist_name_row, checklist_name_col) = json_object("metadata")("name")
        End If
    End If
    'Import status
    If json_object.Exists("status") Then
        row = 2
        If TypeName(json_object("status")) = "Dictionary" Then
            notverified = json_object("status")("0")("name") ' The "Not Verified" status is the first one
            i = 0
            Do
                Sheets(values_sheet).Cells(row, values_status_column) = json_object("status")(CStr(i))("name")
                row = row + 1
                status_count = status_count + 1
                i = i + 1
            Loop While json_object("status").Exists(CStr(i))
        Else
            notverified = json_object("status")(1)("name") ' The "Not Verified" status is the first one
            For Each json_item In json_object("status")
                Sheets(values_sheet).Cells(row, values_status_column) = json_item("name")
                row = row + 1
                status_count = status_count + 1
            Next json_item
        End If
        'Blank the rest of the status rows, although for status this shouldnt be required
        Do While row < row_limit And Len(Cells(row, values_status_column)) > 0
            Sheets(values_sheet).Cells(row, values_status_column) = ""
            row = row + 1
        Loop
    End If
    'Import checklist items
    row = row1
    'If JSON is a translated file, it is a nested dictionary with keys "0", "1", etc
    If TypeName(json_object("items")) = "Dictionary" Then
        i = 0
        Do
            update_row json_object("items")(CStr(i)), row, notverified, get_user_info_successful
            row = row + 1
            item_count = item_count + 1
            i = i + 1
        Loop While json_object("items").Exists(CStr(i))
    'Otherwise, it is just an array
    Else
        For Each json_item In json_object("items")
            update_row json_item, row, notverified, get_user_info_successful
            row = row + 1
            item_count = item_count + 1
        Next json_item
    End If
    'Blank the rest of the item rows
    Do While row < row_limit And (Len(Cells(row, category_column)) + Len(Cells(row, subcategory_column)) + Len(Cells(row, text_column)) + Len(Cells(row, status_column)) + Len(Cells(row, comments_column))) > 0
        Cells(row, category_column) = ""
        Cells(row, subcategory_column) = ""
        Cells(row, text_column) = ""
        Cells(row, description_column) = ""
        Cells(row, severity_column) = ""
        Cells(row, link_column) = ""
        Cells(row, status_column) = ""
        Cells(row, comments_column) = ""
        Cells(row, training_column) = ""
        Cells(row, graph_success_column) = ""
        Cells(row, graph_failure_column) = ""
        Cells(row, guid_column) = ""
        row = row + 1
    Loop
    'Import categories
    If json_object.Exists("categories") Then
        row = 2
        If TypeName(json_object("categories")) = "Dictionary" Then
            i = 0
            Do
                Sheets(values_sheet).Cells(row, values_category_column) = json_object("categories")(CStr(i))("name")
                row = row + 1
                category_count = category_count + 1
                i = i + 1
            Loop While json_object("categories").Exists(CStr(i))
        Else
            For Each json_item In json_object("categories")
                Sheets(values_sheet).Cells(row, values_category_column) = json_item("name")
                row = row + 1
                category_count = category_count + 1
            Next json_item
        End If
        'Blank the rest of the category rows
        Do While row < row_limit And Len(Cells(row, values_category_column)) > 0
            Sheets(values_sheet).Cells(row, values_category_column) = ""
            row = row + 1
        Loop
    End If
    'Import severities
    If json_object.Exists("severities") Then
        row = 2
        If TypeName(json_object("severities")) = "Dictionary" Then
            i = 0
            Do
                Sheets(values_sheet).Cells(row, values_sev_column) = json_object("severities")(CStr(i))("name")
                row = row + 1
                i = i + 1
            Loop While json_object("severities").Exists(CStr(i))
        Else
            For Each json_item In json_object("severities")
                Sheets(values_sheet).Cells(row, values_sev_column) = json_item("name")
                row = row + 1
            Next json_item
        End If
        'Blank the rest of the severity rows
        Do While row < row_limit And Len(Cells(row, values_sev_column)) > 0
            Sheets(values_sheet).Cells(row, values_sev_column) = ""
            row = row + 1
        Loop
    End If
    MsgBox CStr(item_count) + " check items and " + CStr(category_count) + " categories imported from JSON file " + json_file, vbInformation
    Exit Sub
import_checklist_fromfile_err:
    If Err.Number <> 0 Then
        MsgBox "Error while importing checklist from JSON file " & json_file & ": " & Err.Description, vbCritical
    End If
End Sub

'Function with error control in case a property does not exist for an object
Function get_object_property(ByVal object_item As Object, property_name As String) As String
    On Error GoTo get_object_property_err
    Dim aux As String
    aux = object_item(property_name)
    'If it is "&nbsp" or something similar (some translation engines introduce blanks between "&" and "nbsp"), set to null
    If Right(aux, 4) = "nbsp" Then aux = ""
    get_object_property = aux
    Exit Function
get_object_property_err:
    get_object_property = ""
    Exit Function
End Function

' Updates a checklist row with the information in the object
Sub update_row(ByVal json_item As Object, ByVal row As Integer, notverified As String, user_input_saved As Boolean)
On Error GoTo update_row_err
    ' Variables and constants
    Dim check_category, check_subcategory, check_text, check_description, check_severity, check_status, check_link, check_training, check_graph_success, check_graph_failure, check_guid As String
    Dim user_input_comments As String, user_input_status As String
    Dim get_guid_user_input_successful As Boolean
    ' Defaults to English "Not Verified"
    If Len(notverified) = 0 Then notverified = "Not verified"
    ' Code
    check_category = get_object_property(json_item, "category")
    check_subcategory = get_object_property(json_item, "subcategory")
    check_text = get_object_property(json_item, "text")
    check_description = get_object_property(json_item, "description")
    check_severity = get_object_property(json_item, "severity")
    check_link = get_object_property(json_item, "link")
    check_training = get_object_property(json_item, "training")
    check_graph_success = get_object_property(json_item, "graph_success")
    check_graph_failure = get_object_property(json_item, "graph_failure")
    check_guid = get_object_property(json_item, "guid")
    Cells(row, category_column) = check_category
    Cells(row, subcategory_column) = check_subcategory
    Cells(row, text_column) = check_text
    Cells(row, description_column) = check_description
    Cells(row, severity_column) = check_severity
    Cells(row, guid_column) = check_guid
    'If the previous user input was saved, and we can successfully retrieve an entry for this guid, put it in the comments/status fields
    If user_input_saved Then
        If get_user_input_from_guid(check_guid, user_input_comments, user_input_status) Then
            Cells(row, status_column) = CStr(user_input_status)     'Some times around this line there is a dreadful 400 error :(
            Cells(row, comments_column) = CStr(user_input_comments)
        Else
            Cells(row, status_column) = notverified '"notverified" is a variable containing the translation of "not verified"
            Cells(row, comments_column) = ""
        End If
    'Otherwise, blank them
    Else
        Cells(row, status_column) = notverified '"notverified" is a variable containing the translation of "not verified"
        Cells(row, comments_column) = ""
    End If
    'Graph queries can optionally be imported or not, since it impacts readability
    'Per default, they are only imported when using the English language
    If import_graph_queries Then
        Cells(row, graph_success_column) = check_graph_success
        Cells(row, graph_failure_column) = check_graph_failure
    Else
        Cells(row, graph_success_column) = ""
        Cells(row, graph_failure_column) = ""
    End If
    'Training and MoreInfo link optional
    If Len(check_link) > 0 Then
        Cells(row, link_column).Hyperlinks.Add Address:=check_link, TextToDisplay:="More info", Anchor:=Cells(row, link_column), ScreenTip:=check_link
    Else
        Cells(row, link_column) = ""
    End If
    If Len(check_training) > 0 Then
        Cells(row, training_column).Hyperlinks.Add Address:=check_training, TextToDisplay:="Training", Anchor:=Cells(row, training_column), ScreenTip:=check_training
    Else
        Cells(row, training_column) = ""
    End If
    Exit Sub
update_row_err:
    If Err.Number <> 0 Then
        MsgBox "Error while updating row: " & Err.Description, vbCritical
    End If
End Sub

'Generates a random GUID
'https://danwagner.co/how-to-generate-a-guid-in-excel-with-vba/
Function generate_guid() As String
On Error GoTo genguiderr
    Dim k, h As Variant
    generate_guid = Space(36)
    For k = 1 To Len(generate_guid)
        Randomize
        Select Case k
            Case 9, 14, 19, 24: h = "-"
            Case 15:            h = "4"
            Case 20:            h = Hex(Rnd * 3 + 8)
            Case Else:          h = Hex(Rnd * 15)
        End Select
        Mid$(generate_guid, k, 1) = h
    Next
    generate_guid = LCase$(generate_guid)
genguiderr:
    If Err.Number <> 0 Then
        MsgBox "Error while generating GUID: " & Err.Description, vbCritical
    End If
End Function

'Import Azure Resource Graph query results from a JSON file generated with checklist_graph.sh
Sub import_graph_results()
On Error GoTo import_graph_results_err
    Dim json_file As Variant
    Dim objStream
    Dim json As String
    Dim json_object, json_item As Object
    Dim check_guid As String, check_success_result As String, check_failure_result As String, check_result As String, check_arm_id As String
    Dim row As Integer
    Dim query_result_format As String, query_result_date As String
    'File pick dialog
    ChDir ActiveWorkbook.Path
    json_file = Application.GetOpenFilename(Title:="Please choose a file to open", FileFilter:="JSON Files *.json* (*.json),")
    If json_file = False Then
        MsgBox "No file selected.", vbExclamation, "Action canceled"
        Exit Sub
    Else
        If MsgBox("This action will potentially overwrite existing contents in the Comments column. Do you want to continue?", vbQuestion + vbYesNo) = vbYes Then
            'Open and read text file
            Set objStream = CreateObject("ADODB.Stream")
            objStream.Charset = "utf-8"
            objStream.Open
            objStream.LoadFromFile (json_file)
            json = objStream.ReadText()
            objStream.Close
            Set objStream = Nothing
            'Remove line breaks and parse
            json = Replace(json, vbCrLf, "")
            Set json_object = JsonConverter.ParseJson(json)  'This line might give Run-time error 10001 if there are JSON syntax errors
            'Read metadata, which contains the format
            If json_object.Exists("metadata") Then
                query_result_format = get_object_property(json_object("metadata"), "format")
                query_result_date = get_object_property(json_object("metadata"), "date")
            Else
                MsgBox "No metadata found in file " & json_file & ", defaulting to short format", vbInformation
                query_result_format = "short"
                query_result_date = ""
            End If
            'Browse the checks one per one
            If json_object.Exists("checks") Then
                For Each json_item In json_object("checks")
                    If query_result_format = "short" Then
                        'Get the check info
                        check_guid = get_object_property(json_item, "guid")
                        check_success_result = get_object_property(json_item, "success")
                        check_failure_result = get_object_property(json_item, "failure")
                        'Now find the row with a matching GUID, and populate the comments field
                        row = row1
                        Do Until Cells(row, guid_column) = check_guid Or Cells(row, text_column) = ""
                            row = row + 1
                        Loop
                        'And update the comments column if it was found
                        If Cells(row, text_column) = "" Then
                           MsgBox "GUID " & check_guid & " not found in this checklist.", vbExclamation
                        Else
                            Cells(row, comments_column) = "Compliant resources: " + check_success_result + ". Non-compliant resources: " + check_failure_result
                        End If
                    ElseIf query_result_format = "long" Then
                        'Get the check info
                        check_guid = get_object_property(json_item, "guid")
                        check_result = get_object_property(json_item, "result")
                        check_arm_id = get_object_property(json_item, "id")
                        'Now find the row with a matching GUID, and populate the comments field
                        row = row1
                        Do Until Cells(row, guid_column) = check_guid Or Cells(row, text_column) = ""
                            row = row + 1
                        Loop
                        'And update the comments column if it was found
                        If Cells(row, text_column) = "" Then
                           MsgBox "GUID " & check_guid & " not found in this checklist.", vbExclamation
                        Else
                            'Enter a line break if the cell wasnt empty
                            If Len(Cells(row, comments_column)) > 0 Then Cells(row, comments_column) = Cells(row, comments_column) & Chr(10)
                            'Depending on the test result, add 'compliant' or 'non-compliant'
                            If check_result = "success" Then
                                Cells(row, comments_column) = Cells(row, comments_column) & "Compliant: " + check_arm_id
                            ElseIf check_result = "fail" Then
                                Cells(row, comments_column) = Cells(row, comments_column) & "Non-compliant: " + check_arm_id
                            Else
                                MsgBox "Check result " & check_result & " not understood", vbExclamation
                            End If
                        End If
                    Else
                        Debug.Print "Unknown query result format: " & query_result_format
                    End If
                Next json_item
            Else
                MsgBox "It looks like the JSON file " & json_file & " does not contain a 'checks' object?", vbCritical
            End If
        End If
    
    End If
    Exit Sub
import_graph_results_err:
    If Err.Number = 10001 Then
        MsgBox "Error while importing graph results: please verify that the file " & json_file & " has a valid JSON format", vbCritical
    ElseIf Err.Number <> 0 Then
        MsgBox "Error while importing graph results: " & CStr(Err.Number) & ": " & Err.Description, vbCritical
    End If
    Exit Sub
End Sub

' Functions to set global variables when option buttons are pushed
Sub set_japanese()
    selected_language = "ja"
    import_graph_queries = False
End Sub
Sub set_english()
    selected_language = "en"
    import_graph_queries = True
End Sub
Sub set_korean()
    selected_language = "ko"
    import_graph_queries = False
End Sub
Sub set_spanish()
    selected_language = "es"
    import_graph_queries = False
End Sub
Sub set_portuguese()
    selected_language = "pt"
    import_graph_queries = False
End Sub
Sub set_aks()
    selected_technology = "aks"
End Sub
Sub set_avd()
    selected_technology = "avd"
End Sub
Sub set_security()
    selected_technology = "security"
End Sub
Sub set_lz()
    selected_technology = "lz"
End Sub

'Delete all from controls, so that the spreadsheet can be saved as macro-free
Sub clear_rows()
    Dim row As Integer
    row = row1
    Do While row < row_limit And (Len(Cells(row, category_column)) + Len(Cells(row, subcategory_column)) + Len(Cells(row, text_column)) + Len(Cells(row, status_column)) + Len(Cells(row, comments_column))) > 0
        Cells(row, category_column) = ""
        Cells(row, subcategory_column) = ""
        Cells(row, text_column) = ""
        Cells(row, description_column) = ""
        Cells(row, severity_column) = ""
        Cells(row, link_column) = ""
        Cells(row, status_column) = ""
        Cells(row, comments_column) = ""
        Cells(row, training_column) = ""
        Cells(row, graph_success_column) = ""
        Cells(row, graph_failure_column) = ""
        Cells(row, guid_column) = ""
        row = row + 1
    Loop
    Cells(2, 1) = "Azure Review Checklist"
End Sub

'Clear all rows
Sub delete_controls()
    Dim item As Object
    'Browse all shapes
    For Each item In ActiveSheet.Shapes
        'Only Form Controls
        If item.Type = msoFormControl Then
            item.Delete
        End If
    Next item
End Sub

'Inspect option buttons and set global variables accordingly
Sub set_checklist_variables()
On Error GoTo set_checklist_variables_err
    
    'Look at the technology cell
    Select Case Cells(technology_selection_row, technology_selection_col)
        Case Sheets(values_sheet).Cells(2, values_technology_selection_column)
            selected_technology = "lz"
        Case Sheets(values_sheet).Cells(3, values_technology_selection_column)
            selected_technology = "aks"
        Case Sheets(values_sheet).Cells(4, values_technology_selection_column)
            selected_technology = "avd"
        Case Sheets(values_sheet).Cells(5, values_technology_selection_column)
            selected_technology = "security"
        Case Else
            MsgBox "Technology option " & Cells(technology_selection_row, technology_selection_col) & " unknown, defaulting to Landing Zone review", vbCritical
            selected_technology = "lz"
    End Select
    
    'Look at the language cell
    Select Case Cells(language_selection_row, language_selection_col)
        Case Sheets(values_sheet).Cells(2, values_language_selection_column)
            selected_language = "en"
            import_graph_queries = True
        Case Sheets(values_sheet).Cells(3, values_language_selection_column)
            selected_language = "ja"
            import_graph_queries = False
        Case Sheets(values_sheet).Cells(4, values_language_selection_column)
            selected_language = "ko"
            import_graph_queries = False
        Case Sheets(values_sheet).Cells(5, values_language_selection_column)
            selected_language = "pt"
            import_graph_queries = False
        Case Sheets(values_sheet).Cells(6, values_language_selection_column)
            selected_language = "es"
            import_graph_queries = False
        Case Else
            MsgBox "Language option " & Cells(language_selection_row, language_selection_col) & " unknown, defaulting to English", vbCritical
            selected_language = "en"
            import_graph_queries = True
    End Select
        
    'Debug.Print "Selected technology " + selected_technology + ", selected language " + selected_language
    Exit Sub
set_checklist_variables_err:
    MsgBox "Error while reading checklist selection options, defaulting to Landing Zone and English: " & CStr(Err.Number) & ": " & Err.Description, vbCritical
    selected_technology = "lz"
    selected_language = "en"
    import_graph_queries = True
End Sub

'Load in an object variable the existing values
Function get_user_input() As Boolean
On Error GoTo get_user_input_err
    Dim row, checks_counter As Integer
    row = row1
    ReDim user_checks(3, 1) As String
    Erase user_checks
    checks_counter = 0
    'Browse through all rows
    Do While row < row_limit And Len(Cells(row, category_column)) > 0
        'Only store a check if there is a non-blank comment or status is different than "Not Verified"
        If Len(Cells(row, comments_column)) > 0 Or Cells(row, status_column) <> Sheets(values_sheet).Cells(2, values_status_column) Then
            checks_counter = checks_counter + 1
            ReDim Preserve user_checks(3, checks_counter) As String
            user_checks(user_info_guid_index, checks_counter) = Cells(row, guid_column)
            user_checks(user_info_comments_index, checks_counter) = Cells(row, comments_column)
            user_checks(user_info_status_index, checks_counter) = Cells(row, status_column)
        End If
        row = row + 1
    Loop
    get_user_input = True
    Exit Function
get_user_input_err:
    If Err.Number <> 0 Then
        MsgBox "Error while reading existing comments: " & Err.Description, vbCritical
    End If
    get_user_input = False
    Exit Function
End Function

'Return the comments a status for a certain guid in an bidimensional array generated by get_user_input
Function get_user_input_from_guid(guid As String, ByRef comments As String, ByRef status As String) As Boolean
On Error GoTo get_user_input_from_guid_err
    Dim i As Integer
    comments = ""
    status = ""
    For i = 1 To UBound(user_checks(), 2)
        If LCase(user_checks(user_info_guid_index, i)) = LCase(guid) Then
            comments = user_checks(user_info_comments_index, i)
            status = user_checks(user_info_status_index, i)
            get_user_input_from_guid = True
            Exit Function
        End If
    Next i
    get_user_input_from_guid = False
    Exit Function
get_user_input_from_guid_err:
    If Err.Number = 9 Then      'Subscript out of range: silently exit
        get_user_input_from_guid = False
        Exit Function
    ElseIf Err.Number <> 0 Then
        Debug.Print "Error while retrieving comments/status for GUID " + guid + " - " & CStr(Err.Number) & ": " & Err.Description, vbCritical
    End If
    get_user_input_from_guid = False
    Exit Function
End Function


'Test sub
Sub test()
    Dim comments As String, status As String
    If get_user_input() Then
        'Debug.Print CStr(UBound(my_checks, 2) - LBound(my_checks, 2))
        If get_user_input_from_guid("a0f61565-9de5-458f-a372-49c831112dbd", comments, status) Then
            Debug.Print "Comments: " + comments + ". Status: " + status
        End If
    End If
End Sub
