# Azure Review Checklists

When doing Azure design reviews (or any review for that matter), Excel spreadsheets are often the medium of choice. A problem with spreadsheets is that they are not easily made subject to revision control. Additionally, team collaboration with branching, issues, pull requests, reviews and others is difficult at best, impossible in most cases.

This repo will showcase the idea of having a JSON version of the checklist that can be imported into an Excel spreadsheet by means of Visual Basic for Applications (VBA) macros. The JSON can be subject to version control, and modified as technology or standards evolve.

The provided sample spreadsheet leverages code to interpret JSON from the VBA module in [https://github.com/VBA-tools/VBA-JSON/](https://github.com/VBA-tools/VBA-JSON/), from which I put a copy in this repo to be self-contained (make sure you use the latest version though).

Additionally, a Github action in this repository translates after every commit the English version of the checklist to additional languages (Japanese in the first release), using the cognitive service [Azure Translator](https://azure.microsoft.com/services/cognitive-services/translator/).

The sample spreadsheet in this repo includes some macros (find the source code both in the spreadsheet as well as [here](./code/Sheet1.cls)), which are accessible from buttons in the main sheet:

![](./pictures/spreadsheet_screenshot.png)

- **"Easy"** section (circled in red in the snapshot above): most frequently used, to import the latest set of checks from a git repo (whose URL is hard-coded in the spreadsheet). The user can select the checklist (today Landing Zone and AKS review checklists are supported) as well as the language
- **"Advanced"** section (circlued in blue in the snapshot above): it allows exporting/importing to specific files, that the user needs to provide:
    - `Import latest reference`:  `Export checklist to JSON`: it will export the checks as a JSON file (you can find two examples in [lz_checklist.json](./samples/lz_checklist.json) and [aks_checklist.json](./samples/aks_checklist.json))
    - `Import checklist from JSON`: it will import a JSON checklist stored in the local file system

Now you can source-control the JSON file with the checklist items. Changes to the JSON file with the check content can be tracked with issues and PRs, and the checklist set can be then imported in any tool, such as the provided sample spreadsheet.

Another potential benefit of separating the delivery tool from the actual content is the same engine (in this example the same spreadsheet) can be used for different checklists. In this repo you find two checklists as example that can be loaded in the sample spreadsheet: one for reviewing generic Azure Landing Zones ([./samples/lz_checklist.json](lz_checklist.json)), and a second one for verifying Azure Kubernetes Service environments ([aks_checklist.json](./samples/aks_checklist.json)). The check categories are also stored in the JSON export.
