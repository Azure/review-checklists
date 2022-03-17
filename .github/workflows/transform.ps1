
# take in list of files that need to be transformed

if ($args -ne $null) {
    Write-Host "Parameter passed: $($args.ToString())"
    $files = $args[0].trim().split(" ")
} else {
    Write-Host "No parameters passed!"
    $files = $null
}

# If no argument is passed or the first file is a blank, get a list of all JSON files
if (($files -eq $null) -or ($files[0] -eq "")) {
    Write-Host "Trying to find out JSON files..."
    Write-Host "Working directory is $((Get-Location | Select-Object -ExpandProperty Path))..."
    $files = Get-ChildItem -Path './checklists/' -Filter '*.json' -Recurse | Select-Object -ExpandProperty FullName
    #Write-Host "No arguments provided, working with $($files.ToString())"
}

Write-Host "Starting processing $($files.length) files now..."

Foreach ($file in $files) {
    
    # Debug
    Write-Host "Looking at $file now..."

    # in some cases the script is executing when it should not, catch this by testing the file exists before proceeding
    if (-not(Test-Path $file)) {
        Write-Host "File $file does not exist"
        continue
    }

    # do not run in an .en.json file
    $file_extensions = $file.substring($file.length - 8, 8)
    if ($file_extensions -eq ".en.json") {
        Write-Host "Skipping $file since it is an English-based checklist"
        continue
    }

    write-host "Processing file $file"
    $json = Get-Content -Raw $file | ConvertFrom-Json
    
    # initialize the output file structure
    $output = @{
        items = @()
        categories = @()
        status = @()
        severities = @()
        metadata = @()
    }

    # convert the items dictionary to an array
    $i = 0
    do {
        $output.items += $json.items.$i
        $i++
    } while ($json.items.$i -ne $null)

    # convert the categories dictionary to an array
    $i = 0
    do {
        $output.categories += $json.categories.$i
        $i++
    } while ($json.categories.$i -ne $null)
    

    # convert the status dictionary to an array
    $i = 0
    do {
        $output.status += $json.status.$i
        $i++
    } while ($json.status.$i -ne $null)
    
    # convert the severities dictionary to an array
    $i = 0
    do {
        $output.severities += $json.severities.$i
        $i++
    } while ($json.severities.$i -ne $null)

    # clone the metadata object to the output (does not need to convert)
    $output.metadata = $json.metadata
    
    # overwrite the original file with the new json
    $output | ConvertTo-JSON | Out-File ($file) -Encoding UTF8
 
}

