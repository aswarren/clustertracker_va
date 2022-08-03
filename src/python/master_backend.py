import argparse, subprocess, sys
from utils import read_lexicon, validate_geojson, insert_extension
from update_js import update_js
from generate_display_tables import generate_display_tables
from prepare_taxonium import prepare_taxonium
from datetime import date, timedelta

def parse_setup():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i","--input",help="Path to the protobuf file to update the website to display.")
    parser.add_argument("-s","--sample_regions",help="Path to a two-column tsv containing sample names and associated regions.")
    parser.add_argument("-d","--date_metadata",help="Path to a two-column tsv containing sample names and collection dates in YYYY-MM-DD format.", default = "")
    parser.add_argument("-j","--geojson", nargs='*', help="Path to a geojson to use. If doing a multi-level analysis (e.g., analyzing the same dataset over multiple geographic levels) additional geojson files can be added; also specify the -e argument to add a region designator to output files.", default = [''])
    parser.add_argument("-e","--region_extension", nargs='*', help="Appends a file name extension (e.g., '_xxxx') to output files in a multi-region-level analysis (i.e., when using two or more geojson files). Specify a file extension for only the 2nd, 3rd, ..., geojson files. Not needed if using only one geojson file.")
    parser.add_argument("-m","--metadata", nargs='*', help="Path to a metadata file matching the targeted protobuf to update the website to display.", default=[''])
    parser.add_argument("-x","--taxonium_fields",help="Comma-separated list of additional metadata fields to include in Taxonium protobuf. Default is 'cluster,region'. Use name of field in metadata file. Do not separate items with spaces.")
    parser.add_argument("-a","--annotation",help="Path to a gene annotation file compatible with TaxoniumTools.")
    parser.add_argument("-t","--threads",type=int,help="Number of threads to use.", default = 4)
    parser.add_argument("-l","--lexicon",help="Optionally, link to a text file containing all names for the same region, one region per row, tab separated.", default = "")
    parser.add_argument("-X","--lookahead",type=int,help="Number to pass to parameter -X of introduce. Increase to merge nested clusters. Default 2", default = 2)
    parser.add_argument("-H","--host",help="Web-accessible link to the current directory for taxonium cluster view.")
    args = parser.parse_args()
    return args

def primary_pipeline(args):
    #assign arguments to variables and set defaults
    #lexicon
    if args.lexicon != "":
        conversion = read_lexicon(args.lexicon)
    else:
        conversion = {}
    #geojson
    if type(args.geojson) == str:
        jsons = list([args.geojson])
    else:
        jsons = args.geojson
    #file name extension
    exts = ['']
    if args.region_extension is not None:
        if type(args.region_extension) == str:
            exts.append(args.region_extension)
        elif type(args.region_extension) == list:
            exts = args.region_extension
            exts.insert(0,'')
    #Taxonium metadata fields
    tax_fields = "cluster,region"
    if args.taxonium_fields is not None:
        tax_fields += "," + args.taxonium_fields
    
    # check that GeoJSON file is formatted as required
    if len(jsons) > 0:
        for jfile in jsons:
            if validate_geojson(jfile) != 1:
                sys.exit("GeoJSON file " + jfile + " does NOT have 'name' field")
    
    #check that file name extension is assigned if using more than one geojson
    if len(jsons) != len(exts):
        sys.exit("Please specify a file name extension for a multiple region analysis")
    
    # Now run pipline
    for i in range(len(jsons)):
        # get file names
        ext = list([exts[i]])
        if isinstance(args.metadata, str):
            mfile = list([args.metadata])
        else:
            mfile = args.metadata
        if i == 0:
            ifile = args.input
            sfile = args.sample_regions
            dfile = args.date_metadata
            ufile = "hardcoded_clusters.tsv"
            cfile = "clusterswapped.tsv"
            ofile = "cview.jsonl.gz"
        else:
            print("Starting the next analysis.")
            ifile = insert_extension(args.input, ext[0])
            sfile = insert_extension(args.sample_regions, ext[0])
            dfile = insert_extension(args.date_metadata, ext[0])
            ufile = insert_extension("hardcoded_clusters.tsv",ext[0])
            mfile = list([insert_extension(mfile[0], ext[0])])
            cfile = insert_extension("clusterswapped.tsv",ext[0])
            ofile = insert_extension("cview.jsonl.gz",ext[0])
        jfile = list([jsons[i]])

        print("Calling introduce.")
        if dfile == "":
            subprocess.check_call("matUtils introduce -i " + ifile + " -s " + sfile + " -u "+ ufile + " -T " + str(args.threads) + " -X " + str(args.lookahead), shell=True)
        else:
            subprocess.check_call("matUtils introduce -i " + ifile + " -s " + sfile + " -M " + dfile + " -u "+ ufile + " -T " + str(args.threads) + " -X " + str(args.lookahead), shell=True)

        print("Updating map display data.")
        update_js(jfile, conversion, ext)

        print("Generating top cluster tables.")
        generate_display_tables(ext)

        print("Preparing taxonium view.")
        prepare_taxonium(sfile, mfile, ext)

        print("Generating JSONL file for Taxonium view.")
        subprocess.check_call("usher_to_taxonium -i " + ifile + " -m "+ cfile + " -c "+ tax_fields + " -o " + ofile + " -g " + args.annotation,shell=True)
    
    print("Process completed; check website for results.")
    
if __name__ == "__main__":
    primary_pipeline(parse_setup())
