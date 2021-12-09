def get_taxonium_link(host,cluster):
    if host == "https://storage.googleapis.com/ucsc-gi-cdph-bigtree/":
        host += "display_tables/"
    link = "https://taxonium.org/?protoUrl=" + host + "cview.pb.gz"
    link += '&search=[{"id":0.123,"category":"cluster","value":"'
    link += cluster
    link += '","enabled":true,"aa_final":"any","min_tips":1,"aa_gene":"S","search_for_ids":""}]'
    link += '&colourBy={"variable":"region","gene":"S","colourLines":false,"residue":"681"}'
    link += "&zoomToSearch=0&blinking=false"
    return link

def get_investigator_link(pid_list,cluster_id,fname):
    link = "No identifiable samples"
    if pid_list != "":
        link = "https://investigator.big-tree.ucsc.edu/?"
        link += "file=" + fname
        link += "&cid=" + cluster_id
        #encode spaces
        link = link.replace(" ","%20")
    return link

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

def generate_display_tables(conversion = {}, host = "https://storage.googleapis.com/ucsc-gi-cdph-bigtree/"):
    filelines = {}
    def fix_month(datestr):
        monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
        splitr = datestr.split("-")
        return splitr[0] + "-" + monthswap.get(splitr[1],splitr[1]) + "-" + splitr[2]
    default_growthvs = []
    default_lines = []
    totbuff = [] #track overall no valid date clusters to fill in at the end.
    # get sample name/PAUI associations
    pid_assoc = {} # links sample ID with personal id (PAUI)
    with open("pids.tsv") as inf:
        for entry in inf:
            spent = entry.strip().split("\t")
            pid_assoc[spent[0]] = spent[1]
    with open("hardcoded_clusters.tsv") as inf:
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
    header = "Cluster ID\tRegion\tSample Count\tEarliest Date\tLatest Date\tClade\tLineage\tInferred Origins\tInferred Origin Confidences\tGrowth Score\tClick to View in Taxonium\tClick to View in CA Big Tree Investigator\tLink IDs"
    mout = open("cluster_labels.tsv","w+")
    print("sample\tcluster",file=mout)
    for reg, lines in filelines.items():
        fname = conversion[reg].replace(" ", "_") + "_topclusters.tsv"
        with open("display_tables/" + fname, "w+") as outf:
            print(header,file=outf)
            for l in lines:
                #process the line 
                #into something more parseable.
                spent = l.split("\t")
                #get California sample PAUIs and create link to BT Investigator
                pid_list = get_sample_pauis(spent[-1],pid_assoc)
                ilink = get_investigator_link(pid_list, spent[0], fname)
                #save matching results to the other output files
                #for downstream extraction of json
                samples = spent[-1].split(",")
                for s in samples:
                    print(s + "\t" + spent[0],file=mout)
                #generate a link to exist in the last column
                #based on the global "host" variable.
                #and including all html syntax.
                link = get_taxonium_link(host,spent[0])
                #additionally process the date strings
                outline = [spent[0], spent[9], spent[1], fix_month(spent[2]), fix_month(spent[3]), spent[12], spent[13], spent[10], spent[11], spent[4], link, ilink, pid_list]
                print("\t".join(outline),file=outf)

    mout.close()
    sorted_defaults = sorted(list(zip(default_growthvs,default_lines)),key=lambda x:-x[0])
    with open("display_tables/default_clusters.tsv","w+") as outf:
        print(header,file=outf)
        for gv,dl in sorted_defaults:
            spent = dl.split("\t")
            #get California sample PAUIs and create link to BT Investigator
            pid_list = get_sample_pauis(spent[-1],pid_assoc)
            ilink = get_investigator_link(pid_list, spent[0],"default_clusters.tsv")
            link = get_taxonium_link(host,spent[0])
            outline = [spent[0], spent[9], spent[1], fix_month(spent[2]), fix_month(spent[3]), spent[12], spent[13], spent[10], spent[11], spent[4], link, ilink, pid_list]
            print("\t".join(outline), file = outf)
lexicon = {"Alameda":"Alameda County","Alpine":"Alpine County","Amador":"Amador County","Butte":"Butte County",
    "Calaveras":"Calaveras County","Colusa":"Colusa County","Contra Costa":"Contra Costa County","Del Norte":"Del Norte County",
    "El Dorado":"El Dorado County","Fresno":"Fresno County","Glenn":"Glenn County","Humboldt":"Humboldt County",
    "Imperial":"Imperial County","Inyo":"Inyo County","Kern":"Kern County","Kings":"Kings County","Lake":"Lake County",
    "Lassen":"Lassen County","Los Angeles":"Los Angeles County","Madera":"Madera County","Marin":"Marin County",
    "Mariposa":"Mariposa County","Mendocino":"Mendocino County","Merced":"Merced County","Modoc":"Modoc County",
    "Mono":"Mono County","Monterey":"Monterey County","Napa":"Napa County","Nevada":"Nevada County","Orange":"Orange County",
    "Placer":"Placer County","Plumas":"Plumas County","Riverside":"Riverside County","Sacramento":"Sacramento County",
    "San Benito":"San Benito County","San Bernardino":"San Bernardino County","San Diego":"San Diego County",
    "San Francisco":"San Francisco County","San Joaquin":"San Joaquin County","San Luis Obispo":"San Luis Obispo County",
    "San Mateo":"San Mateo County","Santa Barbara":"Santa Barbara County","Santa Clara":"Santa Clara County",
    "Santa Cruz":"Santa Cruz County","Shasta":"Shasta County","Sierra":"Sierra County","Siskiyou":"Siskiyou County",
    "Solano":"Solano County","Sonoma":"Sonoma County","Stanislaus":"Stanislaus County","Sutter":"Sutter County",
    "Tehama":"Tehama County","Trinity":"Trinity County","Tulare":"Tulare County","Tuolumne":"Tuolumne County",
    "Ventura":"Ventura County","Yolo":"Yolo County","Yuba":"Yuba County",
    "ALAMEDA":"Alameda County","ALPINE":"Alpine County","AMADOR":"Amador County","BUTTE":"Butte County",
    "CALAVERAS":"Calaveras County","COLUSA":"Colusa County","CONTRA COSTA":"Contra Costa County","DEL NORTE":"Del Norte County",
    "EL DORADO":"El Dorado County","FRESNO":"Fresno County","GLENN":"Glenn County","HUMBOLDT":"Humboldt County",
    "IMPERIAL":"Imperial County","INYO":"Inyo County","KERN":"Kern County","KINGS":"Kings County","LAKE":"Lake County",
    "LASSEN":"Lassen County","LOS ANGELES":"Los Angeles County","MADERA":"Madera County","MARIN":"Marin County",
    "MARIPOSA":"Mariposa County","MENDOCINO":"Mendocino County","MERCED":"Merced County","MODOC":"Modoc County",
    "MONO":"Mono County","MONTEREY":"Monterey County","NAPA":"Napa County","NEVADA":"Nevada County","ORANGE":"Orange County",
    "PLACER":"Placer County","PLUMAS":"Plumas County","RIVERSIDE":"Riverside County","SACRAMENTO":"Sacramento County",
    "SAN BENITO":"San Benito County","SAN BERNARDINO":"San Bernardino County","SAN DIEGO":"San Diego County",
    "SAN FRANCISCO":"San Francisco County","SAN JOAQUIN":"San Joaquin County","SAN LUIS OBISPO":"San Luis Obispo County",
    "SAN MATEO":"San Mateo County","SANTA BARBARA":"Santa Barbara County","SANTA CLARA":"Santa Clara County",
    "SANTA CRUZ":"Santa Cruz County","SHASTA":"Shasta County","SIERRA":"Sierra County","SISKIYOU":"Siskiyou County",
    "SOLANO":"Solano County","SONOMA":"Sonoma County","STANISLAUS":"Stanislaus County","SUTTER":"Sutter County",
    "TEHAMA":"Tehama County","TRINITY":"Trinity County","TULARE":"Tulare County","TUOLUMNE":"Tuolumne County",
    "VENTURA":"Ventura County","YOLO":"Yolo County","YUBA":"Yuba County",
    "AL":"Alabama","AK":"Alaska","AR":"Arkansas","AZ":"Arizona","CO":"Colorado",
    "CT":"Connecticut","DE":"Delaware","DC":"District of Columbia","FL":"Florida","GA":"Georgia","HI":"Hawaii",
    "ID":"Idaho","IL":"Illinois","IN":"Indiana","IA":"Iowa","KS":"Kansas","KY":"Kentucky","LA":"Louisiana","ME":"Maine",
    "MD":"Maryland","MA":"Massachusetts","MI":"Michigan","MN":"Minnesota","MS":"Mississippi","MO":"Missouri","MT":"Montana",
    "NE":"Nebraska","NV":"Nevada","NH":"New Hampshire","NJ":"New Jersey","NM":"New Mexico","NY":"New York","NC":"North Carolina",
    "ND":"North Dakota","OH":"Ohio","OK":"Oklahoma","OR":"Oregon","PA":"Pennsylvania","RI":"Rhode Island",
    "SC":"South Carolina","SD":"South Dakota","TN":"Tennessee","TX":"Texas","UT":"Utah","VT":"Vermont","VA":"Virginia",
    "WA":"Washington","WV":"West Virginia","WI":"Wisconsin","WY":"Wyoming","PR":"Puerto Rico"}
lexicon.update({v:v for v in lexicon.values()})
if __name__ == "__main__":
    generate_display_tables(lexicon, host = "https://storage.googleapis.com/ucsc-gi-cdph-bigtree/")
