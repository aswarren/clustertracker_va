import subprocess
from master_backend import primary_pipeline, read_lexicon, parse_setup
from master_backend import validate_geojson

#This script is a wrapper around the primary pipeline script
#which does all necessary preprocessing to generate the setup for a California county analysis.
args = parse_setup()
#get list of allowable values for county names. 
conversion = read_lexicon(args.lexicon)
pbf = args.input
metadatafile = args.metadata

valid = validate_geojson(args.geojson)
print(valid)

# get list of samples without valid county names
badsamples = open("unlabeled_samples.txt","w+")
with open(metadatafile) as inf:
    with open("sample_regions.tsv","w+") as outf:
        for entry in inf:
            county = entry.split("\t")[5].strip()
            if county != "":
                #check if county is in lexicon
                if county.upper() in (c.upper() for c in conversion): # convert all names to uppercase to avoid differences in case
                    sample = entry.split("\t")[0].strip()
                    print(sample + "\t" + conversion[county], file = outf)
                else:
                    print(entry.strip(), file = badsamples)
                    print(entry) #debug
            else:
                print(entry.strip(), file = badsamples)
badsamples.close()

# creat a new MAT file without the samples that couldn't be identified with valid county name
print("Clearing out unparseable county samples.")
# extract form input pbf only the samples listed in the sample file
subprocess.check_call("matUtils extract -i " + pbf + " -s sample_regions.tsv -o clean.pb", shell = True)
#update the arguments parsed
args.input = "clean.pb"
args.sample_regions = "sample_regions.tsv"
if args.geojson == "":
    args.geojson = "gz_2010_us_050_00_5m.json"
print("Starting main pipeline.")
primary_pipeline(args)
