# This script takes one or more metadata files and filters out samples that don't
#   match geographic names specified in a lexicon of place names. Use the lexicon
#   to store alternate spellings or capitalizatons of place names.
#   This script also creates files necessary for two regional analysis (one at the
#   CA county level and one at the US state level).
#
#   Arguments:
#      -lexiconfile: name of file with lexicon of place names
#      -metadatafiles: list of metadata files (CDPH metadata file should be listed first)
#      -extension: if using more than one geojson file this is list of file
#        name extensions to differentiate each set of files. Specify only the
#        file name extensions to use with the 2nd, 3rd, ..., set of files.
#      -isWDL: defalut is False. Set to true only if the script will be run 
#        as a WDL task in Terra.
#   Output files:
#      -metadata_merged.tsv: combined metadata file for both CDPH and public samples for the county analysis
#      -metadata_merged_us.tsv: combined metadata file for both CDPH and public samples for the state analysis
#      -sample_regions.tsv: list of sample names and corresponding regions for the county analysis
#      -sample_regions_us.tsv: list of sample names and corresponding regions for the state analysis
#      -sample_dates.tsv: list of sample names and corresponding dates for the county analysis
#      -sample_dates_us.tsv: list of sample names and corresponding dates for the state analysis
#      -pids.tsv: list of sample names and corresponding sample IDs/PAUIs
#
# Example command line usage:
#   python3 process_metadata.py -m samplemeta.tsv public.plusGisaid.latest.metadata.tsv -l state_and_county_lexicon.txt
#-------------------------------------------------------------

import re
import sys, os #comment out for WDL
#set path to directory 
sys.path.insert(1, os.path.join(os.path.abspath(__file__ + "/../../../"), "src/python/")) #comment out for WDL


def process_metadata(lexiconfile, metadatafiles, extension=["_us"], isWDL = False):
    #== for WDL ===
    # isWDL = True
    #===

    if isWDL:
        lexiconfile = '~{state_and_county_lex}'
        mfiles = ['~{samples}', '~{public_meta}']
        ext = "_us" 
    else:
        mfiles = metadatafiles
        if extension is None:
            ext = "_us"
        else:
            ext = extension[0]

    county_conversion = {}
    state_conversion = {}
    with open(lexiconfile) as inf:
        for entry in inf:
            spent = entry.strip().split(",")
            if "County" in spent[0]:
                county_conversion[spent[1].upper()] = spent[0]
            else:
                for alternative in spent:
                    state_conversion[alternative.upper()] = spent[0] 

    metadata = open("metadata_merged.tsv","w+") #output file for merged metadata, for US + CA county analysis
    metadata_us = open("metadata_merged" + ext + ".tsv","w+") #output file for merged metadata, for US analysis
    badsamples = open("rejected_samples.txt","w+") # file for rejected sample names
    region_assoc = open("sample_regions.tsv","w+") # file to store associations between sample ID and region name, for US + CA county analysis
    region_assoc_us = open("sample_regions" + ext + ".tsv","w+") # file to store associations between sample ID and region name, for US analysis
    date_file = open("sample_dates.tsv","w+") # file to store associations between sample ID and sample dates, for US + CA county analysis
    date_file_us = open("sample_dates" + ext + ".tsv","w+") # file to store associations between sample ID and sample dates, for US analysis
    print("sample_id\tdate", file = date_file)
    print("sample_id\tdate", file = date_file_us)
    pid_assoc = open("pids.tsv","w+") # file to store associations between sample ID and specimen_id (formerly PAUI or link_id)
    date_pattern = '[0-9]{4}-[0-9]{2}-[0-9]{2}'
    #write metadata header
    print("strain\tname\tpangolin_lineage\tnextclade_clade\tgisaid_accession\tcounty\tdate\tpaui\tsequencing_lab\tspecimen_id\tspecimen_accession_number\tgenbank_accession\tcountry", file = metadata)
    print("strain\tname\tpangolin_lineage\tnextclade_clade\tgisaid_accession\tcounty\tdate\tpaui\tsequencing_lab\tspecimen_id\tspecimen_accession_number\tgenbank_accession\tcountry", file = metadata_us)
    duplicates = set() #stores sample names of potential duplicates
    
    for f in mfiles:
        with open(f) as inf:
            print("parsing input metadata file: " + f)
            fields = inf.readline().strip().split("\t")
            # check which format the metadata is in based on header field names
            if fields[0] == "usherID":
                # CA metadata header: usherID,name,pango_lineage,nextclade_clade,gisaid_accession,county,collection_date,paui,sequencing_lab,specimen_id,specimen_accession_number
                for entry in inf:
                    has_valid_county = False
                    fields = entry.split("\t")
                    for i in range(len(fields)):
                        fields[i] = fields[i].strip()
                    fields.append("")
                    fields.append("USA")
                    #add item to merged metadata file for CA state analysis
                    print("\t".join(fields), file = metadata_us)
                    #assign to CA state in region file
                    print(fields[0] + "\tCalifornia", file = region_assoc_us)
                    #check if county is in lexicon and if so add to 
                    # merged metadata file and sample regions file
                    county = fields[5]
                    if county != "":
                        if county.upper() in (c.upper() for c in county_conversion): # convert all names to uppercase to avoid differences in case
                            has_valid_county = True
                            text = county_conversion[county.upper()].replace(" ", "_")
                            print(fields[0] + "\t" + text, file = region_assoc)
                            #add item to merged metadata file for CA county analysis
                            print("\t".join(fields), file = metadata)
                    #add sample names to list to check for duplicates; add date to date file
                    if fields[0].startswith("USA/CA"):
                        #add sample name if needed to check for duplicates later on
                        duplicates.add(fields[0])
                        #check for valid date in file name, use date field if invalid
                        if not re.search(date_pattern, fields[0][-10:]):
                            if re.search(date_pattern, fields[6]):
                                print(fields[0] + "\t" + fields[6], file = date_file_us)
                                if has_valid_county:
                                    print(fields[0] + "\t" + fields[6], file = date_file)
                    else:
                        #check for valid date and add sample ID and date to sample dates file
                        if re.search(date_pattern, fields[6]):
                            print(fields[0] + "\t" + fields[6], file = date_file_us)
                            if has_valid_county:
                                print(fields[0] + "\t" + fields[6], file = date_file)
                    #add Specimen ID to association file
                    if fields[9] != "":
                        print(fields[0] + "\t" + fields[9], file = pid_assoc)
            else:
                # public metadata header: strain,genbank_accession,date,country,host,completeness,length,Nextstrain_clade,pangolin_lineage,Nextstrain_clade_usher,pango_lineage_usher
                for entry in inf:
                    fields = entry.strip().split("\t")
                    country = fields[0].split("/")[0]
                    # check for US samples
                    if country == "USA":
                        state = fields[0].split("/")[1].split("-")[0]
                        if state in state_conversion:
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
                                newfields.append("") #specimen_accession_number
                                newfields.append(fields[1]) #genbank_accession
                                newfields.append("USA") #country
                                print("\t".join(newfields), file = metadata_us)
                                #add sample ID and state name to sample regions files
                                text = state_conversion[state.upper()].replace(" ", "_")
                                print(fields[0] + "\t" + text, file = region_assoc_us)
                                #filter out CA samples for CA county analysis
                                if state != "CA":
                                    print("\t".join(newfields), file = metadata)
                                    print(fields[0] + "\t" + text, file = region_assoc)
    metadata.close()
    badsamples.close()
    region_assoc.close()
    date_file.close()
    pid_assoc.close()
    metadata_us.close()
    region_assoc_us.close()
    date_file_us.close()

if __name__ == "__main__":
    from master_backend import parse_setup
    args = parse_setup()
    if args.region_extension is None:
        extension = ["_us"]
    else:
        extension = args.region_extension
    process_metadata(args.lexicon, args.metadata, extension)