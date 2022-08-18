#  Python "backend" code that creates a metadata file that will be used
#    to create the Taxonium protobuf
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
# Example command line usage:
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
        mf = ['~{merged}', '~{merged_us}']
        cluster_file = ['~{clusters_counties}', '~{clusters_state}']
        extension = ['', '_us']
    else: 
        sample_regions = list([sample_regions_file])
        mf = mfile
        cluster_file = ["hardcoded_clusters.tsv"]
        if len(extension) > 1:
            for e in extension[1:]:
                sample_regions.append(insert_extension(sample_regions_file, e)) #comment out for WDL?
                mf.append(insert_extension(mfile[0], e)) #comment out for WDL?
                cluster_file.append("hardcoded_clusters" + e + ".tsv")

    for j, e in enumerate(extension):
        cluster_swp_file = "clusterswapped" + e + ".tsv"
        sd = {}
        with open(cluster_file[j]) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                if spent[0] == 'cluster_id':
                    continue
                for s in spent[-1].split(","):
                    sd[s] = spent[0] # sd[sample name] = cluster id
        rd = {} 
        with open(sample_regions[j]) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                rd[spent[0]] = spent[1] # rd[sample name] = region
        with open(mf[j]) as inf:
            with open(cluster_swp_file,"w+") as outf:
                #clusterswapped is the same as the metadata input
                #except with the cluster ID field added, and "region" field added
                #to account for blank values. 
                i = 0
                for entry in inf:
                    spent = entry.strip().split("\t")
                    if i == 0:
                        spent.append("cluster")
                        spent.append("region")
                        i += 1
                        print("\t".join(spent),file=outf)
                        continue
                    #adds cluster id
                    if spent[0] in sd:
                        spent.append(sd[spent[0]])
                    else:
                        spent.append("N/A")
                    #adds region name
                    if spent[0] in rd:
                        spent.append(rd[spent[0]])
                    else:
                        spent.append("None")
                    i += 1
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