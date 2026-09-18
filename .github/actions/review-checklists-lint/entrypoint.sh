#!/bin/sh -l

# Initialization
file_extension="$1"
key_name="$2"
criteria_key="$3"
criteria_value="$4"
file_list=$(eval "ls -R1 */*.$file_extension")
number_of_checklists=$(echo $file_list | wc -l)

# Info message
echo "DEBUG: Running with file_extension=$file_extension, key_name=$key_name, criteria_key=$criteria_key, criteria_value=$criteria_value"

# Check JSON field uniqueness (GUID for azure checklists)
uniqueguid_file_exclusions='./checklists-ext/theaks_checklist.en.json'
performed_tests=0
unique_failed_tests=0
unique_failed_tests_not_counted=0
IFS=''

for file in $file_list; do
    echo "DEBUG: Processing $file..."
    performed_tests=$((performed_tests+1))
    # Figure out whether we want to process this specific one, if criteria were specified
    process=yes
    if [ -n "$criteria_key" -a -n "$criteria_value" ]; then
        file_criteria_value=$(cat $file | jq -r "$criteria_key")
        if [ "$file_criteria_value" != "$criteria_value" ]; then
            echo "DEBUG: File $file: retrieved criteria value $file_criteria_value does not match criteria $criteria_value (JSON key $criteria_key)"
            process=no
        fi
    fi
    # Process file for unique keys
    if [ "$uniqueguid_file_exclusions" =~ .*"$file".* ]; then
        echo "DEBUG: skipping file $file for GUID uniqueness."
    else
        all_guids=$(cat $file | jq -r "try .. | objects | select( .$key_name) | .$key_name" | wc -l)
        unique_guids=$(cat $file | jq -r "try .. | objects | select( .$key_name) | .$key_name" | sort -u | wc -l)
        if [ "$all_guids" -eq "$unique_guids" ]; then
            echo "INFO: File $file has $all_guids GUIDs, and all are unique"
        else
            echo "INFO: File $file has $all_guids GUIDs, but only $unique_guids are unique"
            if [ "$process" == "yes" ]; then
                unique_failed_tests=$((failed_tests+1))
            else
                unique_failed_tests_not_counted=$((failed_tests_not_counted+1))
            fi
        fi
    fi
    # Check categories
    category_items=$(cat $file | jq -r 'try .. | objects | select( .category) | .category' | sort -u)
    category_list=$(cat $file | jq -r ".categories[].name" | sort -u)
    if [ "$category_items" == "$category_list" ]; then
        echo "INFO: categories in checklist $file match with the categories defined in the checks"
    else
        echo "INFO: there is a discrepancy in the categories defined in file $file."
        echo "DEBUG: categories in check items: $category_items"
        echo "DEBUG: categories in category list: $category_list"
    fi
    # Check any missing severity
    wrong_items=$(cat $file | jq -r '.items[] | select(has("severity") | not) | .guid')
    if [[ -z $wrong_items ]]; then
        echo "DEBUG: all items in file $file have the severity attribute"
    else
        echo "INFO: the following items have a missing severity in file $file:"
        echo $wrong_items
        if [ "$process" == "yes" ]; then
            unique_failed_tests=$((failed_tests+1))
        else
            unique_failed_tests_not_counted=$((failed_tests_not_counted+1))
        fi
    fi
    # Check any missing category
    wrong_items=$(cat $file | jq -r '.items[] | select(has("category") | not) | .guid')
    if [[ -z $wrong_items ]]; then
        echo "DEBUG: all items in file $file have the category attribute"
    else
        echo "INFO: the following items have a missing category in file $file:"
        echo $wrong_items
        if [ "$process" == "yes" ]; then
            unique_failed_tests=$((failed_tests+1))
        else
            unique_failed_tests_not_counted=$((failed_tests_not_counted+1))
        fi
    fi
done
echo "DEBUG: $performed_tests files verified, $unique_failed_tests FAILED lint checks ($unique_failed_tests_not_counted files failed the check, but did not match the criteria)"
echo "number_of_checklists=$number_of_checklists" >> $GITHUB_OUTPUT
# Break the test only if there are not unique GUIDs for a checklist matching the criteria
if [ "$unique_failed_tests" -gt 0 ]; then
    exit 1
fi