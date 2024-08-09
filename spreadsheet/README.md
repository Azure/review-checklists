
## Using the spreadsheet for Azure reviews

1. Download the Excel spreadsheet from the [latest release](https://github.com/Azure/review-checklists/releases/latest/download/review_checklist.xlsm) to your PC

2. Use the dropdown lists to select the technology and language you would like to do your review

![](./pictures/spreadsheet_screenshot.png)

3. Click the control button "Import latest checklist". After you accept the verification message, the spreadsheet will load the latest version of the selected technology and language

4. (Optional) If you are going to distribute the spreadsheet to users who cannot work with macros (for example, either because of security reasons or because they use Office for Mac), save a version of the spreadsheet in xlsx format (instead of xlsm). Note that disabling macros will result in the spreadsheet losing its ability to import updated versions of the checklist or JSON-based Azure Resource Graph query results

5. Go row by row, set the "Status" field to one of the available options, and write any remarks in the "Comments" field (such as why a recommendation is not relevant, or who will fix the open item)

   1. Since there are many rows in a review, it is recommended to proceed in chunks: either going area after area (first "Networking", then "Security", etc) or starting with the "High" priority elements and afterward moving down to "Medium" and "Low"
   1. If any recommendation is not clear, there is a "More Info" link with more context information.
   1. **IMPORTANT**: design decisions are not a checkbox exercise, but a series of compromises. It is OK to deviate from certain recommendations if the implications are clear (for example, sacrificing security with operational simplicity or lower cost for non-critical applications)

6. Check the "Dashboard" worksheet for a graphical representation of the review progress

![](./pictures/spreadsheet_screenshot_dashboard.png)

## Security settings running macros

There are some settings that you might need to change in your system to run macro-enabled Excel spreadsheets. When initially opening the file you may see the following error, which prevents Excel from loading:

> Excel cannot open the file 'review_checklist.xlsm' because the file format or file extension is not valid. Verify that the file has not been corrupted and that the file extension matches the format of the file.

In other cases, the file opens with the following message, which prevents you from being able to load the checklist items:

![macro warning in excel](./pictures/macro_warning.png)

### Unblock the file or add an exception to Windows Security

1. You might need to unblock the file from the file properties in the Windows File Explorer so that you can use the macros required to import the checklist content from github.com:

![how to unblock a file to run macros](./pictures/unblock.png)

2. Additionally, you might want to add the macro-enabled spreadsheet file to the list of exceptions in Windows Security (in the Virus & Threat Protection section):

![how to add an exception to windows security 1](./pictures/defender_settings_1.png)
![how to add an exception to windows security 2](./pictures/defender_settings_2.png)
![how to add an exception to windows security 3](./pictures/defender_settings_3.png)
![how to add an exception to windows security 4](./pictures/defender_settings_4.png)

## Using the spreadsheet to generate JSON checklist files (advanced)

If you wish to do contributions to the checklists, one option is the following:

1. Load up the latest version of the checklist you want to modify
2. Do the required modifications to the checklist items
3. Push the button "Export checklist to JSON" in the **"Advanced"** section of controls in the checklist. Store your file in your local file system, and upload it to the [checklists folder](./checklists) of this Github repo (use the format `<technology>_checklist.en.json`, for example, `lz_checklist.en.json`)
4. This will create a PR and will be reviewed by the corresponding approvers.
