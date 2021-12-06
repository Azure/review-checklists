#!/usr/bin/zsh

##################################################################################################
# This script downloads the latest JSON checklist in https://github.com/Azure/review-checklists
#    and performs the Azure Resource Graph queries defined in the tests.
# It will output a the test results (successful/failed) for each check in the list, that can be
#    then sent to a file or copy/pasted in a different tool (like the sample spreadsheet in this
#    repository).
# The script can take some arguments:
#    -b/--base-url: URL where to download the JSON file from. Defaults to https://raw.githubusercontent.com/Azure/review-checklists/main/samples/
#    -t/--technology: technology to verify. Accepted values lz, aks and avd. Defaults to aks
#    -c/--category: category to filter the tests. Accepted values: 0 to (number_of_categories-1)
#    -l/--list-categories: instead of running Azure Graph queries, it only displays the categories in the file and its corresponding indexes
#    -s/--show-text: shows the check text (good for troubleshooting, not so good to copy/paste to Excel)
#    -n/--no-empty: does not show checks without an associated query
#    -o/--output: can be either console or json
#    -f/--format: can be either short (syntax "<resourceGroup>/<name>") or long (syntax "<id>")
#    --file: custom JSON file (otherwise the latest checklist is downloaded from Github)
#    -mg/--management-group: per default the Azure Resource Graph queries are scoped to the current subscription, you can enlarge the scope to a given management group
#    -d/--debug: increase verbosity
#
# Example:
#       ./checklist_graph.sh -l -t=aks
#       ./checklist_graph.sh -c=0 -t=aks
#
# Jose Moreno, October 2021
###################################################################################################


# Defaults
base_url="https://raw.githubusercontent.com/Azure/review-checklists/main/checklists/"
technology="aks"
category_id=""
debug="no"
help="no"
error_file=/tmp/error.json
list_categories=no
check_text=no
no_empty=no
output=console
format=short
mg=""
filename=""

# Color format variables
normal="\e[0m"
underline="\e[4m"
red="\e[31m"
green="\e[32m"
yellow="\e[33m"
blue="\e[34m"
bold="\e[1m"

# Parse arguments
for i in "$@"
do
     case $i in
          -b=*|--base-url=*)
               base_url="${i#*=}"
               shift # past argument=value
               ;;
          -t=*|--technology=*)
               technology="${i#*=}"
               shift # past argument=value
               ;;
          -l*|--list-categories*)
               list_categories="yes"
               shift # past argument with no value
               ;;
          -c=*|--category=*)
               category_id="${i#*=}"
               shift # past argument=value
               ;;
          -f=*|--format=*)
               format="${i#*=}"
               shift # past argument=value
               ;;
          -s*|--show-text*)
               check_text="yes"
               shift # past argument with no value
               ;;
          -n*|--no-empty*)
               no_empty="yes"
               shift # past argument with no value
               ;;
          -o=*|--output=*)
               output="${i#*=}"
               shift # past argument=value
               ;;
          -mg=*|--management-group=*)
               mg="${i#*=}"
               shift # past argument=value
               ;;
          --file=*)
               filename="${i#*=}"
               shift # past argument=value
               ;;
          -d*|--debug*)
               debug="yes"
               shift # past argument with no value
               ;;
          --help|-h)
               help=yes
               shift # past argument with no value
               ;;
          *)
                    # unknown option
               ;;
     esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# Print help message
if [[ "$help" == "yes" ]]
then
    script_name="$0"
     echo "Please run this script as:
        $script_name [--technology=lz|aks|avd] [--category=<category_id>] [--management-group=<mgmt_group>] [--base-url=<base_url>] [--show-text] [--no-empty] [--debug]
        $script_name [--file=<path_to_json_file>] [--category=<category_id>] [--management-group=<mgmt_group>] [--base-url=<base_url>] [--show-text] [--no-empty] [--debug]
        $script_name [--list-categories] [--base-url=<base_url>] [--technology=lz|aks|avd] [--debug]"
    exit
fi

# If outputing to JSON, we dont want output that breaks the JSON syntax
if [[ "$output" == "json" ]]; then
    check_text=no
    no_empty=yes
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Output is $output, setting --check-text=${check_text} and --no-empty=${no_empty}..."; fi
fi

# If a Management Group was specified, use it in the az graph command
if [[ -z "$mg" ]]; then
    mg_option=""
else
    mg_option="-m $mg"
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Setting management group $mg as scope for the az graph query commands..."; fi
fi

# Download checklist from Github or upload from file
if [[ -n "$filename" ]]
then
    if [[ -e "$filename" ]]
    then
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Getting JSON content from filename $filename..."; fi
        checklist_json=$(cat "$filename")
    else
        echo "ERROR: File $filename could not be found"
        exit
    fi
else
    # Set URL and download checklist from base URL
    checklist_url="${base_url}${technology}_checklist.en.json"
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Getting checklist from $checklist_url..."; fi
    checklist_json=$(curl -s "$checklist_url")
fi

# If in list_categories mode, just get the categories part:
if [[ "$list_categories" == "yes" ]]
then
    i=0
    category_list=$(echo $checklist_json | jq -r '.categories[].name')
    while IFS= read -r category; do
        echo "${i}: - $category"
        i=$(($i+1))
    done <<< "$category_list"
    exit 0
fi

# If there is a category specified, get the name
if [[ -n "$category_id" ]]
then
    category_name=$(echo $checklist_json | jq -r '.categories['$category_id'].name')
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Performing tests for category $category_name..."; fi
else
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Performing tests for all categories..."; fi
fi

# Get a list of the items
if [[ "$debug" == "yes" ]]; then echo "DEBUG: Extracting information from JSON..."; fi
if [[ -n "$category_name" ]]
then
    graph_success_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .graph_success')
    graph_failure_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .graph_failure')
    category_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .category')
    text_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .text')
    guid_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .guid')
    if [[ -z "$text_list" ]]; then
        echo "ERROR: error processing JSON file, please verify the syntax"
        exit
    fi
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $text_list | wc -l) tests found in the checklist for category ${category_name}."; fi
else
    graph_success_list=$(print -r "$checklist_json" | jq -r '.items[] | .graph_success')
    graph_failure_list=$(print -r "$checklist_json" | jq -r '.items[] | .graph_failure')
    category_list=$(print -r "$checklist_json" | jq -r '.items[] | .category')
    text_list=$(print -r "$checklist_json" | jq -r '.items[] | .text')
    guid_list=$(print -r "$checklist_json" | jq -r '.items[] | .guid')
    if [[ -z "$text_list" ]]; then
        echo "ERROR: error processing JSON file, please verify the syntax"
        exit
    fi
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $text_list | wc -l) tests found in the checklist."; fi
fi

# Debug
if [[ "$debug" == "yes" ]]; then 
    echo "DEBUG: $(echo $graph_success_list | wc -l) graph queries for success tests found in the checklist."
    # echo "$graph_success_list"
fi
if [[ "$debug" == "yes" ]]; then 
    echo "DEBUG: $(echo $graph_failure_list | wc -l) graph queries for failure tests found in the checklist."
    # echo "$graph_failure_list"
fi
if [[ "$debug" == "yes" ]]; then 
    echo "DEBUG: $(echo $guid_list | wc -l) GUIDs with a defined Graph query found in the checklist"
    # echo "$guid_list"
fi

# Make sure the Azure CLI extension for Azure Resource Graph is installed and updated
extension_name=resource-graph
extension_version=$(az extension show -n $extension_name --query version -o tsv 2>/dev/null)
if [[ -z "$extension_version" ]]
then
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Azure CLI extension $extension_name not found, installing now..."; fi
    az extension add -n $extension_name -o none 2>/dev/null
else
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Azure CLI extension $extension_name found with version $extension_version, trying to upgrade..."; fi
    az extension update -n $extension_name -o none 2>/dev/null
fi
extension_version=$(az extension show -n $extension_name --query version -o tsv 2>/dev/null)
if [[ "$debug" == "yes" ]]; then echo "Azure CLI extension $extension_name running with version $extension_version"; fi

# Run queries
i=0
this_category_name=""
json_output="{ \"metadata\": {\"format\": \"${format}\", \"timestamp\": \"$(date)\"}, \"checks\": ["
json_output_empty="yes"
while IFS= read -r graph_success_query; do
    i=$(($i+1))
    this_guid=$(echo $guid_list | head -$i | tail -1)
    if [[ "$debug" == "yes" ]]; then echo "Processing check item $i, GUID '$this_guid'..."; fi
    if [[ "$this_guid" == "null" ]] && [[ "$output" == "json" ]]; then
        if [[ "$debug" == "yes" ]]; then echo "ERROR: GUID not defined for check number $i"; fi
    fi
    # Print header category if required
    if [[ "$this_category_name" != "$(echo $category_list | head -$i | tail -1)" ]]
    then
        this_category_name=$(echo $category_list | head -$i | tail -1)
        if [[ "$output" == "console" ]]; then
            echo "${bold}${blue}CHECKLIST CATEGORY: ${this_category_name}${normal}"
        fi
    fi
    # Check if there is any query
    if [[ "$graph_success_query" == "null" ]]; then
        if [[ "$no_empty" != "yes" ]]; then
            # Print title if required
            if [[ "$check_text" == "yes" ]]; then
                this_text=$(echo $text_list | head -$i | tail -1)
                echo "CHECKLIST ITEM: ${this_text}:"
            fi
            # Print output
            echo "N/A"
        fi
    else
        # Print title if required
        if [[ "$check_text" == "yes" ]] && [[ "$output" == "console" ]]; then
            this_text=$(echo $text_list | head -$i | tail -1)
            echo "CHECKLIST ITEM: ${this_text}:"
        fi
        rm $error_file 2>/dev/null; touch $error_file
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Running success query '$graph_success_query'..."; fi
        # If format is short, the graph query command returns a single line, if format is long, it is one line per resource
        if [[ "$format" == "short" ]]; then
            success_result=$(az graph query -q "$graph_success_query" ${(z)mg_option} -o json 2>$error_file | jq -r '.data[] | "\(.resourceGroup)/\(.name)"' 2>>$error_file | tr '\n' ',')
            if [[ -s $error_file ]]; then
                success_result="Error";
                if [[ "$debug" == "yes" ]]; then cat $error_file; fi
            else
                # Remove last comma
                success_result=${success_result%?}
            fi
            # If no object was returned
            if [[ -z "$success_result" ]]; then success_result='None'; fi
        else
            success_result=$(az graph query -q "$graph_success_query" ${(z)mg_option} -o tsv 2>$error_file --query 'data[].id' | sort -u)
        fi
        rm $error_file 2>/dev/null; touch $error_file
        graph_failure_query=$(print -r "$graph_failure_list" | head -$i | tail -1)
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Running failure query '$graph_failure_query'..."; fi
        # If format is short, the graph query command returns a single line, if format is long, it is one line per resource
        if [[ "$format" == "short" ]]; then
            # NOTE: this line will give some unexpected results when running Graph queries that return subscription IDs, since those do not have a RG
            failure_result=$(az graph query -q "$graph_failure_query" ${(z)mg_option} -o json 2>$error_file | jq -r '.data[] | "\(.resourceGroup)/\(.name)"' 2>>$error_file | tr '\n' ',')
            if [[ -s $error_file ]]; then
                failure_result="Error"
                if [[ "$debug" == "yes" ]]; then cat $error_file; fi
            else
                # Remove last comma
                failure_result=${failure_result%?}
            fi
            # If no object was returned
            if [[ -z "$failure_result" ]]; then failure_result='None'; fi
        else
            # If format is long, the result should be a list of IDs
            failure_result=$(az graph query -q "$graph_failure_query" ${(z)mg_option} -o tsv 2>$error_file --query 'data[].id' | sort -u)
        fi
        # Print output in color format
        if [[ "$output" == "console" ]] && [[ "$format" == "short" ]]; then
            if [[ "$success_result" == "None" ]]; then
                success_color=$yellow
            else
                success_color=$green;
            fi
            if [[ "$failure_result" == "None" ]]; then
                failure_color=$green
            else
                failure_color=$red;
            fi
            echo "Success: ${success_color}${success_result}${normal}. Fail: ${failure_color}${failure_result}${normal}"
        fi
        # Append JSON element, depending on the chosen format short/long
        if [[ "$format" == "short" ]]; then
            # First, add a comma if this wasnt the first element
            if [[ "$json_output_empty" == "yes" ]]; then
                json_output_empty="no"
            else
                json_output+=", "
            fi
            json_output+="{\"guid\": \"$this_guid\", \"success\": \"$success_result\", \"failure\": \"$failure_result\"}"
        else
            # If long format, we append a line for each found compliant/non-compliant resource
            while IFS= read -r resource_id
            do
                if [[ -n "$resource_id" ]]; then
                    # First, add a comma if this wasnt the first element
                    if [[ "$json_output_empty" == "yes" ]]; then
                        json_output_empty="no"
                    else
                        json_output+=", "
                    fi
                    # Add an item per compliant resource
                    json_output+="{\"guid\": \"$this_guid\", \"result\": \"success\", \"id\": \"$resource_id\"}"
                fi
            done < <(printf '%s\n' "$success_result")
            while IFS= read -r resource_id
            do
                if [[ -n "$resource_id" ]]; then
                    # First, add a comma if this wasnt the first element
                    if [[ "$json_output_empty" == "yes" ]]; then
                        json_output_empty="no"
                    else
                        json_output+=", "
                    fi
                    # Add an item per non-compliant resource
                    json_output+="{\"guid\": \"$this_guid\", \"result\": \"fail\", \"id\": \"$resource_id\"}"
                fi
            done < <(printf '%s\n' "$failure_result")
        fi
    fi
done <<< "$graph_success_list"

# Close JSON format
json_output+="]}"

# If output is JSON, print check_results variable
if [[ "$output" == "json" ]]; then
    echo "$json_output"
fi