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

Const line_break = vbCrLf
Const category_column = 1
Const subcategory_column = 2
Const text_column = 3
Const severity_column = 4
Const status_column = 5
Const comments_column = 6
Const link_column = 7
Const training_column = 8
Const checklist_name_row = 2
Const checklist_name_col = 1
Const values_sheet = "values"
Const values_sev_column = 1
Const values_category_column = 3

Dim selected_language As String
Dim selected_technology As String

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
    'Avoid empty fields, the Azure translate API doesnt work well with then
    If input_text = "" Then input_text = "&nbsp"
    correct_format_for_JSON = input_text
End Function

'Exports current checklist from excel to a json-formated text file
Sub export_json()
    On Error GoTo errh
    ' Constants
    Const row1 = 5
    Const row_limit = 2000   'Safety net
    Const export_file_name = "checklist.json"
    Const values_sheet = "values"
    Const values_category_column = 3
    ' Variables
    Dim row As Integer
    Dim json As String
    Dim check_category, check_subcategory, check_text, check_severity, check_status, check_link, check_training As String
    Dim category_name, severity_name As String
    Dim export_file_path As Variant
    Dim double_quote As String
    Dim item_count, category_count As Integer
    ' Initialization
    double_quote = Chr(34) ' double quote as a variable
    row = row1
    json = "{" + line_break
    json = json + "  " + double_quote + "items" + double_quote + ": ["
    item_count = 0
    category_count = 0
    ' Loop through all rows as long as there is content
    Do While row < row_limit And Len(Cells(row, category_column)) > 0
        If row > row1 Then json = json + ","
        json = json + line_break
        check_category = Cells(row, category_column)
        check_subcategory = Cells(row, subcategory_column)
        check_text = Cells(row, text_column)
        check_severity = Cells(row, severity_column)
        If Cells(row, link_column).Hyperlinks.Count > 0 Then
            check_link = Cells(row, link_column).Hyperlinks(1).Address
        Else
            check_link = Cells(row, link_column)
        End If
        If Cells(row, training_column).Hyperlinks.Count > 0 Then
            check_training = Cells(row, training_column).Hyperlinks(1).Address
        Else
            check_training = Cells(row, training_column)
        End If
        row = row + 1
        json = json + "    {" + line_break
        json = json + "      " + double_quote + "category" + double_quote + ": " + double_quote + correct_format_for_JSON(check_category) + double_quote + "," + line_break
        json = json + "      " + double_quote + "subcategory" + double_quote + ": " + double_quote + correct_format_for_JSON(check_subcategory) + double_quote + "," + line_break
        json = json + "      " + double_quote + "text" + double_quote + ": " + double_quote + correct_format_for_JSON(check_text) + double_quote + "," + line_break
        json = json + "      " + double_quote + "severity" + double_quote + ": " + double_quote + check_severity + double_quote + "," + line_break
        json = json + "      " + double_quote + "training" + double_quote + ": " + double_quote + correct_format_for_JSON(check_training) + double_quote + "," + line_break
        json = json + "      " + double_quote + "link" + double_quote + ": " + double_quote + correct_format_for_JSON(check_link) + double_quote + line_break
        json = json + "    }"
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
        'Append the technology and options variables
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
        MsgBox "No file selected.", vbExclamation, "Sorry!"
        Exit Sub
    Else
        import_checklist_fromfile json_file
    End If
End Sub


'Import from a local JSON file
'Parse JSON code using the JsonConverter module
Sub import_checklist_fromfile(json_file As Variant)
    On Error GoTo errh
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
    Dim row, item_count, category_count, i As Integer
    'Initialization
    row = row1
    double_quote = Chr(34) ' double quote as a variable
    json = ""
    item_count = 0
    category_count = 0
    'Go through the file line by line
    
    ' Read .json file with FSO.OpenTextFile
    'Set json_ts = FSO.OpenTextFile(json_file, ForReading)
    'json = json_ts.ReadAll
    'json_ts.Close
    'Read .json file as object stream
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
    'Import checklist items
    row = row1
    'If JSON is a translated file, it is a nested dictionary with keys "0", "1", etc
    If TypeName(json_object("items")) = "Dictionary" Then
        i = 0
        Do
            update_row json_object("items")(CStr(i)), row
            row = row + 1
            item_count = item_count + 1
            i = i + 1
        Loop While json_object("items").Exists(CStr(i))
    'Otherwise, it is just an array
    Else
        For Each json_item In json_object("items")
            update_row json_item, row
            row = row + 1
            item_count = item_count + 1
        Next json_item
    End If
    'Blank the rest of the item rows
    Do While row < row_limit And (Len(Cells(row, category_column)) + Len(Cells(row, subcategory_column)) + Len(Cells(row, text_column)) + Len(Cells(row, status_column)) + Len(Cells(row, comments_column))) > 0
        Cells(row, category_column) = ""
        Cells(row, subcategory_column) = ""
        Cells(row, text_column) = ""
        Cells(row, severity_column) = ""
        Cells(row, link_column) = ""
        Cells(row, status_column) = ""
        Cells(row, comments_column) = ""
        Cells(row, training_column) = ""
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
errh:
    If Err.Number <> 0 Then
        MsgBox "Error while importing checklist from JSON " & Err.Description, vbCritical
    End If
End Sub

'Function with error control in case a property does not exist for an object
Function get_object_property(ByVal object_item As Object, property_name As String) As String
    On Error GoTo fncerrh
    Dim aux As String
    aux = object_item(property_name)
    'If it is "&nbsp" or something similar (some translation engines introduce blanks between "&" and "nbsp"), set to null
    If Right(aux, 4) = "nbsp" Then aux = ""
    get_object_property = aux
    Exit Function
fncerrh:
    get_object_property = ""
    Exit Function
End Function

' Updates a checklist row with the information in the object
Sub update_row(ByVal json_item As Object, ByVal row As Integer)
    ' Variables and constants
    Dim check_category, check_subcategory, check_text, check_severity, check_status, check_link, check_training As String
    ' Code
    check_category = get_object_property(json_item, "category")
    check_subcategory = get_object_property(json_item, "subcategory")
    check_text = get_object_property(json_item, "text")
    check_severity = get_object_property(json_item, "severity")
    check_link = get_object_property(json_item, "link")
    check_training = get_object_property(json_item, "training")
    Cells(row, category_column) = check_category
    Cells(row, subcategory_column) = check_subcategory
    Cells(row, text_column) = check_text
    Cells(row, severity_column) = check_severity
    Cells(row, status_column) = "Not verified"
    Cells(row, comments_column) = ""
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
End Sub

' Functions to set global variables when option buttons are pushed
Sub set_japanese()
    selected_language = "ja"
End Sub
Sub set_english()
    selected_language = "en"
End Sub
Sub set_korean()
    selected_language = "ko"
End Sub
Sub set_aks()
    selected_technology = "aks"
End Sub
Sub set_avd()
    selected_technology = "avd"
End Sub
Sub set_lz()
    selected_technology = "lz"
End Sub
