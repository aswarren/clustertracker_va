#write a script to nest counties in a given GeoJSON file inside a US level GeoJSON file
#usage: python3 place_geojson_counties.py <US level GeoJSON file> <state/county level GeoJSON file>
#example: python3 place_geojson_counties.py us.geojson va.geojson

import json
import sys
import argparse
DC_STATEHOOD=1
import us as us_package

#open the US level GeoJSON file
#use argparse to get the files
parser = argparse.ArgumentParser(description='Merge two GeoJSON files.')
parser.add_argument('--us', metavar='us', type=str, help='US level GeoJSON file')
parser.add_argument('--state', metavar='state', type=str, help='state/county level GeoJSON file')
#remove argument uses name of state to remove features from US level GeoJSON file, default is None
parser.add_argument('--remove', metavar='remove', type=str, help='name of state to remove features from US level GeoJSON file', default=None)

args = parser.parse_args()

#get the geojson
with open(args.us) as f, open(args.state) as f2:
    us_map = json.load(f)
    state = json.load(f2)

#deep copy the us_map
us_orig = us_map.copy()

# if remove is defined, remove the state from the US
if args.remove != None:
    #remove the state from the US
    us_map['features'] = [feature for feature in us_map['features'] if feature['properties']['name'] != args.remove]

#get the id of the last US feature
us_id = int(us_map['features'][-1]['id'])
#append each of the state features to the US features
for feature in state['features']:
    us_id += 1
    feature['id'] = us_id
    us_map['features'].append(feature)

#write the new GeoJSON file
#create mashup file name between US and state
mashup = args.us.split('.')[0] + '_' + args.state.split('.')[0] + '.geojson'
with open(mashup, 'w') as outfile:
    json.dump(us_map, outfile)

#write a state_and_county_lexicon.va.txt file in the style of https://github.com/pathogen-genomics/introduction-website/blob/cdph/cdph/data/state_and_county_lexicon.txt
#in two column format name of the county from VA and the shortened versions using the information from the GeoJSON
#open the file
with open('state_and_county_lexicon.va.txt', 'w') as f:
    #write the header
    f.write('county\tshort\n')
    #write the county names and their shortened versions
    for feature in state['features']:
        f.write(feature['properties']['namelsad'] + ',' + feature['properties']['name'] + '\n')
    #now write all the states in the US and their abbreviation, use python library to get the abbreviation
    for feature in us_orig['features']:
        #print(feature['properties']['name'])
        if feature['properties']['name'] == 'District of Columbia':
            f.write(feature['properties']['name'] + ',' + 'DC' + '\n')
        else:
            f.write(feature['properties']['name'] + ',' + us_package.states.lookup(feature['properties']['name']).abbr + '\n')