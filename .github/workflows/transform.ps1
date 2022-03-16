
# take in list of files that need to be transformed
$files = $args[0].trim().split(" ")

Foreach ($file in $files) {
    write-host "processing: $file"
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

