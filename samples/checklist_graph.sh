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
#    -d/--debug: increase verbosity
#    -l/--list-categories: instead of running Azure Graph queries, it only displays the categories in the file and its corresponding indexes
#
# Example:
#       ./checklist_graph.sh -l -t=aks
#       ./checklist_graph.sh -c=0 -t=aks
#
# Jose Moreno, October 2021
###################################################################################################


# Defaults
base_url="https://raw.githubusercontent.com/Azure/review-checklists/main/samples/"
technology="aks"
category_id=""
debug="no"
error_file=/tmp/error.json
list_categories=no
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
          -d*|--debug*)
               debug="yes"
               shift # past argument with no value
               ;;
     esac
done
set -- "${POSITIONAL[@]}" # restore positional parameters

# Set URL and download checklist from base URL
checklist_url="${base_url}${technology}_checklist.en.json"
if [[ "$debug" == "yes" ]]; then echo "DEBUG: Getting checklist from $checklist_url..."; fi
checklist_json=$(curl -s "$checklist_url")

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

# Get a list of graph queries
if [[ -n "$category_name" ]]
then
    graph_success_list=$(echo $checklist_json | jq -r '.items[] | select(.category=="'$category_name'") | .graph_success')
    graph_failure_list=$(echo $checklist_json | jq -r '.items[] | select(.category=="'$category_name'") | .graph_failure')
    category_list=$(echo $checklist_json | jq -r '.items[] | select(.category=="'$category_name'") | .category')
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $category_list | wc -l) tests found in the checklist for category ${category_name}."; fi
else
    graph_success_list=$(echo $checklist_json | jq -r '.items[] | .graph_success')
    graph_failure_list=$(echo $checklist_json | jq -r '.items[] | .graph_failure')
    category_list=$(echo $checklist_json | jq -r '.items[] | .category')
    if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $category_list | wc -l) tests found in the checklist."; fi
fi

# Debug
if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $graph_success_list | wc -l) graph queries for success tests found in the checklist."; fi
if [[ "$debug" == "yes" ]]; then echo "DEBUG: $(echo $graph_failure_list | wc -l) graph queries for failure tests found in the checklist."; fi

# Make sure the Azure CLI extension for Azure Resource Graph is installed and updated
extension_name=resource-graph
extension_version=$(az extension show -n $extension_name --query version -o tsv 2>/dev/null)
if [[ -z "$extension_version" ]]
then
    echo "Azure CLI extension $extension_name not found, installing now..."
    az extension add -n $extension_name -o none 2>/dev/null
else
    echo "Azure CLI extension $extension_name found with version $extension_version, trying to upgrade..."
    az extension update -n $extension_name -o none 2>/dev/null
fi
extension_version=$(az extension show -n $extension_name --query version -o tsv 2>/dev/null)
echo "Azure CLI extension $extension_name running with version $extension_version"

# Run queries
i=0
this_category_name=""
while IFS= read -r graph_success_query; do
    i=$(($i+1))
    #if [[ "$debug" == "yes" ]]; then echo "Processing check item $i..."; fi
    # Print header category if required
    if [[ "$this_category_name" != "$(echo $category_list | head -$i | tail -1)" ]]
    then
        this_category_name=$(echo $category_list | head -$i | tail -1)
        echo "INFO: Checking graph queries for category $this_category_name..."
    fi
    # Check if there is any query stored
    if [[ "$graph_success_query" == "null" ]]
    then
        # Print output
        echo "N/A"
    else
        rm $error_file 2>/dev/null; touch $error_file
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Running success query $graph_success_query..."; fi
        success_result=$(az graph query -q "$graph_success_query" -o json 2>$error_file | jq -r '.data[] | "\(.resourceGroup)/\(.name)"' 2>>$error_file | tr '\n' ',')
        if [[ -s $error_file ]]; then
            success_result="Error ";
            if [[ "$debug" == "yes" ]]; then cat $error_file; fi
        fi
        rm $error_file 2>/dev/null; touch $error_file
        graph_failure_query=$(echo $graph_failure_list | head -$i | tail -1)
        if [[ "$debug" == "yes" ]]; then echo "DEBUG: Running failure query $graph_failure_query..."; fi
        failure_result=$(az graph query -q "$graph_failure_query" -o json 2>$error_file | jq -r '.data[] | "\(.resourceGroup)/\(.name)"' 2>>$error_file | tr '\n' ',')
        if [[ -s $error_file ]]; then
            failure_result="Error "
            if [[ "$debug" == "yes" ]]; then cat $error_file; fi
        fi
        # Remove last comma
        failure_result=${failure_result%?}
        success_result=${success_result%?}
        # Replace empty string with 'none'
        if [[ -z "$success_result" ]]; then success_result='None'; fi
        if [[ -z "$failure_result" ]]; then failure_result='None'; fi
        # Print output
        echo "Success: $success_result. Fail: $failure_result"
    fi
done <<< "$graph_success_list"
