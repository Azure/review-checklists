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
#    -f/--format: can be either text or json (defaults to json)
#    --file: custom JSON file (otherwise the latest checklist is downloaded from Github)
#    -mg/--management-group: per default the Azure Resource Graph queries are scoped to the current subscription, you can enlarge the scope to a given management group
#    -d/--debug: increase verbosity
#
# Example:
#       ./checklist_graph.sh --list-technologies
#       ./checklist_graph.sh --technology=aks --list-categories
#       ./checklist_graph.sh --technology=aks --category=0 --format=text
#       ./checklist_graph.sh --technology=aks --format=json >graph_results.json
#
# Jose Moreno, October 2021
###################################################################################################


# Defaults
base_url="https://raw.githubusercontent.com/Azure/review-checklists/main/"
technology="aks"
category_id=""
debug="no"
help="no"
error_file=/tmp/error.json
list_categories=no
check_text=no
format=json
mg=""
filename=""
no_empty=yes

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
          -t*|--list-technologies*)
               list_technologies="yes"
               shift # past argument with no value
               ;;
          -c=*|--category=*)
               category_id="${i#*=}"
               shift # past argument=value
               ;;
          -g=*|--guid=*)
               check_guid="${i#*=}"
               shift # past argument=value
               ;;
          -f=*|--format=*)
               format="${i#*=}"
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
        $script_name [--list-technologies] [--base-url=<base_url>] [--debug]
        $script_name [--list-categories] [--base-url=<base_url>] [--technology=<technology>] [--debug]
        $script_name [--technology=<technology>] [--category=<category_id>] [--format=json|text] [--management-group=<mgmt_group>] [--base-url=<base_url>] [--debug]
        $script_name [--technology=<technology>] [--category=<category_id>] [--file=<json_file_path>] [--format=json|text] [--management-group=<mgmt_group>] [--base-url=<base_url>] [--debug]"
    exit
fi

# If outputing to JSON, we dont want output that breaks the JSON syntax
if [[ "$format" == "json" ]]; then
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

# If in "list_technologies" mode, just get the categories part:
if [[ "$list_technologies" == "yes" ]]
then
    # Get list of checklists
    git_tree_id=$(curl -s https://api.github.com/repos/Azure/review-checklists/commits | jq -r '.[0].commit.tree.sha')
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Git tree ID is $git_tree_id"; fi
    checklist_list=$(curl -s "https://api.github.com/repos/Azure/review-checklists/git/trees/${git_tree_id}?recursive=true" | jq -r '.tree[].path' | grep en.json | sed -e 's/_checklist.en.json//')
    while IFS= read -r checklist; do
        checklist_url="${base_url}checklists/${checklist}_checklist.en.json"
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Processing JSON content from URL $checklist_url..."; fi
        graph_query_no=$(curl -s "$checklist_url" | jq -r '.items[].graph' | grep -v -e '^null$' | wc -l)
        echo "$checklist ($graph_query_no graph queries)"
    done <<< "$checklist_list"
    exit 0
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
    checklist_url="${base_url}checklists/${technology}_checklist.en.json"
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Getting checklist from $checklist_url..."; fi
    checklist_json=$(curl -s "$checklist_url")
fi

# If in "list_categories" mode, just get the categories part:
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
    graph_query_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .graph')
    category_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .category')
    text_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .text')
    guid_list=$(print -r "$checklist_json" | jq -r '.items[] | select(.category=="'$category_name'") | .guid')
    if [[ -z "$text_list" ]]; then
        echo "ERROR: error processing JSON file, please verify the syntax"
        exit
    fi
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $text_list | wc -l) tests found in the checklist for category ${category_name}."; fi
else
    graph_query_list=$(print -r "$checklist_json" | jq -r '.items[] | .graph')
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
    echo "DEBUG: $(echo $graph_query_list | wc -l) graph queries found in the checklist."
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
if [[ "$debug" == "yes" ]]; then echo "DEBUG: Azure CLI extension $extension_name running with version $extension_version"; fi

# Run queries
i=0
query_no=0
this_category_name=""
json_output="{ \"metadata\": {\"format\": \"${format}\", \"timestamp\": \"$(date)\"}, \"checks\": ["
json_output_empty="yes"
while IFS= read -r graph_query; do
    i=$(($i+1))
    this_guid=$(echo $guid_list | head -$i | tail -1)
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Processing check item $i, GUID '$this_guid'..."; fi
    if [[ "$this_guid" == "null" ]] && [[ "$output" == "json" ]]; then
        if [[ "$debug" == "yes" ]]; then echo "ERROR: GUID not defined for check number $i"; fi
    fi
    # If a GUID was specified, check if it matches the current one
    if [[ -z "$check_guid" ]] || [[ $check_guid == $this_guid ]]; then
        # Check if there is any query
        if [[ "$graph_query" == "null" ]]; then
            if [[ "$no_empty" != "yes" ]]; then
                # Print title if required
                if [[ "$check_text" == "yes" ]]; then
                    this_text=$(echo $text_list | head -$i | tail -1)
                    echo "${blue}CHECKLIST ITEM: ${this_text} (${this_guid}):${normal} "
                fi
                # Print output
                echo "N/A"
            fi
        else
            # Increase counter
            query_no=$(($query_no+1))
            # Print title if text format
            if [[ "$format" == "text" ]]; then
                this_text=$(echo $text_list | head -$i | tail -1)
                echo "${blue}CHECKLIST ITEM: ${this_text} (${this_guid}):${normal}"
            fi
            rm $error_file 2>/dev/null; touch $error_file
            if [[ "$debug" == "yes" ]]; then echo "DEBUG: Running query \"$graph_query\"..."; fi
            # The query should return one line per result. Fields ID and Compliant and mandatory
            query_result=$(az graph query -q "$graph_query" ${(z)mg_option} -o tsv 2>$error_file --query 'data[].[id,compliant]' | sort -u)
            rm $error_file 2>/dev/null; touch $error_file
            while IFS= read -r result
            do
                if [[ -n "$result" ]]; then
                    # Extract the tab-separated fields (ID and compliant)
                    resource_id=$(echo $result | cut -f 1)
                    result_id_temp=$(echo $result | cut -f 2)
                    result_id=${result_id_temp:0:1}
                    # Print output in color if format is text
                    if [[ "$format" == "text" ]]; then
                        if [[ "$result_id" == "1" ]]; then
                            result_text="compliant"
                            color=$green
                        elif [[ "$result_id" == "0" ]]; then
                            result_text="non-compliant"
                            color=$red;
                        else
                            if [[ "$debug" == "yes" ]]; then echo "WARNING: unknown result code returned: $result_id..."; fi
                            result_text="undefined"
                            color=$blue;
                        fi
                        echo "${resource_id}: ${color}${result_text}${normal} "
                    # With JSON format, we append a line for each found compliant/non-compliant resource
                    elif [[ "$format" == "json" ]]; then
                        if [[ "$result_id" == "1" ]]; then
                            result_bool=true
                        elif [[ "$result_id" == "0" ]]; then
                            result_bool=false
                        else
                            if [[ "$debug" == "yes" ]]; then echo "WARNING: unknown result code returned \"$result_id\""; fi
                            result_bool=undefined
                        fi
                        if [[ -n "$resource_id" ]]; then
                            # First, add a comma if this wasnt the first element
                            if [[ "$json_output_empty" == "yes" ]]; then
                                json_output_empty="no"
                            else
                                json_output+=", "
                            fi
                            # Add an item per compliant resource
                            json_output+="{\"guid\": \"$this_guid\", \"compliant\": \"$result_bool\", \"id\": \"$resource_id\"}"
                        fi
                    else
                        echo "ERROR: format $format not recognized, only 'json' or 'text' are accepted formats"
                    fi
                else
                    if [[ "$debug" == "yes" ]]; then echo "WARNING: Graph query returned an empty result"; fi
                fi
            done < <(printf '%s\n' "$query_result")
        fi
    fi
done <<< "$graph_query_list"

if (( $query_no == 0 )); then
    echo "ERROR: The checklist for the selected technology does not contain any graph query"
fi

# Close JSON format
json_output+=" ] }"

# If output is JSON, print check_results variable
if [[ "$format" == "json" ]]; then
    echo "$json_output"
fi
