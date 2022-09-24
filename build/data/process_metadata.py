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
#   python3 process_metadata.py -m public.plusGisaid.latest.metadata.tsv -mx samplemeta.tsv -l state_and_county_lexicon.txt
#-------------------------------------------------------------

import re, csv
import sys, os #comment out for WDL
#set path to directory 
sys.path.insert(1, os.path.join(os.path.abspath(__file__ + "/../../../"), "src/python/")) #comment out for WDL


def process_metadata(lexiconfile, mfile, mfile_merge, extension=["_us"], isWDL = False):
    #== for WDL ===
    # isWDL = True
    #===

    if isWDL:
        lexiconfile = '~{state_and_county_lex}'
        mfile = '~{public_meta}'
        mfile_merge = '~{samples}'
        ext = "_us" 
        #names of airport sample input files
        airport_file_p = '~{airport_p}'
        airport_file_c = '~{airport_c}'
    else:
        if type(mfile_merge) == list:
            mfile_merge = mfile_merge[0]
        if extension is None:
            ext = "_us"
        else:
            ext = extension[0]
        #names of airport sample input files
        airport_file_p = "F1a-qry-AirportCOVIDNet-ToUCSC-Data-P-ALL.csv"
        airport_file_c = "F1b-qry-AirportCOVIDNet-ToUCSC-Data-C-ALL.csv"

    county_conversion = {}
    state_conversion = {}
    airp_conversion = {}
    with open(lexiconfile) as inf:
        for entry in inf:
            spent = entry.strip().split(",")
            if "Airport" in spent[0]:
                airp_conversion[spent[1]] = spent[0]
            elif "County" in spent[0]:
                county_conversion[spent[1].upper()] = spent[0]
            else:
                for alternative in spent:
                    state_conversion[alternative.upper()] = spent[0] 

    metadata = open("metadata_merged.tsv","w+") #output file for merged metadata, for US + CA county analysis
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
    print("strain\tname\tpango_lineage\tnextclade_clade\tgisaid_accession\tcounty\tdate\tpaui\tsequencing_lab\tspecimen_id\tspecimen_accession_number\tgenbank_accession\tNextstrain_clade\tpangolin_lineage\tNextstrain_clade_usher\tpango_lineage_usher\tcountry", file = metadata)
    duplicates = set() #stores sample names of potential duplicates

    #read airport sample data
    airport_data = []
    with open(airport_file_p, mode='r') as csv_file:
        data = csv.DictReader(csv_file)
        for row in data:
            airport_data.append([str(row["Barcode"]),'',row["GISAID_epi_isl"],row["Kiosk"],row["Collection_Date"]])
    with open(airport_file_c, mode='r') as csv_file:
        data = csv.DictReader(csv_file)
        for row in data:
            airport_data.append([str(row["Submitter Specimen ID"]),str(row["PAUI"]),row["GISAID_epi_isl"],row["Airport"],row["Collection_Date"]])
    
    with open(mfile_merge) as inf:
        print("parsing input metadata file: " + mfile_merge)
        # CA metadata header: usherID,name,pango_lineage,nextclade_clade,gisaid_accession,county,collection_date,paui,sequencing_lab,specimen_id,specimen_accession_number 
        fields = inf.readline() #skip header
        for entry in inf:
            has_valid_county = False
            fields = entry.split("\t")
            for i in range(len(fields)):
                fields[i] = fields[i].strip()
            fields.append("") #genbank_accession
            fields.append("") #Nextstrain_clade (public metadata)
            fields.append("") #pangolin_lineage (public metadata)
            fields.append("") #Nextstrain_clade_usher (public metadata)
            fields.append("") #pango_lineage_usher (public metadata)
            fields.append("USA") #country
            
            #First, check to see if item is in airports file. If so, override county region with airport region
            # and save values to fill in any missing blanks in metadata
            ids = [fields[0],fields[1],fields[7],fields[-2],fields[-1]]
            isAirport = False
            aiport_paui = ""
            airport_gisaid = ""
            airport_abbr = ""
            airport_date = ""
            for item in airport_data:
                if any(item[0] in id for id in ids):
                    isAirport = True
                    airport_paui = item[1]
                    airport_gisaid = item[2]
                    airport_abbr = item[3]
                    airport_date = item[4]
                    break
                elif item[1] != "" and any(item[1] in id for id in ids):
                    isAirport = True
                    airport_paui = item[1]
                    airport_gisaid = item[2]
                    airport_abbr = item[3]
                    airport_date = item[4]
                    break
                elif item[2] != "" and item[2] == fields[4]:
                    isAirport = True
                    airport_paui = item[1]
                    airport_gisaid = item[2]
                    airport_abbr = item[3]
                    airport_date = item[4]
                    break
            #if date isn't valid, reset to blank to avoid having to do multiple validity checks
            if airport_date != "" and not re.search(date_pattern, airport_date):
                airport_date = ""

            #Next, assign a region
            #assign region for airport data
            if isAirport:
                if airport_abbr in airp_conversion:
                    text = airp_conversion[airport_abbr].replace(" ", "_")
                    print(fields[0] + "\t" + text, file = region_assoc)
                    print(fields[0] + "\t" + text, file = region_assoc_us)
                else:
                    isAirport = False
            #assign region for non-airport data
            if not isAirport:
                #assign to CA state in region file
                print(fields[0] + "\tCalifornia", file = region_assoc_us)
                #check if county is in lexicon and if so add to region association file
                county = fields[5]
                if county != "":
                    if county.upper() in (c.upper() for c in county_conversion): # convert all names to uppercase to avoid differences in case
                        has_valid_county = True
                        text = county_conversion[county.upper()].replace(" ", "_")
                        print(fields[0] + "\t" + text, file = region_assoc)
            
            #Next, add dates to date file if needed
            #add sample names to list to check for duplicates; add date to date file
            if fields[0].startswith("USA/"):
                #add sample name if needed to check for duplicates later on
                duplicates.add(fields[0])
                #check for valid date in file name, use date field if invalid
                if not re.search(date_pattern, fields[0][-10:]):
                    if re.search(date_pattern, fields[6]):
                        print(fields[0] + "\t" + fields[6], file = date_file_us)
                        if has_valid_county or isAirport:
                            print(fields[0] + "\t" + fields[6], file = date_file)
                    elif isAirport and airport_date != "":
                        print(fields[0] + "\t" + airport_date, file = date_file)
                        print(fields[0] + "\t" + airport_date, file = date_file_us)
            else:
                #check for valid date and add sample ID and date to sample dates file
                if re.search(date_pattern, fields[6]):
                    print(fields[0] + "\t" + fields[6], file = date_file_us)
                    if has_valid_county or isAirport:
                        print(fields[0] + "\t" + fields[6], file = date_file)
                elif isAirport and airport_date != "":
                    print(fields[0] + "\t" + airport_date, file = date_file)
                    print(fields[0] + "\t" + airport_date, file = date_file_us)
            
            #Now, add Specimen ID to association file
            if fields[9] != "":
                print(fields[0] + "\t" + fields[9], file = pid_assoc)

            #Finally, write item to merged metadata file
            if isAirport:
                #if date, gisaid id, or paui are missing, fill those in
                if fields[6] == "" and airport_date != "":
                    fields[6] = airport_date
                if fields[7] == "" and aiport_paui != "":
                    fields[7] = aiport_paui
                if fields[4] == "" and airport_gisaid != "":
                    fields[4] = airport_gisaid
            print("\t".join(fields), file = metadata)


    with open(mfile) as inf:
        print("parsing input metadata file: " + mfile)
        # public metadata header: strain,genbank_accession,date,country,host,completeness,length,Nextstrain_clade,pangolin_lineage,Nextstrain_clade_usher,pango_lineage_usher
        fields = inf.readline() #skip header
        for entry in inf:
            fields = entry.strip().split("\t")
            country = fields[0].split("/")[0]
            #first, remove duplicate CDPH data
            if country == "USA" and fields[0] in duplicates:
                print(fields[0], file = badsamples)
            else:
                #add item to merged metadata file
                newfields = []
                newfields.append(fields[0]) #sample name
                newfields.append("") #CDPH name
                newfields.append("") #pango_lineage (CDPH metadata)
                newfields.append("") #nextclade_clade (CDPH metadata)
                newfields.append("") #gisaid_accession
                newfields.append("") #county name
                newfields.append(fields[2]) #date
                newfields.append("") #paui
                newfields.append("") #sequencing_lab
                newfields.append("") #specimen_id
                newfields.append("") #specimen_accession_number
                newfields.append(fields[1]) #genbank_accession
                newfields.append(fields[7]) #Nextstrain_clade (public metadata)
                newfields.append(fields[8]) #pangolin_lineage (public metadata)
                newfields.append(fields[9]) #Nextstrain_clade_usher (public metadata)
                newfields.append(fields[10]) #pango_lineage_usher (public metadata)
                newfields.append(fields[3]) #country
                print("\t".join(newfields), file = metadata)
                # get region for US samples
                if country == "USA":
                    state = fields[0].split("/")[1].split("-")[0]
                    if state in state_conversion:
                        #add sample ID and state name to sample regions files
                        text = state_conversion[state.upper()].replace(" ", "_")
                        print(fields[0] + "\t" + text, file = region_assoc_us)
                        #filter out CA samples for CA county analysis
                        if state != "CA":
                            print(fields[0] + "\t" + text, file = region_assoc)

    metadata.close()
    badsamples.close()
    region_assoc.close()
    date_file.close()
    pid_assoc.close()
    region_assoc_us.close()
    date_file_us.close()

if __name__ == "__main__":
    from master_backend import parse_setup
    args = parse_setup()
    if args.region_extension is None:
        extension = ["_us"]
    else:
        extension = args.region_extension
    process_metadata(args.lexicon, args.metadata, args.merge_metafile, extension)