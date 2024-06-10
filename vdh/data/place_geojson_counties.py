#write a script to nest counties in a given GeoJSON file inside a US level GeoJSON file
#usage: python3 place_geojson_counties.py <US level GeoJSON file> <State Abbreviation> <US counties file>
#example: python3 place_geojson_counties.py  --us us-states.geo.json --state va --counties georef-united-states-of-america-county.geojson

import json
import sys
import argparse
DC_STATEHOOD=1
import us as us_package
from copy import deepcopy


#open the US level GeoJSON file
#use argparse to get the files
parser = argparse.ArgumentParser(description='Merge two GeoJSON files.')
parser.add_argument('--us', metavar='us', type=str, help='US level GeoJSON file')
parser.add_argument('--state', metavar='state', type=str, help='State of interest')
#Argument for "georef-united-states-of-america-county.geojson" file
parser.add_argument('--counties', metavar='counties', type=str, help='File containing all US counties')
#remove argument uses name of state to remove features from US level GeoJSON file, default is None
parser.add_argument('--remove', metavar='remove', type=str, help='name of state to remove features from US level GeoJSON file', default=None)

args = parser.parse_args()

#Find state of interest from command line argument
all_counties_geojson = args.counties
interest_state_abbr = args.state[:2]
interest_state = str(us_package.states.lookup(interest_state_abbr))

#Get the geojson of first CLI argument and stored geojson file
with open(args.us) as f, open(all_counties_geojson) as f2:
    us_map = json.load(f)
    all_counties = json.load(f2)
    

#deep copy the us_map
us_orig = deepcopy(us_map)

# if remove is defined, remove the state from the US
if args.remove != None:
    #remove the state from the US
    us_map['features'] = [feature for feature in us_map['features'] if feature['properties']['name'] != args.remove]
      
#find relevant counties using interest_state and all_counties_geojson
counties = []
for feature in all_counties['features']:
    if feature['properties']['ste_name'][0] == interest_state:
        counties.append(feature)

#get the id of the last US feature
us_id = int(us_map['features'][-1]['id'])
#append each of the state features to the US features
for feature in counties:
    us_id += 1
    feature['id'] = us_id
    #append :{state abbreviation} to the end of the name
    feature['properties']['coty_name_long'][0] += ":" + str(interest_state_abbr).upper()
    us_map['features'].append(feature)

#write the new GeoJSON file
#create mashup file name between US and state
#concetenates '_counties.geojson' to state abbreviation to preserve GeoJSON format
mashup = args.us.split('.')[0] + '_' + str(interest_state_abbr) + '_counties.geojson'
with open(mashup, 'w') as outfile:
    json.dump(us_map, outfile)

#write a state_and_county_lexicon.{state abbreviation}.txt file in similar style to https://github.com/aswarren/clustertracker_va/blob/vdhct/vdh/data/state_and_county_lexicon.va.txt
#Using the GeoJSON file, generates the following three column format: 1) Long County Name + State Abbreviation 2) FIPS Code 3) County name
#open the file
with open(f'state_and_county_lexicon.{interest_state_abbr}.txt', 'w') as f, open(f'county_lexicon.{interest_state_abbr}.txt', 'w') as f2:
    for feature in counties:
        f.write(','.join([feature['properties']['coty_name_long'][0],feature['properties']['coty_code'][0],feature['properties']['coty_name'][0]]) + '\n')
        f2.write(','.join([feature['properties']['coty_name_long'][0],feature['properties']['coty_code'][0],feature['properties']['coty_name'][0]]) + '\n')

    #now write all the states in the US and their abbreviation, use python library to get the abbreviation
    for feature in us_orig['features']:
        #print(feature['properties']['name'])
        if feature['properties']['name'] == 'District of Columbia':
            f.write(feature['properties']['name'] + ',' + 'DC' + '\n')
        else:
            if us_package.states.lookup(feature['properties']['name']) == None:
                print('Could not find the following in US states package: ' + feature['properties']['name'])
            elif us_package.states.lookup(feature['properties']['name']).abbr != None:
                f.write(feature['properties']['name'] + ',' + us_package.states.lookup(feature['properties']['name']).abbr + '\n')