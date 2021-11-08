import subprocess, sys, re
from master_backend import primary_pipeline, read_lexicon, parse_setup
from master_backend import validate_geojson

# This script is a wrapper around the primary pipeline script
# which does all necessary preprocessing to generate the setup for a 
# California county + U.S. state analysis. 
#   Files you will need to have set up:
#     -Lexicon with variations on state or county names
#     -GeoJSON file tailored to your geography; geographic names must be consistent with names in Lexicon
#   Processing steps:
#     (1) Process metadata file(s)
#         -ensure required field names exist
#         -remove non-US samples from public metadata
#         -remove California samples from public metadata since county is unknown
#         -For California metadata file, remove samples w/o a valid county name
#         -Handle cases where county matches a state name (e.g., "Nevada")
#         -remove samples without a valid date (YYYY-MM-DD)
#         -merge public and California-specific metadata files, adding/renaming fields as necessary
#         -create file to store sample name/region association
#     (2) Use merged metadata file to filter samples from protobuf file
#     (3) Run the primary pipeline

#get arguments and assign variable names
args = parse_setup()
pbf = args.input

#read lexicon to get list of allowable values for state/county names. 
conversion = read_lexicon(args.lexicon)
#list of U.S. counties witht the same name as a state
county_state = {"Washington","Delaware","Wyoming","Ohio","Nevada","Mississippi","Texas","Iowa","Oklahoma","Utah","Indiana","Colorado","Arkansas","Idaho","Oregon","Hawaii","New York"}

# check that GeoJSON file is formatted as required
if validate_geojson(args.geojson) != 1:
    print("GeoJSON file DOES NOT have 'name' field")
    sys.exit()

#Step 1: Process metadata file(s)
mfiles = args.metadata.split(",") #get names of metadata files
metadata = open("metadata_merged.tsv","w+") #output file for merged metadata
badsamples = open("unlabeled_samples.txt","w+") # file for rejected sample names
region_assoc = open("sample_regions.tsv","w+") # file to store associations between sample ID and region name
date_pattern = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
#write metadata header
print("strain\tname\tpangolin_lineage\tnextclade_clade\tgisaid_accession\tcounty\tdate\tpaui\tsequencing_lab\tgenbank_accession\tcountry", file = metadata)
for f in mfiles:
    with open(f) as inf:
        fields = inf.readline().strip().split("\t")
        # check which format the metadata is in based on header field names
        if fields[0] == "usherID":
            # CA metadata header: usherID,name,pango_lineage,nextclade_clade,gisaid_accession,county,collection_date,paui,sequencing_lab
            for entry in inf:
                fields = entry.strip().split("\t")
                # check for valid California county names
                county = fields[5]
                if county != "":
                    #check if county is in lexicon
                    if county.upper() in (c.upper() for c in conversion): # convert all names to uppercase to avoid differences in case
                        #check for valid date
                        if re.search(date_pattern, fields[6]):
                            #add item to merged metadata file
                            fields.append("")
                            fields.append("USA")
                            print("\t".join(fields), file = metadata)
                            #add sample ID and county name to sample regions file
                            if county in county_state: #handle cases where county name matches state name
                                print(fields[0] + "\t" + county + " County", file = region_assoc)
                            else:
                                print(fields[0] + "\t" + conversion[county], file = region_assoc)
                        else:
                            print(fields[0], file = badsamples) #does not have a valid date
                    else:
                        print(fields[0], file = badsamples) #not a valid CA county
                else:
                    print(fields[0], file = badsamples) #sample does not have county
        else:
            # public metadata header: strain,genbank_accession,date,country,host,completeness,length,Nextstrain_clade,pangolin_lineage,Nextstrain_clade_usher,pango_lineage_usher
            for entry in inf:
                fields = entry.strip().split("\t")
                country = fields[0].split("/")[0]
                # check for US samples
                if country == "USA":
                    state = fields[0].split("/")[1].split("-")[0]
                    if state in conversion:
                        #TO DO - assign California samples a county via naming scheme
                        if state == "CA":
                            #sample is from California; reject
                            print(fields[0], file = badsamples)
                        else: 
                            #check for valid date
                            if re.search(date_pattern, fields[2]):
                                #add item to merged metadata file
                                newfields = []
                                newfields.append(fields[0]) #sample name
                                newfields.append("") #CDPH name
                                newfields.append(fields[8]) #pangolin_lineage
                                newfields.append(fields[7]) #nextclade_clade = Nextstrain_clade
                                newfields.append("") #gisaid_accession
                                newfields.append("") #county name
                                newfields.append(fields[2]) #date
                                newfields.append("") #paui
                                newfields.append("") #sequencing_lab
                                newfields.append(fields[1]) #genbank_accession
                                newfields.append("USA") #country
                                print("\t".join(newfields), file = metadata)
                                #add sample ID and state name to sample regions file
                                print(fields[0] + "\t" + conversion[state.upper()], file = region_assoc)
                            else:
                                print(fields[0], file = badsamples) #does not have a valid date
                    else:
                        #can't parse state
                        print(fields[0], file = badsamples)
                elif entry.startswith("CDPH"): 
                    #sample is from California; reject
                    print(fields[0], file = badsamples)
                else:
                    #non-US sample
                    print(fields[0], file = badsamples)

metadata.close()
badsamples.close()
region_assoc.close()

# Step 2: Use merged metadata file to filter samples from protobuf file
print("Clearing out unparseable samples.")
# extract form input pbf only the samples listed in the merged metadata file
subprocess.check_call("matUtils extract -i " + pbf + " -s metadata_merged.tsv -o clean.pb", shell = True)

# Step 3: Run the primary pipeline
#update the arguments parsed
args.input = "clean.pb"
args.metadata = "metadata_merged.tsv"
args.sample_regions = "sample_regions.tsv"
print("Starting main pipeline.")
primary_pipeline(args)
