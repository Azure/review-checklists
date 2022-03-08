# Review Checklist Scripts (preview)

In this folder you can find scripts supporting the review process.

## Azure Resource Graph reviews

The script [checklist_graph.sh](./checklist_graph.sh) can do the automated graph queries associated to checklist items in the checklists in the [../checklists](../checklists) folder. It has multiple modes of operations, the following sections show some examples of how to use it.

### Installation

You can download the script in any environment that supports Azure CLI, such as the [Azure Cloud Shell](https://shell.azure.com). In order to download the script you can run this command:

```
wget –quiet –output-document ./checklist_graph.sh https://raw.githubusercontent.com/Azure/review-checklists/main/scripts/checklist_graph.sh
```

### Basic usage

You can run the script to produce a JSON-formated output of all the checklist items with documented Azure Resouce Graph queries. For example, to run the Azure Resource Graph queries for the AKS checklist, with the output in short format (no subscription IDs):

```
./checklist_graph.sh --technology=aks --output=json --format=short > /mnt/c/graph_short.json
```

The previous command will generate a JSON file `/mnt/c/graph_short.json` (using the Windows Subsystem for Linux here, as you probably guessed). You can go now to your Excel spreadsheet. Make sure you have loaded up the corresponding checklist already (AKS in this example), and use the Advanced command "Import Graph Results" to import this file into the spreadsheet:

![Advanced buttons](../pictures/advanced_buttons.png)

The "Comments" column of the spreadsheet will fill in with the results of the Azure Graph Queries:

- Under "Success" you will see resources that are compliant with that specific check
- Under "Failure" resources that are not compliant with the corresponding check will be shown

This example shows the result of importing the results of the Azure Resource Graph checks on a subscription with a single AKS cluster:

![Advanced ](../pictures/graph_import_result.png)

As you can see, for those checklist items with Graph queries stored, the results of the Azure Resource Graph queries are stored. This shows that the AKS cluster used in this example is not compliant with most of the checks, which can make the review easier.

The following sections will show more advanced usage of the script.

### Listing the existing categories in a checklist

You can run the script as well to generate a more human-readable output. For example, run this in order to execute analysis scoped to a single category. Command:

```
./checklist_graph.sh --techonology=aks --list-categories
```

Output:

```
0: - Identity and Access Management
1: - Network Topology and Connectivity
2: - BC and DR
3: - Governance and Security
4: - Cost Governance
5: - Operations
6: - Application Deployment
```

### Doing a review for all categories with console output

This example shows how to run this for analysis on all categories in a single subscription. The output can be copy/pasted to the Excel spreadsheet (category by category). Command:

```
./checklist_graph.sh --techonology=aks
```

Output (truncated for brevity). Note that the resources are formated with the syntax `<resource-group>/<resource-name>`:

```
CHECKLIST CATEGORY: BC and DR
N/A
N/A
N/A
Success: None. Fail: akstest/aks101cluster
Success: None. Fail: akstest/aks101cluster
N/A
N/A
CHECKLIST CATEGORY: Identity and Access Management
Success: akstest/aks101cluster. Fail: None
Success: None. Fail: akstest/aks101cluster
N/A
N/A
N/A
N/A
...
```

### Doing a review for a single with console output

Again, you can use the `--category` paramater as in this example for analysis on a single category (you need the category ID retrieved by running the script with the `--list-categories` flag) in a single subscription. The output can be copy/pasted to the Excel spreadsheet. Command:

```
./checklist_graph.sh --techonology=aks --category=1
```

Output:

```
CHECKLIST CATEGORY: Network Topology and Connectivity
Success: akstest/aks. Fail: akstest/aks101cluster
N/A
N/A
N/A
Success: None. Fail: akstest/aks,akstest/aks101cluster
Success: None. Fail: akstest/aks,akstest/aks101cluster
N/A
N/A
N/A
Success: None. Fail: akstest/aks,akstest/aks101cluster
Success: akstest/aks. Fail: akstest/aks101cluster
N/A
N/A
Success: None. Fail: akstest/aksVnet
Success: akstest/aks,akstest/aks101cluster. Fail: None
Success: akstest/aks. Fail: None
N/A
N/A
```

### Doing a review for a single category with JSON output

This example is very similar to the first one in this page, but it runs with default formatting (long), where each resource is identified by its full resource ID. Run this for analysis on a single category (you need the category ID retrieved by running the script with the `--list-categories` flag) in a single subscription. The JSON output can redirected to a file, that can be later imported in the Excel spreadsheet. Command:

```
./checklist_graph.sh --technology=aks --category=1 --output=json
```

Optionally you can redirect the output to a file:

```
./checklist_graph.sh --technology=aks --category=1 --output=json >graph_check.json
```

You can use the `jq` utility to pretty-print the output (you might need to install it in your Linux distro, in [Azure Cloud Shell](https://shell.azure.com) it is already installed):

```
./checklist_graph.sh --technology=aks --category=1 --output=json | jq
```

Output:

```
{
  "checks": [
    {
      "guid": "a0f61565-9de5-458f-a372-49c831112dbd",
      "success": "akstest/aks",
      "failure": "akstest/aks101cluster"
    },
    {
      "guid": "3b365a91-7ecb-4e48-bbe5-4cd7df2e8bba",
      "success": "None",
      "failure": "akstest/aks,akstest/aks101cluster"
    },
    {
      "guid": "c4581559-bb91-463e-a908-aed8c44ce3b2",
      "success": "None",
      "failure": "akstest/aks,akstest/aks101cluster"
    },
    {
      "guid": "ecccd979-3b6b-4cda-9b50-eb2eb03dda6d",
      "success": "None",
      "failure": "akstest/aks,akstest/aks101cluster"
    },
    {
      "guid": "58d7c892-ddb1-407d-9769-ae669ca48e4a",
      "success": "akstest/aks",
      "failure": "akstest/aks101cluster"
    },
    {
      "guid": "9bda4776-8f24-4c11-9775-c2ea55b46a94",
      "success": "None",
      "failure": "akstest/aksVnet"
    },
    {
      "guid": "8008ae7d-7e4b-4475-a6c8-bdbf59bce65d",
      "success": "akstest/aks,akstest/aks101cluster",
      "failure": "None"
    },
    {
      "guid": "ba7da7be-9952-4914-a384-5d997cb39132",
      "success": "None",
      "failure": "None"
    }
  ]
}
```

### Run the graph queries scoped to a Management Group

All previous commands can be scoped to a management group, instead of to a single subscription by using the `--management-group` flag, to specify a management group name (make sure to specify the **name** and not the **display name** of the management group). Example:

```
./checklist_graph.sh --technology=aks --category=1 --management-group=mymgmtgroup
```

The output is the same as the previous examples, depending on which flags are used.

### Run the queries with resource IDs as output

The previous queries return the compliant and non-compliant resources in the syntax `<resource_group>/<resource_name>`, but if having multiple subscriptions you probably want the full ARM ID of the compliant/non-compliant resources. The flag `--format=long` does exactly that. Note that this format cannot be imported in the Excel spreadsheet at this time (see [issue 33](https://github.com/Azure/review-checklists/issues/33)). Here an example:

```
./checklist_graph.sh --technology=aks --category=1 --output=json --format=long
```

Output (truncated for readability):

```
{
  "checks": [
    {
      "guid": "a0f61565-9de5-458f-a372-49c831112dbd",
      "result": "success",
      "id": "/subscriptions/e7da9914-9b05-4891-893c-546cb7b0422e/resourceGroups/akstest/providers/Microsoft.ContainerService/managedClusters/aks"
    },
    {
      "guid": "a0f61565-9de5-458f-a372-49c831112dbd",
      "result": "fail","id": "/subscriptions/e7da9914-9b05-4891-893c-546cb7b0422e/resourceGroups/akstest/providers/Microsoft.ContainerService/managedClusters/aks101cluster"
    },
    {
      "guid": "3b365a91-7ecb-4e48-bbe5-4cd7df2e8bba",
      "result": "fail",
      "id": "/subscriptions/e7da9914-9b05-4891-893c-546cb7b0422e/resourceGroups/akstest/providers/Microsoft.ContainerService/managedClusters/aks"
    },
    {
      "guid": "3b365a91-7ecb-4e48-bbe5-4cd7df2e8bba",
      "result": "fail",
      "id": "/subscriptions/e7da9914-9b05-4891-893c-546cb7b0422e/resourceGroups/akstest/providers/Microsoft.ContainerService/managedClusters/aks"
    },
    ...
```