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

# check that GeoJSON file is formatted as required
if validate_geojson(args.geojson) != 1:
    print("GeoJSON file DOES NOT have 'name' field")
    sys.exit()

# reformat metadata file to be compatible with Taxonium requirements
# sort usable samples from metadata file
nbad = 0
ngood = 0
new_metadf = open("metadata_taxonim.txt","w+") # metadata file formatted for Taxonium
badsamples = open("unlabeled_samples.txt","w+") # list of samples w/o valid county names
with open(metadatafile) as inf:
    with open("sample_regions.tsv","w+") as outf:
        i = 0
        for entry in inf:
            fields = entry.strip().split("\t")
            
            # format metadata
            if i == 0:
                fields[0] = "strain" # ename "usherID" field
                fields[2] = "pangolin_lineage" # rename "pango_lineage" field
                fields[6] = "date" # rename "collection_date" field
                fields.append("genbank_accession") # needed for Taxonium
                fields.append("country") # needed for Taxonium
            else:
                fields.append("")
                fields.append("USA")
            print("\t".join(fields),file=new_metadf)

            # sort good/bad samples
            county = fields[5]
            if county != "":
                #check if county is in lexicon
                if county.upper() in (c.upper() for c in conversion): # convert all names to uppercase to avoid differences in case
                    sample = entry.split("\t")[0].strip()
                    print(sample + "\t" + conversion[county], file = outf)
                    ngood += 1
                else:
                    print(entry.strip(), file = badsamples)
                    nbad += 1
            else:
                print(entry.strip(), file = badsamples)
                nbad += 1
            i += 1
badsamples.close()
new_metadf.close()
print(f"{ngood} parseable samples found in the region; {nbad} samples ignored")

# creat a new MAT file without the samples that couldn't be identified with valid county name
print("Clearing out unparseable county samples.")
# extract form input pbf only the samples listed in the sample file
subprocess.check_call("matUtils extract -i " + pbf + " -s sample_regions.tsv -o clean.pb", shell = True)
#update the arguments parsed
args.input = "clean.pb"
args.metadata = "metadata_taxonim.txt"
args.sample_regions = "sample_regions.tsv"

print("Starting main pipeline.")
primary_pipeline(args)
