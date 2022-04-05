import json #for validate_geojson

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

def validate_geojson(gfile):
    f = open(gfile)
    geojson_lines = json.load(f)
    f.close()
    for feature in geojson_lines["features"]:
        if "name" in feature["properties"]:
            return 1
        else:
            return 0

def insert_extension(fname, extension):
    if isinstance(fname, list):
        f = fname[0]
    else:
        f = fname
    parts = f.rpartition('.')
    if parts[1] == "":
        newname = parts[2] + extension
    else:
        newname = parts[0] + extension + parts[1] + parts[2]
    return newname
