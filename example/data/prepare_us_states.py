#This script is a wrapper around the primary pipeline script
#which does all necessary preprocessing to generate the setup for a united states analysis.
#
# Example command line usage:
# python3 prepare_us_states.py -i public-latest.all.masked.pb -m public-latest.metadata.tsv
# -H http://websitename -f NC_045512v2.fa -a ncbiGenes.gtf -l state_lexicon.txt
#--------------------------------------------------------------

import sys, os, subprocess
#set path to directory
sys.path.insert(1, os.path.join(os.path.abspath(__file__ + "/../../../"), "src/python/"))
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

#Step 2: Use excluded samples to filter useable samples from protobuf file
print("Clearing out unparseable samples.")
subprocess.check_call("matUtils extract -i " + pbf + " -s unlabeled_samples.txt -p -o clean.pb", shell = True)
#--------------------------------------------------------------

#Step 3: Run the primary pipeline
#update the arguments parsed
args.input = "clean.pb"
args.sample_regions = "sample_regions.tsv"
args.geojson = "us-states.geo.json"
print("Starting main pipeline.")
primary_pipeline(args)