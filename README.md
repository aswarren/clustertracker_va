# Calfornia Big Tree Cluster-Tracker
Code to generate a webpage displaying SARS-CoV-2 clusters and introductions inferred via [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce). SARS-CoV-2 introductions between California counties and U.S. states are displayed geographically on an interactive map and in a separate table below the map, with links to view and explore the data in [Taxonium](http://taxonium.org) and the [California Big Tree Investigator](https://github.com/pathogen-genomics/paui-mapper). This version is a customizaton for use with data produced from the Calfornia Big Tree effort at UCSC for the California Department of Public Health; the original Cluster-Tracker project can be found [here](https://github.com/jmcbroome/introduction-website).

**Approach:** This site uses python to perform backend setup and vanilla javascript for website rendering. We use the protobuf file format to store mutation-annotated phylogentic tree information, and tab-separated text files (TSV) for metadata and text-based output files. Python scripts are used to process a mix of samples from California State and public repositories, and to launch the [matUtils](https://usher-wiki.readthedocs.io/en/latest/matUtils.html) suite of tools for manipulating the protobuf files and calculating the introductions into each region. [TaxoniumTools](https://docs.taxonium.org/en/latest/taxoniumtools.html) is used to convert protobuf files to JSONL for use in the Taxonium viewer. We use the [Terra](https://terra.bio/) platform as our primary data pipeline, so our python scripts are modularized to be be compatible with WDL, but can also be run on the user's desktop computer. A [GeoJSON](https://geojson.org/) file with introductions for each region is created for input into a [Leaflet-based map](https://leafletjs.com/). JSON files supply a table below the map with cluster details. 

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
* [Customizing Cluster Tracker](#customizing-cluster-tracker)
  * Software Requirements
  * Input File Requirements
  * Additional Considerations
  * General Steps
  * Customizations to the Cluster Table Below the Map
  * Customizing the Map--Basics
  * Customizing the Map--Advanced
  * Additional Notes

## Screenshot and Features

<img width="900" style="border: 1px solid gray;" alt="CA Big Tree Cluster Tracker 2022-09-16 screen shot" src="https://user-images.githubusercontent.com/67020823/190701837-753e7891-71df-434d-91cd-7b90bf2aa46c.png">

#### Features

* Displays on a map the total number of introductions into a region, and introductions from one region into another.
* Numbers of introductions can be displayed either in raw numbers or using log scaling.
* Introductions on the map can be filtered to show just those from the past 3 months, past 6 months, past 12 months, or the whole pandemic.
* Users can toggle between two levels of analysis: California counties or California state. The county-level introductions display introductions to and from Calfornia counties as well as other U.S. states. The state-level introductions display introductions between all of California (as a single region) and other states.
* A table below the map displays information clusters in the selected region and includes:
  * the number of samples in the cluster, the range of dates for the cluster, clade and lineage information, the best potential origin for the cluster and an index value indicating the confidence of the origin estimate, the cluster's growth score (an importance estimate based on cluster size and age)
  * a link to view the cluster in [Taxonium](http://taxonium.org)
  * a link to view the samples in the California Big Tree Investigator tool, where users can join PHI to the phylogentic tree information (for authorized users only)
  * all sample names in the cluster
  * for CDPH samples, a list of all associated specimen IDs
* All data in the table can be sorted in ascending or descending order. 
* Mulitple column sorting can be achieved by pressing the Shift key while clicking on a second column.
* A search box allows the user to filter the table contents.
* Table data can be copied by selecting a range of table cells and using Ctrl-C to copy the contents to the computer's clipboard.
* The Taxonium JSONL file with phylogenetic tree information and a tab-separated file with information for all introductions can be downloaded for further analysis.

## Quickstart

Use this Quickstart guide to create a basic U.S.-based implementation of Cluster Tracker using public SARS-CoV-2 data.

**Software Requirements:** You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) (version 0.5.0 or later) and [TaxoniumTools](https://docs.taxonium.org/en/latest/taxoniumtools.html) installed and available on your path. You should have python 3 installed on your computer. Verify that the python "dateutil" package is included as some versions of python may be missing the dateutil standard package; it can be installed if needed via conda.

**Input Data Files**

Use the following set of input files to create a basic implementation of Cluster Tracker.

| File | Description/Notes |
| --- | --- |
| MAT protobuf file | Should be compatible with [UShER](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#the-mutation-annotated-tree-mat-protocol-buffer-pb). Download ["public-latest.all.masked.pb"](https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/) to use with the processing scripts in the example directory. |
| Metadata file | Metadata file in TSV format. Download ["public-latest.metadata.tsv.gz"](https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/) to use with the processing scripts in the example directory. |
| hu1.gb | Gene annotation file; can be downloaded [here](https://raw.githubusercontent.com/theosanderson/taxonium/master/taxoniumtools/test_data/hu1.gb) Used to produce a Taxonium view. |

### Quickstart Instructions
1. Clone this repository into your workspace of choice. (Note that "cdph" is the default branch for this repository; "main" is reserved for J. McBroome's original Cluster Tracker.)
2. Acquire the input data files and store in a directory that can be accesed from your workspace.
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

* build: python processing scripts and helper bash shell scripts for producing the CDPH customization of CA Big Tree Cluster Tracker
* dist: files to be deployed via Google App Engine for the CA Big Tree Cluster Tracker web site. (Note: data files are hosted via GCP)
* example: example JS and python code for creating a basic implementation of Cluster Tracker
* lib: contains Leaflet JS libarary
* src: JS and python source code for creating a basic implementation of Cluster Tracker

## Customizing Cluster Tracker

**Software Requirements:** You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) (version 0.5.0 or later) and [TaxoniumTools](https://docs.taxonium.org/en/latest/taxoniumtools.html) installed and available on your path. You should have python 3 installed on your computer. Verify that the python "dateutil" package is included as some versions of python may be missing the dateutil standard package; it can be installed if needed via conda.

**Input File Requirements:**

* Mutation annotated protobuf file and corresponding metadata file. A gene annotation file is also required.
* To generate a website for your regions of interest, you will first need to obtain a [geojson]((https://geojson-maps.ash.ms)) formatted file representing your regions of interest. Region names should be specified with the "name" property. Each Feature should have an "id" property that can be used to identify the feature numerically. An example file can be found at [example/data/us-states.geo.json](https://github.com/pathogen-genomics/introduction-website/blob/cdph/example/data/us-states.geo.json) in the example/data folder.
* You will need to generate a sample-region two-column tsv, with sample identifiers in the first column and the name of the region they are from in the second column. Do not include a header row. Example:
```
USA/CA-CZB-9556/2020|MW483159.1|2020-04-13	California
USA/DC-DFS-PHL-0022/2020|MZ488067.1|2020-03-20	District of Columbia
USA/WV-QDX-1284/2020|MW065351.1|2020-03-17	West Virginia
...
```
* You will need what we're calling a "lexicon" file to ensure compatibility between region names- this is an unheaded csv containing in the first column the base name of each region to be used by the map, and comma separated after that, each other name for that region across your other files. An example is provided under [example/data/state_lexicon.txt](https://github.com/pathogen-genomics/introduction-website/blob/cdph/example/data/state_lexicon.txt).

**Additional Considerations:** Our web site takes advantage of the ability of the [Taxonium](https://taxonium.org/) phylogenetic tree visualization tool to display data hosted from any publicly available web location. Currently, to view clusters in Taxonium using the link on the website table requires you to put the final output file (cview.jsonl.gz) in a publicly available web location. You can work around this by uploading the cview.jsonl.gz file that is output by the pipeline directly to Taxonium, then search for your cluster of interest from the website table using the search box on the resulting display. 

**General Steps**

1. The simplest way to start would be to clone this repository and edit the code in the example folder. Follow the instructions in the Quick Start section if you would like to start development from this simple example.

2. Gather the files mentioned in the Input File Requirements section above. If you need to preprocess your data, you can use [example/data/prepare_us_states.py](https://github.com/pathogen-genomics/introduction-website/blob/cdph/example/data/prepare_us_states.py) as a model. If you include the parse_setup method in your pre-processing script, you can use the same arguments you would with the main master_backend.py script. If you have several different sources of samples, with a different metadata format for each source, the -m argument can handle multiple metadata files (e.g., "-m metadata1.tsv metadata2.tsv").

3. Once you've obtained and/or created the required files, navigate to your data directory (e.g., example/data) and run:

```
python3 master_backend.py -i path/to/your.pb -m path/to/matching/metadata.tsv -a path/to/hu1.gb -j path/to/your/geo.json -s path/to/your/sample_regions.tsv -l path/to/your/lexicon.txt -H web/accessible/link/to/index/directory
```
(You may need to adjust the path to the src/python/master_backend.py file depending on where your working data directory is. If you are working from the example/data folder, you would specify "../../src/python/master_backend.py".)

You can optionally pass the following parameters to master_backend.py:
* -d: Path to a two-column tsv containing sample names and collection dates in YYYY-MM-DD format. matUtils can automatically determine the sample date if it as appended to the sample name with the pipe (|) character (e.g., "USA/CA-CZB-9556/2020|MW483159.1|2020-04-13"). If your sample names don't follow this naming convention, you can use the -d option to specify sample dates.
* -x: Comma-separated list of additional metadata fields to include in Taxonium protobuf. Default is 'cluster,region'. Use the name of the field in the metadata file. Do not separate items with spaces.
* -t: sets the number of threads to use when calling matUtils introduce; the default is 4.
* -X: Number to pass to parameter -X of matUtils introduce. Increase to merge nested clusters; the default is 2.
* -e: In our implementation for CDPH we use two sets of geojson files to handle two levels of geographic analysis, one at the county level and one at the state level. To differentiate the two sets of files we implemnted the -e option to append a filename "extension" to the second set of files, e.g., "default_clusters.tsv" for the county level analysis and "default_clusters**_us**.tsv" for the state level analysis. In this case you would use the -e paramater with "_us" as the parameter value. The default is to use no filename extension.

Note that the geojson parameter, -j, can take multiple arguments if you need to create a multi-geographic-level analysis, as we did for CDPH. If you use more than one geojson file, be sure to specify file name extensions using the -e parameter noted above.

Outputs:
* The primary data outputs contaning the calculated introductions are hardcoded_clusters.tsv (tab separated file with detailed cluster and introduction information) and cview.jsonl.gz (file for viewing introductions with Taxonium).
* The following set of files are used in the web site:
  * regions.js: This file supplies the geojson data to the Leaflet map (via the introData variable).
  * cluster_data.json.gz: This JSON-formateed file supplies the data table below the map with basic cluster information; it is pre-sorted by growth score. (The growth score is the number of samples in the cluster divided by the cluster's observed time frame; see the [matUtils introduce documentation](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce) for details.) 
  * sample_data.json.gz: This JSON-formateed file supplies the data table below the map with the sample names (and specimen IDs for CDPH data) in the final column(s) of the data table.

4. If you are not working from the example/data directory, you will need to copy regions.js, the display_tables folder, cview.jsonl.gz, and hardcoded_clusters.tsv into the directory where your web site files are located. We suggest grouping these files in a data folder. Our example web site has the following structure:
* index.html: the HTML code for the app
* css: contains the style sheet for the site
* data: contains the above mentioned data files
* lib: contains the JS libraries used in the app: Leaflet JS, SlickGrid, jQuery, and jQueryUI
* scripts: contains the JS files that power the Leaflet map (main.js) and the table (datagrid.js).

5. Assuming you are working from the the example/data directory, navigate up one level to the example root directory (or the root directory of your website) and run 
```
python3 -m http.server
```

**Customizations to the Cluster Table Below the Map:** Cluster Tracker uses the highly-customizeable [SlickGrid](http://slickgrid.net/) JS library to display cluster information below the map. Customizations to the table can be achieved by modifying scripts/datagrid.js; you may wish to consult the SlickGrid documentation for details. 

Our version for CDPH includes additional fields in the cluster table that are not automatically generated from matUtils introduce. To do likewise, you will need to modify the datagrid.js file to insert additional columns of data (the setCols function specifies column parameters) and modify how the data is read and assignd to the SlickGrid DataView object. 

**Customizing the Map--Basics:** We use [Leaflet.js](https://leafletjs.com/) for our mapping app, and largely built upon their [Interactive Choropleth Map example](https://leafletjs.com/examples/choropleth/). The scripts/main.js file is where you will find all the Leaflet map functions. Some common basic modifications you may wish to make:
* The map center and extent is set via the Leaflet [setView](https://github.com/pathogen-genomics/introduction-website/blob/756310ec0d81e575aa5348a9949d499bcdc733a4/src/js/main.js#L1) method in main.js.
* The color scale is set using the [map_colors parameter](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L6) variable the [legend_log](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L385-L395) variable in main.js.
* Color scale cut points can be modified in the [getColor* methods](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L28-L70) and in the [getBinVals and getLegendBins methods](https://github.com/pathogen-genomics/introduction-website/blob/ec47a523eafcefa031e5d1f47cfff8ca87e8e590/src/js/main.js#L328-L379) in main.js

**Customizing the Map--Advanced:** Additional map customizations can be found in our customization for CDPH, located in the dist folder. Of interest, we developed a toggle that can switch between a county-based view of introducions and a larger state-based view of introductions. This can be achieved by using Leaflet's Layer method.

**Additional Notes:** Modern browsers tend to cache files to make loading the website quicker. If your data files will be updated with regularity you may want to consider setting up your server so that it prevents cacheing.
