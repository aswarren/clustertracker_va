#  Python "backend" code for creating a Leaflet compatible geojson file.
#  This script takes one or more geojson files and inserts cluster introduction
#  data for each region into each geographic feature. This script is meant to
#  to be called from "master_backend.py" but can be run separately from the
#  command line.
#
# Arguments:
#   -target: list of geojson file(s) containng the lat/long boundaries of the 
#     regions of interest. Typically you will show all regions on a single map,
#     but if you want to  show the same overall map with different boundaries (e.g.
#     one map with US county boundaries and one file with US state boundaries) 
#     this can be done with using two geojson files (e.g., one with county 
#     boundaries and one with state boundaries.
#   -conversion: dictionary created from lexicon file
#   -extension: if using more than one geojson file this is list of file
#     name extensions to differentiate each set of files. Specify only the
#     file name extensions to use with the 2nd, 3rd, ..., set of files.
# Outputs:
#  -region.js
#
# Example command line usage:
# python3 update_js.py -j us-states_ca-counties.geo.json us-states.geo.json
#  -l state_and_county_lexicon.txt -e "_us"
#-------------------------------------------------------------

import json
import math
import datetime as dt
from dateutil.relativedelta import relativedelta

def update_js(target=[''], conversion = {}, extension=['']):
    #for WDL: insert here read_lexicon function from utils.py

    #target = ['~{us_states_w_ca_counties_geo}' , '~{us_states_geo}'] #for WDL
    #conversion = read_lexicon('~{state_and_county_lex}') #for WDL
    #extension = ["", "_us"] #for WDL

    #input cluster file name(s)
    cluster_file = ["hardcoded_clusters" + extension[i] + ".tsv" for i in range(len(target))] #comment out for WDL
    #cluster_file = ['~{clusters_counties}', '~{clusters_state}'] #for WDL

    monthswap = {"Jan":"01","Feb":"02","Mar":"03","Apr":"04","May":"05","Jun":"06","Jul":"07","Aug":"08","Sep":"09","Oct":"10","Nov":"11","Dec":"12"}
    conversion.update({v:v for k,v in conversion.items()})
    conversion["indeterminate"] = "indeterminate"
    datepoints = ["all", dt.date.today()-relativedelta(months=12), dt.date.today()-relativedelta(months=6), dt.date.today()-relativedelta(months=3)]
    
    for idx, gfile in enumerate(target):
        #intialize variables
        svd = {"type":"FeatureCollection", "features":[]}
        #here, the data is stored in a series of dictionaries
        #which are generally structured with the minimum date as the outermost layer
        #then the destination of an introduction
        #than the source of an introduction
        prefd = {datepoints[0]:"", datepoints[1]:"12_", datepoints[2]:"6_", datepoints[3]:"3_"}
        dinvc = {d:{} for d in datepoints}
        dsvc = {d:{} for d in datepoints}
        dotvc = {d:{} for d in datepoints}
        dovc = {d:{} for d in datepoints} 
        
        with open(cluster_file[idx]) as inf:
            for entry in inf:
                spent = entry.strip().split("\t")
                if spent[0] == "cluster_id":
                    continue
                reg = conversion[spent[9].replace("_"," ")]
                if  "indeterminate" in spent[10]:
                    continue
                #get the date of this cluster's earliest sample into a usable form
                dsplt = spent[2].split("-")
                if dsplt == "no-valid-date".split("-"):
                    cdate = dt.date(year=2019,month=11,day=1)
                else:
                    cdate = dt.date(year=int(dsplt[0]), month=int(monthswap[dsplt[1]]), day=int(dsplt[2]))
                for startdate, ovc in dovc.items():
                    if startdate == "all" or cdate > startdate:
                        if reg not in dsvc[startdate]:
                            dsvc[startdate][reg] = 0
                        dsvc[startdate][reg] += spent[-1].count(',') + 1
                        if reg not in dinvc[startdate]:
                            dinvc[startdate][reg] = 0
                        dinvc[startdate][reg] += 1
                        otvc = dotvc[startdate]
                        ovc = dovc[startdate]
                        if reg not in ovc:
                            ovc[reg] = {}
                        for tlo in spent[10].split(","):
                            orig = conversion[tlo.replace("_"," ")]
                            if orig not in otvc:
                                otvc[orig] = 0
                            otvc[orig] += 1
                            if orig not in ovc[reg]:
                                ovc[reg][orig] = 0
                            ovc[reg][orig] += 1
        dsumin = {sd:sum(invc.values()) for sd,invc in dinvc.items()}
        sids = {}
        f = open(gfile)
        geojson_lines = json.load(f)
        f.close()
        id = 0
        #we fill in the basic count of introductions to each area first
        #as well as fill in an integer "ID" if its not already present
        for data in geojson_lines["features"]:
            data["properties"]["intros"] = {}
            for sd, invc in dinvc.items():
                prefix = prefd[sd]
                data["properties"]["intros"][prefix + "basecount"] = invc.get(data["properties"]["name"],0) 
            svd["features"].append(data)
            if "id" in data:
                sids[data["properties"]["name"]] = data["id"]
            else:
                data["id"] = str(id)
                sids[data["properties"]["name"]] = str(id)
                id += 1
        #update the data intros list with specific state values
        for ftd in svd["features"]:
            #update the ftd["properties"]["intros"] with each state
            #state introductions to itself, for now, I will fill with indeterminate
            #this is transposed so that the introductions to each state are stored across each other state by origin
            #in order that coloring and hovertext can be correctly accessed.
            iid = ftd['properties']["name"]
            did = {}
            #for timeslice
            for sd, ovc in dovc.items():
                #get everything where this specific row/region is an origin
                prefix = prefd[sd]
                #fill with 0
                inv_ovc = {k:subd.get(iid,0) for k,subd in ovc.items()}
                for destination, count in inv_ovc.items():
                    #scale the count for display
                    if destination == "indeterminate":
                        continue
                    did = sids[conversion.get(destination,destination)]
                    ftd["properties"]["intros"][prefix + "raw" + did] = count
                    if count > 5: #debug: if count > 0:
                        sumin = dsumin[sd]
                        invc = dinvc[sd]
                        otvc = dotvc[sd]
                        ftd["properties"]["intros"][prefix + did] = math.log10(count * sumin / invc[destination] / otvc[iid])
                    else:
                        #if there are less than 5 counts, the log correction can do some pretty extreme highlighting
                        #for example, even a single introduction between two distant places may be surprising
                        #but that doesn't mean it should get a lot of emphasis. So we cut off anything with less than 5 introductions total.
                        ftd["properties"]["intros"][prefix + did] = -0.5
        region_file = "regions" + extension[idx] + ".js"
        with open(region_file,"w") as outf:
            print("//data updated via update_js.py",file=outf)
            if idx == 0:
                print('var None = "None";',file=outf)
            print('var introData' + extension[idx] + ' = {"type":"FeatureCollection","features":[',file=outf)
            for propd in svd['features']:
                assert "intros" in propd["properties"]
                print(str(propd) + ",",file=outf)
            print("]};",file=outf)

if __name__ == "__main__":
    from master_backend import parse_setup
    from utils import read_lexicon
    args = parse_setup()
    conversion = read_lexicon(args.lexicon)
    if len(args.geojson) > 1:
        extension = args.region_extension
        extension.insert(0,'')
    else:
        extension = ['']
    if type(args.geojson) == str:
        jsons = list([args.geojson])
    else:
        jsons = args.geojson
    update_js(jsons, conversion, extension)