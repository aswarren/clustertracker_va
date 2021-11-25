import argparse
from update_js import update_js
from generate_display_tables import generate_display_tables
from prepare_taxonium import prepare_taxonium
from datetime import date, timedelta
import subprocess
import json

def read_lexicon(lfile):
    conversion = {}
    with open(lfile) as inf:
        for entry in inf:
            spent = entry.strip().split(",")
            for alternative in spent:
                conversion[alternative] = spent[0]
                # automatically create an all uppercase lexicon alternative
                if alternative != alternative.upper():
                    conversion[alternative.upper()] = spent[0]
    return conversion

def parse_setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",help="Path to the protobuf file to update the website to display.")
    parser.add_argument("-s","--sample_regions",help="Path to a two-column tsv containing sample names and associated regions.")
    parser.add_argument("-j","--geojson",help="Path to a geojson to use.")
    parser.add_argument("-m","--metadata",help="Path to a metadata file matching the targeted protobuf to update the website to display.")
    parser.add_argument("-f","--reference",help="Path to a reference fasta.")
    parser.add_argument("-a","--annotation",help="Path to a gtf annotation matching the reference.")
    parser.add_argument("-t","--threads",type=int,help="Number of threads to use.", default = 4)
    parser.add_argument("-l","--lexicon",help="Optionally, link to a text file containing all names for the same region, one region per row, tab separated.", default = "")
    parser.add_argument("-X","--lookahead",type=int,help="Number to pass to parameter -X of introduce. Increase to merge nested clusters. Default 2", default = 2)
    parser.add_argument("-H","--host",help="Web-accessible link to the current directory for taxonium cluster view.",default="https://storage.googleapis.com/ucsc-gi-cdph-bigtree/")
    args = parser.parse_args()
    return args

def validate_geojson(gfile):
    #TO DO: need to  ensure geo json feature name is called "name"
    f = open(gfile)
    geojson_lines = json.load(f)
    f.close()
    for feature in geojson_lines["features"]:
        if "name" in feature["properties"]:
            #print("GeoJSON file has 'name' field") ## DEBUG
            return 1
        else:
            #print("GeoJSON file DOES NOT have 'name' field") ##DEBUG
            return 0

def primary_pipeline(args):
    pbf = args.input
    mf = args.metadata
    if args.lexicon != "":
        conversion = read_lexicon(args.lexicon)
    else:
        conversion = {}
    # print(conversion)
    print("Calling introduce.")
    subprocess.check_call("matUtils introduce -i " + args.input + " -s " + args.sample_regions + " -u hardcoded_clusters.tsv -T " + str(args.threads) + " -X " + str(args.lookahead), shell=True)
    print("Updating map display data.")
    update_js(args.geojson, conversion)
    print("Generating top cluster tables.")
    generate_display_tables(conversion, host = args.host)
    print("Preparing taxonium view.")
    prepare_taxonium(args.sample_regions, mf)
    print("Generating viewable pb.")
    subprocess.check_call("matUtils extract -i " + args.input + " -M clusterswapped.tsv -F cluster,region,paui,name,gisaid_accession --write-taxodium cview.pb --title Cluster-Tracker -g " + args.annotation + " -f " + args.reference,shell=True)
    print("Process completed; check website for results.")

if __name__ == "__main__":
    primary_pipeline(parse_setup())
