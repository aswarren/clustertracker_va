#  Python "backend" code to generate individual cluster files for each 
#    region. These files contain the information that is displayed in
#    the table below the map on the web page. 
#  This script is meant to be called from "master_backend.py" but can be
#    run separately from the command line.
#
# "generate_display_tables" is the main function.
# Arguments:
#   -conversion: dictionary created from lexicon file
#   -host: Publicly accessible URL where you will be hosting the Taxonium
#     protobuf.
#   -extension: if using more than one geojson file this is list of file
#     name extensions to differentiate each set of files. Specify only the
#     file name extensions to use with the 2nd, 3rd, ..., set of files.
# Outputs:
#  - default_clusters.tsv
#  -[region_name]_topclusters.tsv
#  -cluster_labels.tsv
#
# Example command line usage:
# python3 generate_display_tables.py -l state_and_county_lexicon.txt
#  -H https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/ -e "_us"
#-------------------------------------------------------------
# CDPH WDL INPUTS:
#  File state_and_county_lex # "state_and_county_lexicon.txt", lexicon with state and county abbreviations
#  File clusters_counties # "hardcoded_clusters.tsv", cluster file from CA county introductions
#  File clusters_state # "hardcoded_clusters_us.tsv", cluster file from CA state introductions
#  File pids #"pids.tsv", file linking sample name and PAUI/Specimen ID from CA county samples
#  File pids_us #"pids_us.tsv", file linking sample name and PAUI/Specimen ID from CA state samples
# CDPH WDL OUTPUTS:
#  File labels = "cluster_labels.tsv"
#  File labels_us = "cluster_labels_us.tsv"
#  Array[File] display_tables = glob("*lusters.tsv")
#-------------------------------------------------------------

import os #comment out for WDL

# function to construct links to Taxonium
def get_taxonium_link(host,cluster,ext):
    link = 'https://taxonium.org/?protoUrl=' + host + 'cview' + ext + '.jsonl.gz'
    link += '&color={"field":"meta_region"}'
    link += '&srch=[{"key":"aa1","type":"meta_cluster","method":"text_match","text":"'
    link += cluster
    link += '","gene":"S","position":484,"new_residue":"any","min_tips":0,"controls":true}]'
    link += '&zoomToSearch=0'
    return link


#function to evaluate whether to add custom CDPH data fields to 
# output cluster files
def is_custom_data(host):
    if "ucsc-gi-cdph-bigtree" in host:
        return True
    else:
        return False

## Functions for custom CDPH data
#adds a link to the CA Big Tree Investigator to the output cluster files
def get_investigator_link(pid_list,cluster_id,fname):
    link = "No identifiable samples"
    if pid_list != "":
        link = "https://investigator.big-tree.ucsc.edu/?"
        link += "file=" + fname
        link += "&cid=" + cluster_id
        #encode spaces
        link = link.replace(" ","%20")
    return link

#adds unique sample ID's to the output cluster files
def get_sample_pauis(items,pid_assoc):
    pid_list = ""
    pids = []
    samples = items.split(",")
    for s in samples:
        #get PAUI's from sample names
        if s.startswith('CDPH') or s.startswith('USA/CA-CDPH'):
            if s in pid_assoc:
                pids.append(pid_assoc[s])
    if pids:
        pid_list = ",".join(pids)
    return pid_list

## main function
def generate_display_tables(conversion = {}, host = '', extension = ['']):
    #for WDL: insert here read_lexicon function from utils.py
    
    #conversion = read_lexicon('~{state_and_county_lex}') #for WDL
    #host = 'https://storage.googleapis.com/ucsc-gi-cdph-bigtree/display_tables/'
    #extension = ['', '_us'] #for WDL

    #set flag to identify whether to add custom fields to output cluster files
    is_custom =  is_custom_data(host)

    #input file names
    cluster_file = ["hardcoded_clusters" + extension[i] + ".tsv" for i in range(len(extension))] #comment out for WDL
    #cluster_file = ['~{clusters_counties}', '~{clusters_state}'] #for WDL
    if is_custom:
        pid_file = ["pids" + extension[i] + ".tsv" for i in range(len(extension))] #comment out for WDL
        #pid_file = ['~{pids}','~{pids_us}'] #for WDL
        subfolder = ""
    else:
        subfolder = "display_tables/"
        #check if folder exists and create if needed
        if not os.path.isdir(subfolder):
            os.makedirs(subfolder)
    
    #file header
    header = "Cluster ID\tRegion\tSample Count\tEarliest Date\tLatest Date\tClade\tLineage\tInferred Origins\tInferred Origin Confidences\tGrowth Score\tClick to View in Taxonium"
    if is_custom:
        header += "\tClick to View in CA Big Tree Investigator\tSpecimen IDs"

    for i, ext in enumerate(extension):
        labels_file = "cluster_labels" + ext + ".tsv"
        defaultc_file = "default_clusters" + ext + ".tsv"
        filelines = {}
        def fix_month(datestr):
            monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
            splitr = datestr.split("-")
            return splitr[0] + "-" + monthswap.get(splitr[1],splitr[1]) + "-" + splitr[2]
        default_growthvs = []
        default_lines = []
        totbuff = [] #track overall no valid date clusters to fill in at the end.
        
        if is_custom:
            # get sample name/PAUI associations
            pid_assoc = {} # links sample ID with personal id (PAUI)
            with open(pid_file[i]) as inf:
                for entry in inf:
                    spent = entry.strip().split("\t")
                    pid_assoc[spent[0]] = spent[1]

        with open(cluster_file[i]) as inf:
            cr = "None"
            buffer = []
            for entry in inf:
                spent = entry.strip().split("\t")
                if spent[0] == "cluster_id": 
                    continue
                reg = conversion[spent[9].replace("_"," ")]
                if reg not in filelines:
                    filelines[reg] = []
                if cr == "None":
                    cr = reg
                elif reg != cr:
                    #when moving to a new region
                    if len(filelines[cr]) < 100:
                        filelines[cr].extend(buffer[:100-len(filelines[cr])])
                    buffer = []
                    cr = reg
                if spent[3] == "no-valid-date":
                    buffer.append(entry.strip())
                    totbuff.append((entry.strip(), float(spent[4])))
                    continue
                if len(filelines[reg]) < 100:
                    filelines[reg].append(entry.strip())
                #now, check to see if this scores in the top 100 overall. Significantly more complicated since we have to sort things out as we go here.
                if len(default_lines) < 100:
                    default_growthvs.append(float(spent[4]))
                    default_lines.append(entry.strip())
                elif float(spent[4]) > min(default_growthvs):
                    popind = default_growthvs.index(min(default_growthvs))
                    default_growthvs.pop(popind)
                    default_lines.pop(popind)
                    default_growthvs.append(float(spent[4]))
                    default_lines.append(entry.strip())
                    assert len(default_lines) == 100
            #remove any remaining buffer for the last region in the file as well.
            if len(filelines[cr]) < 100:
                filelines[cr].extend(buffer[:100-len(filelines[cr])])
            #and if there are less than 100 clusters with dates for the default view, extend that as well.
            if len(default_lines) < 100:
                totbuff.sort(key = lambda x: x[1], reverse = True)
                for t in totbuff[:100-len(default_lines)]:
                    default_lines.append(t[0])
                    default_growthvs.append(0-1/t[1])
        mout = open(labels_file,"w+")
        print("sample\tcluster",file=mout)
        for reg, lines in filelines.items():
            fname = conversion[reg].replace(" ", "_") + "_topclusters" + ext + ".tsv"
            with open(subfolder + fname, "w+") as outf:
                print(header,file=outf)
                for l in lines:
                    #process the line 
                    #into something more parseable.
                    spent = l.split("\t")
                    #save matching results to the other output files
                    #for downstream extraction of json
                    samples = spent[-1].split(",")
                    for s in samples:
                        print(s + "\t" + spent[0],file=mout)
                    #generate a link to exist in the last column
                    #based on the global "host" variable.
                    #and including all html syntax.
                    link = get_taxonium_link(host,spent[0],ext)
                    #additionally process the date strings
                    outline = [spent[0], spent[9], spent[1], fix_month(spent[2]), fix_month(spent[3]), spent[12], spent[13], spent[10], spent[11], spent[4], link]
                    if is_custom:
                        #get California sample PAUIs and create link to BT Investigator
                        pid_list = get_sample_pauis(spent[-1],pid_assoc)
                        ilink = get_investigator_link(pid_list, spent[0], fname)
                        outline.append(ilink)
                        outline.append(pid_list)
                    print("\t".join(outline),file=outf)

        mout.close()
        sorted_defaults = sorted(list(zip(default_growthvs,default_lines)),key=lambda x:-x[0])
        with open(subfolder + defaultc_file,"w+") as outf:
            print(header,file=outf)
            for gv,dl in sorted_defaults:
                spent = dl.split("\t")
                link = get_taxonium_link(host,spent[0],ext)
                outline = [spent[0], spent[9], spent[1], fix_month(spent[2]), fix_month(spent[3]), spent[12], spent[13], spent[10], spent[11], spent[4], link]
                if is_custom:
                    #get California sample PAUIs and create link to BT Investigator
                    pid_list = get_sample_pauis(spent[-1],pid_assoc)
                    ilink = get_investigator_link(pid_list, spent[0],defaultc_file)
                    outline.append(ilink)
                    outline.append(pid_list)
                print("\t".join(outline), file = outf)

if __name__ == "__main__":
    from master_backend import parse_setup
    from utils import read_lexicon
    args = parse_setup()
    lexicon = read_lexicon(args.lexicon)
    lexicon.update({v:v for v in lexicon.values()})
    extension = args.region_extension
    if extension is None:
        extension = ['']
    else:
        extension.insert(0,'')
    generate_display_tables(lexicon, args.host, extension)