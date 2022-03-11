import subprocess, sys, re
from master_backend import primary_pipeline, read_lexicon, parse_setup
from master_backend import validate_geojson
from process_metadata import process_metadata

# This script is a wrapper around the primary pipeline script
# which does all necessary preprocessing to generate the setup for a 
# California county + U.S. state analysis. 
#   Files you will need to have set up:
#     -Lexicon with variations on state or county names
#     -GeoJSON file tailored to your geography; geographic names must be consistent with names in Lexicon
#   Processing steps:
#     (1) Process metadata file(s)
#     (2) Use merged metadata file to filter samples from protobuf file
#     (3) Run the primary pipeline

#get arguments and assign variable names
args = parse_setup()
pbf = args.input

# check that GeoJSON file is formatted as required
if validate_geojson(args.geojson) != 1:
    print("GeoJSON file DOES NOT have 'name' field")
    sys.exit()

#Step 1: Process metadata file(s)
#read lexicon to get list of allowable values for state/county names. 
conversion = read_lexicon(args.lexicon)
process_metadata(conversion, args.metadata)

# Step 2: Use merged metadata file to filter samples from protobuf file
print("Clearing out unparseable samples.")
# extract from input pbf only the usable samples
# regions as counties
subprocess.check_call("matUtils extract -i " + pbf + " -s sample_regions.tsv -o clean.pb", shell = True)
#regions as states
subprocess.check_call("matUtils extract -i " + pbf + " -s sample_regions_us.tsv -o clean_us.pb", shell = True)

# Step 3: Run the primary pipeline
#update the arguments parsed
args.input = "clean.pb"
args.metadata = "metadata_merged.tsv"
args.sample_regions = "sample_regions.tsv"
args.date_metadata = "sample_dates.tsv"
print("Starting main pipeline.")
primary_pipeline(args)
