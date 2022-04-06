# This script takes one or more metadata files and filters out samples that don't
#   match geographic names specified in a lexicon of place names. Use the lexicon
#   to store alternate spellings or capitalizatons of place names.
#   This script also creates files necessary for two regional analysis (one at the
#   CA county level and one at the US state level).
#
#   Arguments:
#      -lexiconfile: name of file with lexicon of place names
#      -metadatafiles: list of metadata files
#   Output files:
#      -metadata_merged.tsv: combined metadata file for both CDPH and public samples for the county analysis
#      -metadata_merged_us.tsv: combined metadata file for both CDPH and public samples for the state analysis
#      -sample_regions.tsv: list of sample names and corresponding regions for the county analysis
#      -sample_regions_us.tsv: list of sample names and corresponding regions for the state analysis
#      -sample_dates.tsv: list of sample names and corresponding dates for the county analysis
#      -sample_dates_us.tsv: list of sample names and corresponding dates for the state analysis
#      -pids.tsv: list of sample names and corresponding sample IDs/PAUIs for the county analysis
#      -pids_us.tsv: list of sample names and corresponding sample IDs/PAUIs for the state analysis
#   Processing overview:
#      -removes samples without a valid date (YYYY-MM-DD)
#      -removes samples w/o a valid county name from CDPH metadata (county analysis only)
#      -handles cases where county name matches a state name (e.g., "Nevada")
#      -removes California samples from public metadata (county analysis only)
#      -removes non-US samples from public metadata
#      -merges public and California-specific metadata files, adding/renaming fields as necessary
#      -creates file(s) to store sample name and region association
#      -creates file(s) to store sample name and date if date is not part of file name
#      -creates file(s) to store sample name and PAUI/Specimen ID
#
# Example command line usage:
#   python3 process_metadata.py -m samplemeta.tsv public.plusGisaid.latest.metadata.tsv -l state_and_county_lexicon.txt
#-------------------------------------------------------------

import sys, re
import os #comment out for WDL
#set path to directory 
sys.path.insert(1, os.path.join(os.path.abspath(__file__ + "/../../../"), "src/python/")) #comment out for WDL
from utils import read_lexicon #comment out for WDL


def process_metadata(lexiconfile, metadatafiles, extension=["_us"]):
    #list of U.S. counties witht the same name as a state
    county_state = {"Washington","Delaware","Wyoming","Ohio","Nevada","Mississippi","Texas","Iowa","Oklahoma","Utah","Indiana","Colorado","Arkansas","Idaho","Oregon","Hawaii","New York"}
    
    #for WDL: insert here read_lexicon function from utils.py

    conversion = read_lexicon(lexiconfile) #comment out for WDL, replace with file variable
    
    #get names of metadata files; CDPH metadata file should come first, public Gisaid metadata file should come second
    mfiles = metadatafiles #comment out for WDL, replace with file variable

    #assign file name extension for outputting files for both CA county and CA state analysis
    if extension is None: #comment out this block for WDL, replace with: ext = "_us"
        ext = "_us"
    else:
        ext = extension[0]

    metadata = open("metadata_merged.tsv","w+") #output file for merged metadata, for US + CA county analysis
    metadata_us = open("metadata_merged" + ext + ".tsv","w+") #output file for merged metadata, for US analysis
    badsamples = open("unlabeled_samples.txt","w+") # file for rejected sample names
    region_assoc = open("sample_regions.tsv","w+") # file to store associations between sample ID and region name, for US + CA county analysis
    region_assoc_us = open("sample_regions" + ext + ".tsv","w+") # file to store associations between sample ID and region name, for US analysis
    date_file = open("sample_dates.tsv","w+") # file to store associations between sample ID and sample dates, for US + CA county analysis
    date_file_us = open("sample_dates" + ext + ".tsv","w+") # file to store associations between sample ID and sample dates, for US analysis
    print("sample_id\tdate", file = date_file)
    print("sample_id\tdate", file = date_file_us)
    pid_assoc = open("pids.tsv","w+") # file to store associations between sample ID and specimen_id (formerly PAUI or link_id)
    pid_assoc_us = open("pids" + ext + ".tsv","w+") # file to store associations between sample ID and specimen_id (formerly PAUI or link_id)
    date_pattern = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    #write metadata header
    print("strain\tname\tpangolin_lineage\tnextclade_clade\tgisaid_accession\tcounty\tdate\tpaui\tsequencing_lab\tspecimen_id\tgenbank_accession\tcountry", file = metadata)
    print("strain\tname\tpangolin_lineage\tnextclade_clade\tgisaid_accession\tcounty\tdate\tpaui\tsequencing_lab\tspecimen_id\tgenbank_accession\tcountry", file = metadata_us)
    duplicates = set() #stores sample names of potential duplicates
    for f in mfiles:
        with open(f) as inf:
            fields = inf.readline().strip().split("\t")
            # check which format the metadata is in based on header field names
            if fields[0] == "usherID":
                # CA metadata header: usherID,name,pango_lineage,nextclade_clade,gisaid_accession,county,collection_date,paui,sequencing_lab,specimen_id
                for entry in inf:
                    fields = entry.split("\t")
                    for i in range(len(fields)):
                        fields[i] = fields[i].strip()
                    county = fields[5]
                    #check for valid date
                    if re.search(date_pattern, fields[6]):
                        #add sample name if needed to check for duplicates later on
                        if fields[0].startswith("USA/CA"):
                            duplicates.add(fields[0])
                        fields.append("")
                        fields.append("USA")
                        #add item to merged metadata file for CA state analysis
                        print("\t".join(fields), file = metadata_us)
                        #assign to CA state in region file
                        print(fields[0] + "\tCalifornia", file = region_assoc_us)
                        #if non-standard sample name, add sample ID and date to sample dates file
                        if not (fields[0].startswith("USA/")):
                            print(fields[0] + "\t" + fields[6], file = date_file_us)
                        #add Specimen ID/PAUI to association file
                        if fields[9] != "":
                            print(fields[0] + "\t" + fields[9], file = pid_assoc_us)
                        # check for valid California county names for County specific data processing
                        if county != "":
                            #check if county is in lexicon
                            if county.upper() in (c.upper() for c in conversion): # convert all names to uppercase to avoid differences in case
                                #add item to merged metadata file
                                print("\t".join(fields), file = metadata)
                                #add sample ID and county name to sample regions file
                                if county in county_state: #handle cases where county name matches state name
                                    text = county.replace(" ", "_") + "_County"
                                else:
                                    text = conversion[county].replace(" ", "_")
                                print(fields[0] + "\t" + text, file = region_assoc)
                                #if non-standard sample name, add sample ID and date to sample dates file
                                if not (fields[0].startswith("USA/")):
                                    print(fields[0] + "\t" + fields[6], file = date_file)
                                #add Specimen ID/PAUI to association file
                                if fields[9] != "":
                                    print(fields[0] + "\t" + fields[9], file = pid_assoc)
                    else:
                        print(fields[0], file = badsamples) #does not have a valid date        
            else:
                # public metadata header: strain,genbank_accession,date,country,host,completeness,length,Nextstrain_clade,pangolin_lineage,Nextstrain_clade_usher,pango_lineage_usher
                for entry in inf:
                    fields = entry.strip().split("\t")
                    country = fields[0].split("/")[0]
                    # check for US samples
                    if country == "USA":
                        state = fields[0].split("/")[1].split("-")[0]
                        if state in conversion:
                            #check for valid date
                            if re.search(date_pattern, fields[2]):
                                #first check for CA state duplicates
                                if (state == "CA") and (fields[0] in duplicates):
                                    print(fields[0], file = badsamples)
                                else:
                                    #add item to merged metadata file
                                    newfields = []
                                    newfields.append(fields[0]) #sample name
                                    newfields.append("") #CDPH name
                                    newfields.append(fields[8]) #pangolin_lineage
                                    newfields.append(fields[7]) #nextclade_clade = Nextstrain_clade
                                    newfields.append("") #gisaid_accession
                                    newfields.append("") #county name
                                    newfields.append(fields[2]) #date
                                    newfields.append("") #Link ID (PAUI)
                                    newfields.append("") #sequencing_lab
                                    newfields.append("") #specimen_id
                                    newfields.append(fields[1]) #genbank_accession
                                    newfields.append("USA") #country
                                    print("\t".join(newfields), file = metadata_us)
                                    #add sample ID and state name to sample regions file
                                    text = conversion[state.upper()].replace(" ", "_")
                                    print(fields[0] + "\t" + text, file = region_assoc_us)
                                    #TO DO - assign California samples a county via naming scheme
                                    #filter out CA samples for CA county analysis
                                    if state != "CA":
                                        print("\t".join(newfields), file = metadata)
                                        print(fields[0] + "\t" + text, file = region_assoc)
                            else:
                                print(fields[0], file = badsamples) #does not have a valid date   
                        else:
                            #can't parse state
                            print(fields[0], file = badsamples)
                    else:
                        #non-US sample
                        print(fields[0], file = badsamples)
    metadata.close()
    badsamples.close()
    region_assoc.close()
    date_file.close()
    pid_assoc.close()
    metadata_us.close()
    region_assoc_us.close()
    date_file_us.close()
    pid_assoc_us.close()

if __name__ == "__main__":
    from master_backend import parse_setup
    args = parse_setup()
    if args.region_extension is None:
        extension = ["_us"]
    else:
        extension = args.region_extension
    process_metadata(args.lexicon, args.metadata, extension)