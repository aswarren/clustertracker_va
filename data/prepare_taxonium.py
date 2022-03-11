def prepare_taxonium(sample_regions, mf, extension = ""):
    ext = extension.split(",") #get file name extensions if processiing more than one file
    for e in ext:
        cluster_file = "hardcoded_clusters" + e + ".tsv"
        cluster_swp_file = "clusterswapped" + e + ".tsv"
        idx = sample_regions.rfind(".")
        if idx >= 0:
            sample_regions = sample_regions[:idx] + e + sample_regions[idx:]
        idx = mf.rfind(".")
        if idx >= 0:
            mf = mf[:idx] + e + mf[idx:]
        sd = {}
        with open(cluster_file) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                if spent[0] == 'cluster_id':
                    continue
                for s in spent[-1].split(","):
                    sd[s] = spent[0] # sd[sample name] = cluster id
        rd = {} 
        with open(sample_regions) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                rd[spent[0]] = spent[1] # rd[sample name] = region
        with open(mf) as inf:
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

extension = ",_us"
if __name__ == "__main__":
    prepare_taxonium("sample_regions.tsv","metadata_merged.tsv",extension)