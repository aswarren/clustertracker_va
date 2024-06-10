#write a script to nest counties in a given GeoJSON file inside a US level GeoJSON file
#usage: python3 place_geojson_counties.py <US level GeoJSON file> <state/county level GeoJSON file>
#example: python3 place_geojson_counties.py us.geojson va.geojson

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
parser.add_argument('--state', metavar='state', type=str, help='state/county level GeoJSON file')
#remove argument uses name of state to remove features from US level GeoJSON file, default is None
parser.add_argument('--remove', metavar='remove', type=str, help='name of state to remove features from US level GeoJSON file', default=None)

args = parser.parse_args()

#Find state of interest from command line argument
all_counties_geojson = 'georef-united-states-of-america-county.geojson'
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
    # print(feature['properties']['ste_name'][0])
    # print(interest_state)
    if feature['properties']['ste_name'][0] == interest_state:
        counties.append(feature)
        # print("success")
# print(counties)

#get the id of the last US feature
us_id = int(us_map['features'][-1]['id'])
#append each of the state features to the US features
for feature in counties:
    us_id += 1
    feature['id'] = us_id
    #swap the name and namelsad attributes so that county name is the primary alias
    # feature['properties']['name'], feature['properties']['alias'] = feature['properties']['namelsad'], feature['properties']['name']
    #append :VA to the end of the name
    # feature['properties']['name'] = feature['properties']['name'] + ':VA'
    us_map['features'].append(feature)

#write the new GeoJSON file
#create mashup file name between US and state
mashup = args.us.split('.')[0] + '_' + args.state.split('.')[0] + '.geojson'
with open(mashup, 'w') as outfile:
    json.dump(us_map, outfile)

#write a state_and_county_lexicon.va.txt file in the style of https://github.com/pathogen-genomics/introduction-website/blob/cdph/cdph/data/state_and_county_lexicon.txt
#in two column format name of the county from VA and the shortened versions using the information from the GeoJSON
#open the file
with open(f'state_and_county_lexicon.{interest_state_abbr}.txt', 'w') as f, open(f'county_lexicon.{interest_state_abbr}.txt', 'w') as f2:
# with open('state_and_county_lexicon.va.txt', 'w') as f, open('county_lexicon.va.txt', 'w') as f2:
    #write the header
    #write the county names and their shortened versions
    #writing this with the expectation that county,fips,longe county name. that name attribute will be used out of the geojson
    for feature in counties:
        # print(feature['properties']['coty_name_long'])
        # print(feature['properties']['coty_fp_code'])
        f.write(','.join([feature['properties']['coty_name_long'][0],feature['properties']['coty_fp_code'],feature['properties']['coty_name'][0]]) + '\n')
        f2.write(','.join([feature['properties']['coty_name_long'][0],feature['properties']['coty_name'][0]]) + '\n')

        #f.write(','.join([feature['properties']['name'],feature['properties']['geoid']]) + '\n')
    #now write all the states in the US and their abbreviation, use python library to get the abbreviation
    for feature in us_orig['features']:
        #print(feature['properties']['name'])
        if feature['properties']['name'] == 'District of Columbia':
            f.write(feature['properties']['name'] + ',' + 'DC' + '\n')
        else:
            if us_package.states.lookup(feature['properties']['name']) == None:
                print('Could not find the following in US states package ' + feature['properties']['name'])
            elif us_package.states.lookup(feature['properties']['name']).abbr != None:
                f.write(feature['properties']['name'] + ',' + us_package.states.lookup(feature['properties']['name']).abbr + '\n')