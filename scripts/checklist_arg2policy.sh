#!/usr/bin/zsh

#######################
# WORK IN PROGRESS !! #
#######################

##################################################################################################
# This script downloads the latest JSON checklist in https://github.com/Azure/review-checklists
#    and converts the ARG queries into policies.
# The script can take some arguments:
#    -b/--base-url: URL where to download the JSON file from. Defaults to https://raw.githubusercontent.com/Azure/review-checklists/main/samples/
#    -t/--technology: technology to verify. Accepted values lz, aks and avd. Defaults to aks
#    -c/--category: category to filter the tests. Accepted values: 0 to (number_of_categories-1)
#    -l/--list-categories: instead of running Azure Graph queries, it only displays the categories in the file and its corresponding indexes
#    -mg/--management-group: per default the Azure Policy assignments are scoped to the current subscription, you can enlarge the scope to a given management group
#    -d/--debug: increase verbosity
#
# Example:
#       ./checklist_arg2policy.sh --list-technologies
#       ./checklist_arg2policy.sh --technology=aks --list-categories
#       ./checklist_arg2policy.sh --technology=aks --category=0 --format=text
#       ./checklist_arg2policy.sh --technology=aks --format=json >graph_results.json
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
if [[ "$help" == "yes" ]] || [[ "$#" -eq 0 ]]
then
    script_name="$0"
     echo "Please run this script as:
        $script_name [--list-technologies] [--base-url=<base_url>] [--debug]
        $script_name [--list-categories] [--base-url=<base_url>] [--technology=<technology>] [--debug]
        $script_name [--technology=<technology>] [--category=<category_id>] [--format=json|text] [--management-group=<mgmt_group>] [--base-url=<base_url>] [--debug]
        $script_name [--technology=<technology>] [--category=<category_id>] [--file=<json_file_path>] [--format=json|text] [--management-group=<mgmt_group>] [--base-url=<base_url>] [--debug]"
    exit
fi


# If a Management Group was specified, use it in the az graph command
# TO BE IMPLEMENTED
if [[ -z "$mg" ]]; then
    mg_option=""
else
    mg_option="-m $mg"
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Setting management group $mg as scope for the az graph query commands..."; fi
fi

# If in "list_technologies" mode, just get the categories part:
if [[ "$list_technologies" == "yes" ]]
then
    # Get latest tree from repo
    git_tree_id=$(curl -s https://api.github.com/repos/Azure/review-checklists/commits | jq -r '.[0].commit.tree.sha')
    # Get list of checklists
    checklist_list=$(curl -s "https://api.github.com/repos/Azure/review-checklists/git/trees/${git_tree_id}?recursive=true" | jq -r '.tree[].path' | grep en.json | sed -e 's/_checklist.en.json//')
    while IFS= read -r checklist; do
        checklist_url="${base_url}${checklist}_checklist.en.json"
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Processing JSON content from URL $checklist_url..."; fi
        graph_query_no=$(curl -s "$checklist_url" | jq -r '.items[].graph' | grep -v -e '^null$' | wc -l)
        checklist_print=$(echo $checklist | cut -d/ -f2)
        echo "$checklist_print ($graph_query_no graph queries)"
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

# Process queries
i=0
query_no=0
this_category_name=""
json_output="{ \"metadata\": {\"format\": \"${format}\", \"timestamp\": \"$(date)\"}, \"checks\": ["
json_output_empty="yes"
while IFS= read -r graph_query; do
    i=$(($i+1))
    this_guid=$(echo $guid_list | head -$i | tail -1)
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: Processing check item $i, GUID '$this_guid'..."; fi
    # Check if there is any query
    if [[ "$graph_query" == "null" ]]; then
        if [[ "$no_empty" != "yes" ]]; then
            # Print title if required
            if [[ "$check_text" == "yes" ]]; then
                this_text=$(echo $text_list | head -$i | tail -1)
                echo "${blue}CHECKLIST ITEM: ${this_text}:${normal}"
            fi
            # Print output
            echo "N/A"
        fi
    else
        # Increase counter
        query_no=$(($query_no+1))
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Processing query \"$graph_query\"..."; fi
        # Get result of endpoint resources/policy
        # post "/providers/Microsoft.ResourceGraph/resources/policy?api-version=2018-09-01-preview&effect=$Effect" $Query
        az rest --method POST --uri "https://management.azure.com/providers/Microsoft.ResourceGraph/resources/policy?api-version=2018-09-01-preview" --body "{\"query\":\"$graph_query\"}" >$error_file
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
