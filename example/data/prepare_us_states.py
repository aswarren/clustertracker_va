# This script is a wrapper around the primary pipeline script.
# It does all necessary preprocessing of the global public SARS-CoV-2 phylogenetic tree
# (https://hgdownload.soe.ucsc.edu/goldenPath/wuhCor1/UShER_SARS-CoV-2/) and generates 
# all files needed to calculate introductions into each U.S. state.
#
# Example command line usage:
# python3 prepare_us_states.py -i public-latest.all.masked.pb -m public-latest.metadata.tsv
# -a hu1.gb -l state_lexicon.txt -j us-states.geo.json -r 0
# -x “date,country,name,Nextstrain_clade_usher,pango_lineage_usher”
#--------------------------------------------------------------

import subprocess
from master_backend import primary_pipeline, parse_setup
from utils import read_lexicon

#--------------------------------------------------------------
#Step 1: Process metadata file
print("Processing metadata file")
args = parse_setup()
conversion = read_lexicon(args.lexicon)
pbf = args.input
subprocess.check_call("matUtils extract -i " + pbf + " -u samplenames.txt",shell=True)
badsamples = open("unlabeled_samples.txt","w+")
with open("samplenames.txt") as inf:
    with open("sample_regions.tsv","w+") as outf:
        for entry in inf:
            country = entry.split("/")[0]
            if country == "USA":
                state = entry.split("/")[1].split("-")[0]
                if state in conversion:
                    print(entry.strip() + "\t" + conversion[state.upper()], file = outf)
                else:
                    print(entry.strip(), file = badsamples)
badsamples.close()
#--------------------------------------------------------------

#Step 2: Prune the protobuf file to include only US samples.
# Notes: this step is optional. Skip this step if you would like to create a global phylogenetic tree.
# If you decide to use the full global phylogenetic tree, we recommend setting up your own Taxonium
# backend, as very large trees may cause Taxonium to bog down.
print("Clearing out unparseable samples.")
subprocess.check_call("matUtils extract -i " + pbf + " -s unlabeled_samples.txt -p -o clean.pb", shell = True)
#--------------------------------------------------------------

#Step 3: Run the primary pipeline
#update the arguments parsed
args.input = "clean.pb" #comment this line out if you are skipping step 2.
args.sample_regions = "sample_regions.tsv"
print("Starting main pipeline.")
primary_pipeline(args)