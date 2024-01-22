#write a script to nest counties in a given GeoJSON file inside a US level GeoJSON file
#usage: python3 place_geojson_counties.py <US level GeoJSON file> <state/county level GeoJSON file>
#example: python3 place_geojson_counties.py us.geojson va.geojson

import json
import sys
import argparse

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
    us = json.load(f)
    state = json.load(f2)

# if remove is defined, remove the state from the US
if args.remove != None:
    #remove the state from the US
    us['features'] = [feature for feature in us['features'] if feature['properties']['name'] != args.remove]

#get the id of the last US feature
us_id = int(us['features'][-1]['id'])
#append each of the state features to the US features
for feature in state['features']:
    us_id += 1
    feature['id'] = us_id
    us['features'].append(feature)

#write the new GeoJSON file
#create mashup file name between US and state
mashup = args.us.split('.')[0] + '_' + args.state.split('.')[0] + '.geojson'
with open(mashup, 'w') as outfile:
    json.dump(us, outfile)