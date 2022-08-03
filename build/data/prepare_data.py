# This script is a wrapper around the primary pipeline script
# which does all necessary preprocessing to generate files for a
# multi-source analysis using both public SARS-CoV-2 sequences and
# sequences from the CA Dept of Public Health (CDPH) CovidNet.
# 
# The series of python scripts that this workflow uses has been
# optimized to be compatible with WDL tasks in Terra.
#
# Input files for the California Big Tree Cluster Tracker consist of
# one mutation-annotated tree in protobuf format, and two
# metadata files (one for the public data and one for CDPH data).
#
# This script can generate two sets of files from the same input
# data by feeding in two GeoJSON files.
# 
#   Files you will need to have set up prior to running this script:
#     -Lexicon with variations on state or county names
#     -GeoJSON file(s) tailored to your geography; geographic names must be 
#        consistent with names in Lexicon
#
#   Overview of processing steps:
#     (1) Process metadata file(s) to filter out unusable samples, and, 
#         if needed, merge multiple metadata files into one.
#     (2) Use merged metadata file to filter samples from protobuf file.
#     (3) Run the primary pipeline
#
# Example command line usage:
# python3 prepare_data.py -i new_tree.pb -m samplemeta.tsv public.plusGisaid.latest.metadata.tsv 
#  -a hu1.gb -j us-states_ca-counties.geo.json us-states.geo.json 
#  -e "_us" -l state_and_county_lexicon.txt -H https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/
#  -x "genbank_accession,gisaid_accession,country,county,date,name,pangolin_lineage,nextclade_clade,specimen_id,specimen_accession_number,sequencing_lab"
#
#------------------------------------------------------------------------------------------

import subprocess, sys, re, os
#set path to directory
sys.path.insert(1, os.path.join(os.path.abspath(__file__ + "/../../../"), "src/python/"))
from master_backend import primary_pipeline, parse_setup
from utils import validate_geojson
from process_metadata import process_metadata

#get arguments and assign variable names
args = parse_setup()
pbf = args.input
#--------------------------------------------------------------

# Step 1: Process metadata file(s)
print("Processing metadata file(s)")
process_metadata(args.lexicon, args.metadata, args.region_extension)
#--------------------------------------------------------------

# Step 2: Run the primary pipeline
#update the arguments parsed
args.metadata = "metadata_merged.tsv"
args.sample_regions = "sample_regions.tsv"
args.date_metadata = "sample_dates.tsv"
print("Starting main pipeline.")
primary_pipeline(args)
