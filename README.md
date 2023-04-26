# Calfornia Big Tree Cluster-Tracker
Code to generate a webpage displaying SARS-CoV-2 clusters and introductions inferred via [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce). SARS-CoV-2 introductions between California counties and U.S. states are displayed geographically on an interactive map and in a separate table below the map, with links to view and explore the data in [Taxonium](http://taxonium.org) and the [California Big Tree Investigator](https://github.com/pathogen-genomics/paui-mapper). This version is a customizaton for use with data produced from the Calfornia Big Tree effort at UCSC for the California Department of Public Health; the original Cluster-Tracker project can be found [here](https://github.com/jmcbroome/introduction-website).

**Approach:** This site uses python to perform backend setup and vanilla javascript for website rendering. We use the protobuf file format to store mutation-annotated phylogentic tree information, and tab-separated text files (TSV) for metadata and text-based output files. Python scripts are used to process a mix of samples from California State and public repositories, and to launch the [matUtils](https://usher-wiki.readthedocs.io/en/latest/matUtils.html) suite of tools for manipulating the protobuf files and calculating the introductions into each region. [TaxoniumTools](https://docs.taxonium.org/en/latest/taxoniumtools.html) is used to convert protobuf files to JSONL for use in the Taxonium viewer. We use the [Terra](https://terra.bio/) platform as our primary data pipeline, so our python scripts are modularized to be be compatible with WDL, but can also be run on the user's desktop computer. A [GeoJSON](https://geojson.org/) file with introductions for each region is created for input into a [Leaflet-based map](https://leafletjs.com/). JSON files supply a table below the map with cluster details. 

**Customization:** Information on how to create a customized version of Cluster Tracker can be found in the [README](example/README.md) in the "examples" directory. A python script and a number of data files would be required to preprocess your data if you wish to use data not in the [global public SARS-CoV-2 phylogenetic tree](https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/).

#### Contents

* [Screenshot and Features](#screenshot-and-features)
  * [Features](#features)
* [Quickstart](#quickstart)
  * Software Requirements
  * Input Data Files
  * [Quickstart Instructions](#quickstart-instructions)
* [Further Details](#further-details)
  * [Overview of Repo Folder Structure](#overview-of-repo-folder-structure)

## Screenshot and Features

<img width="900" style="border: 1px solid gray;" alt="CA Big Tree Cluster Tracker screen shot" src="https://user-images.githubusercontent.com/67020823/234706279-a62680b5-ee23-48cf-b275-788a3238bba7.png">

#### Features

* Displays on a map the total number of introductions into a region, and introductions from one region into another.
* Numbers of introductions can be displayed with log scaling applied or as actual numbers of introductions.
* Introductions on the map can be filtered to show just those from the past 3 months, past 6 months, past 12 months, or the whole pandemic.
* Users can toggle between two levels of analysis: California counties or California state. The county-level introductions display introductions to and from Calfornia counties as well as other U.S. states. The state-level introductions display introductions between all of California (as a single region) and other states.
* A table below the map displays information about clusters in the selected region and includes:
  * the number of samples in the cluster, the range of dates for the cluster, clade and lineage information, a list of potential origins for the cluster and an index value indicating the confidence associated with the potential origin, the cluster's growth score (an importance estimate based on cluster size and age)
  * a link to view the cluster in [Taxonium](http://taxonium.org)
  * a link to view the samples in the California Big Tree Investigator tool, where users can join PHI to the phylogentic tree information (for authorized users only)
  * all sample names in the cluster
  * for CDPH samples, a list of all associated specimen IDs
* All data in the table can be sorted in ascending or descending order. Mulitple column sorting can be achieved by pressing the Shift key while clicking on a second column.
* A search tool allows the user to filter the table contents.
  * Search on one or more columns for text containing a search string. Multiple phrases can be searched for using logical "and" or "or" criteria.
  * The table can also be filtered by date range, cluster size, or growth score.
* Table data can be copied by selecting a range of table cells and using Ctrl-C to copy the contents to the computer's clipboard.
* The Taxonium JSONL file with phylogenetic tree information and a tab-separated file with information for all introductions can be downloaded for further analysis.

## Quickstart

Use this Quickstart guide to create a basic U.S.-based implementation of Cluster Tracker using public SARS-CoV-2 data.

**Software Requirements:** You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) (version 0.6.2 or later) and [TaxoniumTools](https://docs.taxonium.org/en/latest/taxoniumtools.html) installed and available on your path. You should have python 3 installed on your computer. Verify that the python "dateutil" package is included as some versions of python may be missing the dateutil standard package; it can be installed if needed via conda.

**Input Data Files**

Use the following set of input files to create a basic implementation of Cluster Tracker.

| File | Description/Notes |
| --- | --- |
| MAT protobuf file | Should be compatible with [UShER](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#the-mutation-annotated-tree-mat-protocol-buffer-pb). Download ["public-latest.all.masked.pb"](https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/) to use with the processing scripts in the example directory. |
| Metadata file | Metadata file in TSV format. Download ["public-latest.metadata.tsv.gz"](https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/) to use with the processing scripts in the example directory. |
| hu1.gb | Gene annotation file; can be downloaded [here](https://raw.githubusercontent.com/theosanderson/taxonium/master/taxoniumtools/test_data/hu1.gb). Used to produce a Taxonium view. |

### Quickstart Instructions
1. Clone this repository into your workspace of choice. (Note that "cdph" is the default branch for this repository; "main" is reserved for J. McBroome's original Cluster Tracker.)
2. Acquire the input data files and store in a directory that can be accesed from your workspace. (You can put these files in the "example/data" directory to simplify the data processing, if desired.)
3. Navigate to the "example/data" directory of this cloned repo, and run "prepare_us_states.py" with the files obtained above, a la the below.

```
cd example/data
python3 prepare_county_data.py -i path/to/CA/Big/Tree/protobuf.pb -m path/to/metadata-file.tsv -H web/accessible/link/to/index/directory -a path/to/hu1.gb -j us-states.geo.json -l state_lexicon.txt -x “genbank_accession,country,date,name,pangolin_lineage”
```

4. You can then view your results with a Python server initiated in the example directory.

```
cd ..
python3 -m http.server
```

## Further Details

### Overview of Repo Folder Structure

* cdph: Contains source code for data processing and the web app for the California Big Tree Cluster Tracker.
  * data: Contains python source code for data processing as well as extra files needed during creation and transfer of output files to the Google Cloud storage bucket, and a copy of the Taxonium config file for customizing the Taxonium interface.
  * www: Contains files (except for the data files) to be deployed via Google App Engine for the CA Big Tree Cluster Tracker web site. (Note: data files are hosted via GCP.)
  * [README.md](cdph/README.md): Contains data processing and deployment notes for the California Big Tree Cluster Tracker.
* example: Contains source code for data processing and the web app for creating a basic implementation of Cluster Tracker. Note that this basic version simplifies the California Big Tree Cluster Tracker by eliminating the option for California-county-based introductions.
  * data: Contains python source code for data processing using the global public SARS-CoV-2 phylogenetic tree and creating US-state-based introductions.
  * www: Contains all files needed for the web app except for data files and a customized Taxonium backend.
  * [README.md](example/README.md): Contains notes on how to customize Cluster Tracker for a different geographic region.
* src/js: Contains source code for the JS libraries used in the California Big Tree Cluster Tracker app.
