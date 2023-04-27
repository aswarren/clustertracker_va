# Calfornia Big Tree Cluster-Tracker Development and Testing Notes

The California Big Tree Cluster Tracker uses Google Cloud for storage, deployment, and testing. In addition to UShER and TaxoniumTools, as noted in the main [README](../README.md), you will want to [install the Google Cloud SDK](https://cloud.google.com/sdk/docs/install) and [initialize](https://cloud.google.com/sdk/docs/initializing) it for use on your local machine.

## Testing the Web Site Locally

If no changes to the data files are needed, testing the user interface locally should suffice. After performing any necessary commits/merges, navigate to "cdph/www" and start the Python server:

```
cd cdph/www
python3 -m http.server
```

The website should be available for testing at http://localhost:8000/

## Development and Testing of the Python Data Processing Scripts

The Python scripts for data processing have been modularized so they can be translated into WDL tasks in Terra. This makes development and testing a little easier as each python script can be run on its own. All subtasks -- except for running matUtils introduce -- can be run locally to test code changes. 

It is recommended to run matUtils introduce on a Virtual Machine with enough memory (ideally, more than 200 GB). The VM "matutils-cluster-tracker-1" has been set up as a "[n2-highmem-48](https://cloud.google.com/compute/docs/general-purpose-machines#n2-high-mem)" machine type (48 vCPUs, 384 GB memory, 32 Gbps bandwidth).

Before running matUtils, either locally or on a VM, you will want to make sure UShER is updated. Installation instructions for UShER can be found on the [UShER wiki](https://usher-wiki.readthedocs.io/en/latest/Installation.html).

Instructions for running each processing step, including detailed descriptions of each input file and output file, can be found in the "Python to WDL Workflow Inputs/Outputs" Google doc (CDPH Genomics > Big Tree Cluster Tracker).

To test a new set of output files:
1. Copy the primary set of output files (cluster_data.json.gz, sample_data.json.gz, cview.jsonl.gz, and regions.js) to a convient location in our Google Cloud bucket. The "dev" subfolder within the "ucsc-gi-cdph-bigtree/display_tables" folder can be used for this purpose if desired.
2. Change the following items in cdph/www/index.html:
  * In the header, change the URL of the "dataHost" variable (e.g., to https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/dev/).
  * You probably won't be able to test the links to Taxonium without also creating a new backend for testing, so you can leave the "taxoniumHost" variable as is.
  * At the bottom of the file, change the URL of the "regions.js" file (e.g., to https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/dev/).
3. The "cview.jsonl.gz" file is likely to be too large for using taxonium.org's default backend, so you can test this file manually by downloading the [desktop version of Taxonium](https://docs.taxonium.org/en/latest/app.html).
4. Navigate to the "www" folder. Then deploy the app to Google Cloud App Engine using the "--no-promote" and "--verson" flags.
```
cd cdph/www
gcloud app deploy --no-promote --version dev
```
5. The "app deploy" command will give you the URL to use to access the app.

## Deploying the Web Site to Production 

To deploy California Big Tree Cluster Tracker to Google Cloud App Engine, first navigate to the "cdph/www" folder and then use the deploy command:
```
cd cdph/www
gcloud app deploy
```
