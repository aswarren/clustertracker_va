# Calfornia Big Tree Cluster-Tracker
Code to generate a webpage displaying SARS-CoV-2 clusters and introductions inferred via [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce). SARS-CoV-2 introductions between California counties and U.S. states are displayed geographically on an interactive map and in a separate table below the map, with links to view and explore the data in Taxonium and the [California Big Tree Investigator](https://github.com/pathogen-genomics/paui-mapper). This version is a customizaton for use with data produced from the Calfornia Big Tree effort at UCSC for the California Department of Public Health; the original Cluster-Tracker project can be found [here](https://github.com/jmcbroome/introduction-website).

**Approach:** This site uses python to perform backend setup and vanilla javascript for website rendering. We use the protobuf file format to store mutation-annotated phylogentic tree information, and tab-separated text files (TSV) for metadata and text-based output files. Python scripts are used to process a mix of samples from California State and public repositories, and to launch the [matUtils](https://usher-wiki.readthedocs.io/en/latest/matUtils.html) suite of tools for manipulating the protobuf files and calculating the introductions into each region. We use the [Terra](https://terra.bio/) platform as our primary data pipeline, so our python scripts are modularized to be be compatible with WDL, but can also be run on the user's desktop computer. A [GeoJSON](https://geojson.org/) file with introductions for each region is created for input into a [Leaflet-based map](https://leafletjs.com/). TSV files supply a table below the map with cluster details. 

**Customization:** Information on how to create a customized version of Cluster Tracker can be found [below](#customizing-cluster-tracker). A python script and a number of data files would be required to preprocess your data if you wish to use data not in the [global public SARS-CoV-2 phylogenetic tree](https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/).

#### Contents

* [Screenshot and Features](#screenshot-and-features)
  * [Features](#features)
* [Quickstart](#quickstart)
  * Software Requirements
  * Input Data Files
  * [Quickstart Instructions](#quickstart-instructions)
* [Further Details](#further-details)
  * [Overview of Repo Folder Structure](#overview-of-repo-folder-structure)
  * [The Data Processing Pipeline](#the-data-processing-pipeline)
* [Customizing Cluster Tracker](#customizing-cluster-tracker)

## Screenshot and Features

<img width="700" style="border: 1px solid gray;" alt="CA Big Tree Cluster Tracker-2022-03-23 screen shot" src="https://user-images.githubusercontent.com/67020823/159781769-c84bfc77-0fda-412d-b790-ba980b03c496.png">

#### Features

* Displays on a map the total number of introductions into a region, and introductions from one region into another.
* Numbers of introductions can be displayed either in raw numbers or using log scaling.
* Introductions on the map can be filtered to show just those from the past 3 months, past 6 months, past 12 months, or the whole pandemic.
* A table below the map displays information for the top 100 clusters in the selected region and includes:
  * the number of samples in the cluster, the range of dates for the cluster, clade and lineage information, the inferred origin of the cluster and a score indicating the confidence of the origin estimate, the cluster's growth score (an importance estimate based on cluster size and age)
  * a link to view the cluster in [Taxonium](http://taxonium.org)
  * a link to view the samples in the California Big Tree Investigator tool, where users can join PHI to the phylogentic tree information (for authorized users only)
* All data in the table can be sorted in ascending or descending order.
* A search box allows the user to filter the table contents.
* Users can toggle between two levels of analysis: California counties or California state. The county-level introductions display introductions to and from Calfornia counties as well as other U.S. states. The state-level introductions display introductions between all of California (as a single region) and other states.
* The Taxonium protobuf file with phylogenetic tree information and a tab-separated file with information for all introductions can be downloaded for further analysis.

## Quickstart

**Software Requirements:** You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) (version 0.5.0 or later) installed and available on your path. You should have python 3 installed on your computer. Verify that the python "dateutil" package is included as some versions of python may be missing the dateutil standard package; it can be installed if needed via conda.

**NOTE:** The instructions in this section assume that output data files will be deployed to Pathogen Genomics' public web storage location in the cloud. See the instructions in the [Customization](#customizing-cluster-tracker) section below if you would like to deploy a local version of CA Big Tree Cluster Tracker on your computer for testing or development. Note that in a local version the links to Taxonium and Big Tree Investigator won't function properly unless the output files are stored in a publicly accessible location. 

**Input Data Files**

The following set of input files are required to create a fully functioning version of the California Big Tree Cluster Tracker. One protobuf and two metadata files, plus a GTF file and a FASTA file are required.

| File | Description/Notes |
| --- | --- |
| new_tree.pb | CA Big Tree MAT protobuf file compatible with [UShER](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#the-mutation-annotated-tree-mat-protocol-buffer-pb) |
| public.plusGisaid.latest.metadata.tsv | Metadata file for the public and GISAID data, in TSV format. The first line of the file should be a header with the following columns: strain, genbank_accession,date, country, host, completeness, length, Nextstrain_clade, pangolin_lineage, Nextstrain_clade_usher, pango_lineage_usher |
| samplemeta.tsv | Metadata file for the CDPH Calfornia county data, in TSV format. The first line of the file should be a header with the following columns: usherID, name, pango_lineage, nextclade_clade, gisaid_accession, county, collection_date, paui, sequencing_lab, specimen_id |
| ncbiGenes.gtf | Gene annotation GTF file; can be downloaded [here](https://usher-wiki.readthedocs.io/en/latest/_downloads/2052d9a7147253e32a3420939550ac63/ncbiGenes.gtf) |
| NC_045512v2.fa | FASTA reference sequence file; can be downloaded [here](https://raw.githubusercontent.com/yatisht/usher/5e83b71829dbe54a37af845fd23d473a8f67b839/test/NC_045512v2.fa). Used to produce a Taxonium view. |

### Quickstart Instructions
1. Clone this repository into your workspace of choice. (Note that "cdph" is the default branch for this repository; "main" is reserved for J. McBroome's original Cluster Tracker.)
2. Acquire the input data files and store in a directory that can be accesed from your workspace.
3. Navigate to the "data" directory of this cloned repo, and run "prepare_county_data.py" with the files obtained above, a la the below.

```
cd data
python3 prepare_county_data.py -i path/to/CA/Big/Tree/protobuf.pb -m path/to/metadata-file-1.tsv,path/to/metadata-file-2.tsv -H web/accessible/link/to/index/directory -f path/to/NC_045512v2.fa -a path/to/ncbiGenes.gtf -j us-states_ca-counties.geo.json -l state_and_county_lexicon.txt
gzip cview.pb
```

4. You can then view your results with a Python server initiated in the main directory.

```
cd ..
python3 -m http.server
```

## Further Details

### Overview of Repo Folder Structure

* data: contains python scripts for processing data files and for creating GeoJSON files used in the web site
* data/display_tables: folder where final output files for the website are created; may need to create this folder if it doesn't already exist
* src: contains JS source code and JS libraries used in the web site
* lib: contains Leaflet JS library used for the web site
* scripts: contains JS scripts used for the web site
* css: contains style sheets used for the web site

### The Data Processing Pipeline

#### Preprocessing the Data and Running the Master Backend

**data/prepare_county_data.py**

This script pre-processes the data and is a wrapper for the primary pipeline script (/data/master_backend.py). Its main functions are to merge the two metadata files, sort out unusable samples (those that cannot be attributed to a US state, don't have valid dates, or don't have valid Calif. county names), and extract only the usable samples into a new protobuf. It then runs the "master_backend" python script (which, in turn, computes the introductions).

**Arguments**

| Parameter | Description |
| --- | --- |
| -i path/to/protobuf-file.pb | Path to the protobuf file that forms the basis of the web display. |
| -m path/to/metadata-file.tsv | Path to the metadata file(s) (in TSV format) that correspond with the target protobuf file. If there is more than one file, separate them with commas. Currently, they must follow one of the two formats described above in the Quickstart section. |
| -H web/accessible/link/to/index/directory | Optional. Only necessary if building the files required for the web site. This will be the location where your web app resides. |
| -f path/to/reference-fasta-file.fa | Path to a reference fasta. |
| -a path/to/gtf-annotation-file.gtf | Path to a gtf annotation matching the reference. |
| -j path/to/region-geojson-file.json | Path to the geojson file describing the regions of interest. For the CA Big Tree Cluster-Tracker, this file is called "us-states_ca-counties.geo.json" and is located in the "data" subdirectory. |
| -l  path/to/lexicon-file.txt | A text file that aids in standarizing region names that occur in the metadata or can be parsed from the file name. List all variations for the region name separated by commas, with one line per region. The preferred region name should come first. For example, if "California" is the preferred region name but the metadata may contain "CA" or "Calif.", the line in the lexicon for this region would be: "California,CA,Calif." For the CA Big Tree Cluster-Tracker, this file is called "state_and_county_lexicon.txt", and is and is located in the "data" subdirectory. |

**Files generated**

| File Name | Description |
| --- | --- |
| clean.pb | MAT protobuf filtered to exclude unusable samples and samples outside the US. Required for input into "master_backend.py" |
| metadata_merged.tsv | Metadata file containing only the usable samples, created by combining metadata file #1 (public+GISAID metadata) and file #2 (CA county metadata). Required for input into "master_backend.py". |
| sample_regions.tsv | Stores the associations between the sample ID and the region name. Required for input into "master_backend.py"; important for matUtils introduce. |
| unlabeled_samples.txt | List of rejected samples, useful for debugging. |

### The Master Backend Script: Calculating Introductions and Generating Website Files

**data/master_backend.py**

This script takes the cleaned protobuf file generated above and uses [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce) to calculate the number of new introductions of the virus genome into each geographic region (in this case, all counties in California plus all U.S. States). It then generates a series of data tables for use in the web app, and creates a protobuf suitable for viewing in Taxonium.

**Primary data output files**

| File Name | Description |
| --- | --- |
| hardcoded_clusters.tsv | Output from matUtils introduce containing information for all the clusters. |
| cview.pb | Final output protobuf of clusters, suitable for viewing in Taxonium. |

**Output files for the UI and map**

| File Name | Description |
| --- | --- |
| region.js | This is the geoJSON file that is displayed in the Leaflet map, with all cluster counts and introductions. |
| display_tables/[region_name]_topclusters.tsv | Series of files, one for each region, that extracts the top 100 clusters in that region for quick display in the data table below the map. Includes links to Taxonium and CA Big Tree Investigator. |

## Customizing Cluster Tracker

**Software Requirements:** You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) (version 0.5.0 or later) installed and available on your path. You should have python 3 installed on your computer. Verify that the python "dateutil" package is included as some versions of python may be missing the dateutil standard package; it can be installed if needed via conda.

**Input File Requirements:**

* Mutation annotated protobuf file and corresponding metadata file. A gene annotation GTF file and FASTA reference sequence file are also required.
* To generate a website for your set of regions of interest, [you will first need to obtain a geojson representing your regions of interest.](https://geojson-maps.ash.ms). The region name should be specified with the "name" property. Each Feature should have an "id" property that can be used to identify the feature numerically. An example is provided under [example/data/us-states.geo.json](https://github.com/pathogen-genomics/introduction-website/blob/cdph/example/data/us-states.geo.json) file in the example/data folder.
* You will need to generate a sample-region two-column tsv, with sample identifiers in the first column and the ID of the region they are from in the second column.
* You will need what we're calling a "lexicon" file to ensure compatibility between region names- this is an unheaded csv containing in the first column the base name of each region to be used by the map, and comma separated after that, each other name for that region across your other files. An example is provided under [example/data/state_lexicon.txt](https://github.com/pathogen-genomics/introduction-website/blob/cdph/example/data/state_lexicon.txt).

**Aditional Considerations:** Our web site takes advantage of the ability of the [Taxonium](https://taxonium.org/) phylogenetic tree visualization tool to display data hosted from any publicly available web location. Currently, to view clusters in Taxonium using the link on the website table requires you to put the final output protobuf file (cview.pb) in a publicly available web location in order to function correctly. You can work around this by uploading the cview.pb / cluster_taxonium.pb that is output by the pipeline directly to Taxonium, then search for your cluster of interest from the website table using the search box on the resulting display. 

1. The simplest way to start would be to clone this repository and edit the code in the example folder. Follow the instructions in the Quick Start section if you would like to start development from this simple example.
2. Gather the files mentioned in the Input File Requirements section above. If you need to preprocess your data, you can use the example/data/prepare_us_states.py as a model. 
3. Once you've obtained and/or created the required files, you can either (a) copy the src/python files to your working directory, or navigate to the src/python directory and run:

```
python3 master_backend.py -i path/to/your.pb -m path/to/matching/metadata.tsv -f path/to/NC_045512v2.fa -a path/to/ncbiGenes.gtf -j path/to/your/geo.json -s path/to/your/sample_regions.tsv -l path/to/your/lexicon.txt -H web/accessible/link/to/index/directory
gzip cview.pb
```

You can optionally pass -G or -X parameters, which will be applied when introduce is called. 

Then navigate to the outermost index directory and run 
```
python3 -m http.server
```

**Customizations to the Cluster Table Below the Map:** Basic customizations to the table can be achieved by modifying the parameters in the loadTargetTable function of scripts/main.js. Documentation can be found [here](https://github.com/derekeder/csv-to-html-table). 

Data for the table comes from the output files from generate_display_tables.py (default_clusters.tsv and region_name_topclusters.tsv). Our version for CDPH includes additional fields not automatically generated from matUtils introduce. To do likewise, you may wish to modify both the generate_display_tables.py python script to insert data (we have done this by setting the is_custom_data flag in python script), and add additional custom_formatting elements in the scripts/main.js loadTargetTable function. If needed, you can modify the scripts/ssv_to_html_table.js library to manipulate how the data files are read. (Our modifications to these JS files can be seen in dist/scripts.)

**Customizing the Map--Basics:** We use [Leaflet.js](https://leafletjs.com/) for our mapping app. The scripts/main.js file is where you will find all the Leaflet map functions. Basic modifications:
* The map center and extent is done with the Leaflet [setView](https://github.com/pathogen-genomics/introduction-website/blob/756310ec0d81e575aa5348a9949d499bcdc733a4/src/js/main.js#L1) method in main.js.
* The color scale is set using the [map_colors parameter](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L6) variable the [legend_log](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L385-L395) variable in main.js.
* Color scale cut points can be modified in the [getColor* methods](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L28-L70) and in the [getBinVals and getLegendBins methods](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L328-L379) in main.js

**Customizing the Map--Advanced:** Additional map customizations can be found in our customization for CDPH, located in the dist folder. Of interest, we developed a toggle that can switch between a county-based view of introducions and a larger state-based view of introductions. This can be achieved by using Leaflet's

**Additional Considerations:** Modern browsers tend to cache files to make loading the website quicker. If your data files will be updated with regularity you may want to consider setting up your server so that it prevents cacheing.
