#  Python "backend" code that creates a metadata file that will be used
#    to create the Taxonium JSONL file
#
# Arguments:
#   -sample_regions_file: TSV file containing sample names and associated regions
#   -mfile: metadata file
#   -extension: if using more than one geojson file this is list of file
#     name extensions to differentiate each set of files. Specify only the
#     file name extensions to use with the 2nd, 3rd, ..., set of files.
#   -isWDL: defalut is False. Set to true only if the script will be run 
#     as a WDL task in Terra.
# Outputs:
#  -clusterswapped.tsv
#
# Example command line if following the GitHub example in the "example" directory:
# python3 prepare_taxonium.py -s sample_regions.tsv -m public-latest.metadata.tsv
# 
# Example command line usage for CDPH:
# python3 prepare_taxonium.py -s sample_regions.tsv -m metadata_merged.tsv -e "_us"
#-------------------------------------------------------------

from utils import insert_extension #comment out for WDL

def prepare_taxonium(sample_regions_file, mfile, extension=[''], isWDL = False):
    #== for WDL ===
    # isWDL = True
    #===

    #input file names
    if isWDL:
        sample_regions = ['~{regions}', '~{regions_us}']
        mfile = '~{merged}'
        cluster_file = ['~{clusters_counties}', '~{clusters_state}']
        extension = ['', '_us']
    else: 
        sample_regions = list([sample_regions_file])
        cluster_file = ["hardcoded_clusters.tsv"]
        if len(extension) > 1:
            for e in extension[1:]:
                sample_regions.append(insert_extension(sample_regions_file, e))
                cluster_file.append("hardcoded_clusters" + e + ".tsv")

    #assign cluster/region labels
    header_labels = "\tcluster\tregion"
    if len(extension) > 1:
        for i in range(1, len(extension)):
            header_labels = header_labels + "\tcluster" + str(i + 1) + "\tregion" + str(i + 1)

    #initialize cluster and region dict lists
    cluster_dicts = []
    region_dicts = []
    for index in range(len(extension)):
        sd = {}
        with open(cluster_file[index]) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                if spent[0] == 'cluster_id':
                    continue
                for s in spent[-1].split(","):
                    sd[s] = spent[0] # sd[sample name] = cluster id
        rd = {} 
        with open(sample_regions[index]) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                rd[spent[0]] = spent[1] # rd[sample name] = region
        cluster_dicts.append(sd)
        region_dicts.append(rd)

    with open("clusterswapped.tsv","w+") as outf:
        #clusterswapped is the same as the metadata input
        #except with the cluster ID field added, and "region" field added
        #to account for blank values. 
        with open(mfile) as inf:
            line = inf.readline()
            print(line.strip() + header_labels,file=outf) #add header labels
            for entry in inf:
                spent = entry.split("\t") #don't use strip here to preserve trailing tabs
                spent[-1] = spent[-1].strip() #remove newline char
                for index in range(len(extension)):
                    #adds cluster id
                    if spent[0] in cluster_dicts[index]:
                        spent.append(cluster_dicts[index][spent[0]])
                    else:
                        spent.append("N/A")
                    #adds region name
                    if spent[0] in region_dicts[index]:
                        spent.append(region_dicts[index][spent[0]].replace("_", " "))
                    else:
                        spent.append("None")
                print("\t".join(spent),file=outf)

if __name__ == "__main__":
    from master_backend import parse_setup
    args = parse_setup()
    extension = args.region_extension
    if extension is None:
        extension = ['']
    else:
        extension.insert(0,'')
    prepare_taxonium(args.sample_regions, args.metadata, extension)