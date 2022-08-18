# Changelog

## v0.6.0 (2022-08-17):
   - UI changes: Imlments a new data display table via SlickGrid library; allows for filtering via Search box, sort column by ascending/descending order, mulitple column sort, highlight and copy a range of cells, column width adjustment, user-adjustable pagination options, and popups to display truncated cell text
   - UI changes: Data for data display table is supplied by two JSON files that represent the full data set
   - UI changes: Adds cluster sample names and CDPH specimen_IDs to the data table
   - UI changes: Users can search the data table for sample names/CDPH specimen_IDs in addition to cluster information
   - UI changes: Modification to table header and hover text to clarify inferred origin and inferred origin confidence
   - Data processing: Removes filtering of protobuf to US-only samples
   - Data processing: Replaces "top_clusters" files with a set of two JSON files, one for the basic cluster information, and one for sample names and CDPH specimen_IDs
   - Data processing: New JSON data format for links to CA Big Tree Investigator
   - Data processing: Adds flag in python scripts to indicate when data processing is via WDL Task or command line
   - Data processing: Adds flag in python script to better handle custom CA Big Tree data processing requirements
   - Data processing: moves the host URL variable to the index.html file
## v0.5.0 (2022-07-21):
   - Updates to use new Taxonium v.2 viewer
   - Data processing: updates utils.py to better handle complex file names
## v0.4.3 (2022-07-12):
   - move/reformat version history to changelog
   - upgraded datatables.net from 1.10.25 to 1.11.3 to resolve security vulnerabilities
## v0.4.2 (2022-06-22):
   - Data processing: incorporates new specimen_accession_number field for CDPH metadata
## v0.4.1 (2022-04-07):
   - updates UI to download uncompressed version of hardcoded_clusters.tsv
## v0.4.0 (2022-03-22):
  - Data processing: adds new California state-wide introductions data
  - UI changes: adds new button to show/hide California state region introductions and rearranges other buttons
  - Data processing: handles new specimen_id field in metadata (replaces paui/link_id)
## v0.3.1 (2022-03-02):
  - UI changges: adds an "Update in progress message" when data transfer is in progress.
  - UI changes: turns the raw cluster count vs. log-fold enrichment drop-down into a toggle button.
  - uses cache busting to prevent caching of JS and data files
  - loads local copy of jquery if can't connect to CDN
## v0.3 (2022-02-02):
  - UI changes: adds option to show introductions by raw numbers
  - UI changes: displays the number of CDPH samples for viewing in Investigator in the data table
  - Data processing: fixes metadata processng errors when splitting and stripping lines with missing metadata fields
  - Data processing: accomodates new CDC sequence file naming convention
## v0.2.3 (2022-01-20): 
  - UI changes: add links in data display table to CA Big Tree Investigator
  - update text in intro paragraph
## v0.2.2 (2022-01-04): 
  - refine input to matUtils introduce to optimize processing
  - UI update to differentiate download links
## v0.2.1 (2021-12-22): 
  - fixed issue with missing or incorrect cluster dates 
  - added clade information to Taxonium protobuf
  - use more stable jquery CDN
## v0.2.0 (2021-12-17): 
  - UI changes: removed links in data display table to CA Big Tree Investigator
