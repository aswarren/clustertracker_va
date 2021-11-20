# Calfornia Big Tree Cluster-Tracker
Code to generate a webpage displaying SARS-CoV-2 clusters and introductions inferred via [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce). Data for counties in the state of California and and for U.S. states are displayed on a map and in a table, with links to view and explore the data in Taxonium and the California Big Tree Investigator. This version is a customizaton for use with data produced from the Calfornia Big Tree; the original Cluster-Tracker project can be found at https://github.com/jmcbroome/introduction-website(https://github.com/jmcbroome/introduction-website). 

A python script and a number of data files are required to preprocess the data (described below).

## Quickstart

This site uses python to perform backend setup and vanilla javascript for website rendering. You will need to have the [UShER software suite](https://usher-wiki.readthedocs.io/en/latest/Installation.html) installed and available on your path. This site was built with UShER version 0.5.0; earlier versions of UShER may not function as anticipated. The python "dateutil" package is required. Some versions of python may be missing the dateutil standard package; it can be installed if needed via conda.

Input data files:
- CA Big Tree MAT protobuf file (compatible with [UShER](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#the-mutation-annotated-tree-mat-protocol-buffer-pb))
- Metadata file #1 describing public and GISAID data, in TSV format.
  - The first line of the file should be a header with the following columns: strain, genbank_accession,date, country, host, completeness, length, Nextstrain_clade, pangolin_lineage, Nextstrain_clade_usher, pango_lineage_usher
- Metadata file #2 describing Calfornia county data, in TSV format. 
  - The first line of the file should be a header with the following columns: usherID, name, pango_lineage, nextclade_clade, gisaid_accession, county, collection_date, paui, sequencing_lab
- Gene annotation GTF file 
  - (e.g., ncbiGenes.gtf, can be downloaded [here](https://usher-wiki.readthedocs.io/en/latest/_downloads/2052d9a7147253e32a3420939550ac63/ncbiGenes.gtf))
- FASTA reference sequence file 
  - (e.g., NC_045512v2.fa, can be downloaded [here](https://raw.githubusercontent.com/yatisht/usher/5e83b71829dbe54a37af845fd23d473a8f67b839/test/NC_045512v2.fa)) to produce a Taxonium view

Instructions:
1. Clone this repository into your workspace of choice.
2. Acquire the input data files and store in a directory that can be accesed from your workspace.
3. Navigate to the "data" directory of this cloned repo, and run "prepare_county_data.py" with the files obtained above, ala the below.

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

## Further Details: Data Processing and What the Python Scripts Do

### /data/prepare_county_data.py 

This script pre-processes the data and is a wrapper for the primary pipeline script (/data/master_backend.py). Its main functions are to merges the two metadata formats, sorts out unusable samples (those that cannot be attributed to a US state, don't have valid dates or don't have valid Calif. county names), and uses this list to extract usable samples from the original protobuf. It then runs the "master_backend" python script, which computes the introductions.

Files generated:
- clean.pb: 
  - MAT protobuf filtered to exclude unusable samples and samples outside the US. Required for input into "master_backend.py"
- metadata_merged.tsv: 
  - Metadata file containing only the usable samples, created by combining metadata file #1 (public+GISAID metadata) and file #2 (CA county metadata). Required for input into "master_backend.py".
- sample_regions.tsv: 
  - Stores the associations between the sample ID and the region name. Required for input into "master_backend.py"; important for matUtils introduce.
- unlabeled_samples.txt: 
  - List of rejected samples, useful for debugging.

### /data/master_backend.py

This script takes the cleaned protobuf file generated above and uses [matUtils introduce](https://usher-wiki.readthedocs.io/en/latest/matUtils.html#introduce) to calculate the number of new introductions of the virus genome into each geographic region (in this case, all counties in California plus all U.S. States). It then generates a series of data tables for use in the web app, and creates a protobuf suitable for viewing in Taxonium.

Primary data output files:
- hardcoded_clusters.tsv: 
  - Output from matUtils introduce containing information for all the clusters.
- cview.pb: 
  - Final output protobuf of clusters, suitable for viewing in Taxonium.

Output files for the UI and map:
- region.js: 
  - This is the geoJSON file that is displayed in the Leaflet map, with all cluster counts and introductions.
- display_tables/[region_name]_topclusters.tsv: 
  - Extracts the top 100 clusters from each region for quick display in the data table below the map.

Misc. data output files:
- clusterswapped.tsv: adds cluster ID field, "region" field, fills in blank values as needed

## Customizing Cluster-Tracker: The Pipeline and More Explanation

To generate a website for your set of regions of interest, [you will first need to obtain a geojson representing your regions of interest.](https://geojson-maps.ash.ms). You will need to generate a sample-region two-column tsv, with sample identifiers in the first column and the ID of the region they are from in the second column. You will need what I'm calling a "lexicon" file to ensure compatibility between names- this is an unheaded csv containing in the first column the base name of each region to be used by the map, and comma separated after that, each other name for that region across your other files. An example is provided under data/state_lexicon.txt.

Once you've obtained these files, you can navigate to the data directory and run

```
python3 master_backend.py -i path/to/your.pb -m path/to/matching/metadata.tsv -f path/to/NC_045512v2.fa -a path/to/ncbiGenes.gtf -j path/to/your/geo.json -s path/to/your/sample_regions.tsv -l path/to/your/lexicon.txt -H web/accessible/link/to/index/directory
gzip cview.pb
```

You can optionally pass -G or -X parameters, which will be applied when introduce is called. 

Then navigate to the outermost index directory and run 
```
python3 -m http.server
```

It is not required to make the website on a web-accessible directory, but the taxonium view (clicking view cluster on the site) will not function if it's not. You can work around this by uploading the cview.pb / cluster_taxonium.pb that is output by the pipeline directly to [taxonium](https://cov2tree.org/), then search for your cluster of interest from the website table using the search box on the resulting display. 
