#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import seaborn as sns
import os
import sys
import re
import argparse
import datetime
from collections import defaultdict
from shapely.geometry import Point
from shapely.geometry import Polygon
from matplotlib.colors import ListedColormap
from matplotlib.colors import Normalize
from matplotlib import cm
from matplotlib import colorbar
from matplotlib import ticker
from matplotlib import patches
from matplotlib import colors



#This program converts hardcoded_clusters.tsv form clustertracker to a generalized EpiHiper seeding
#it also creates a chloropleth map of the introductions into the state

def get_state_pop(state_fips):
    # Read the CSV file from the Census Bureau's website
    import pandas as pd
    state_fips=51
    df = pd.read_csv("https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv", encoding = "latin-1")

    # Filter the data by the FIPS code (column name: STATE and COUNTY)
    # For example, to get the population size for the state of VA (FIPS code: 51)
    state_df = df[df["STATE"] == int(state_fips)]

    # Extract the population size (column name: POPESTIMATE2020) and the county name (column name: CTYNAME) for each county
    #state_pop = va_df[["POPESTIMATE2020", "CTYNAME"]]

    # Print the results
    print(state_df.head())
    return state_df

#perform sobol sensitivity analysis on a 2*std deviation range of parameters to determine the behavior of the calculation
def sobol_sensitivity_analysis(mean_introductions, std_dev_introductions, mean_samples, std_dev_samples, mean_population, std_dev_population):
    from SALib.problem import ProblemSpec

    problem = ProblemSpec({
    'names': ['num_introd', 'county_samples', 'county_pop'], #input parameter names
    'bounds': [[mean_introductions - (2*std_dev_introductions), mean_introductions + (2*std_dev_introductions)], \
               [mean_samples - (2 * std_dev_samples), mean_samples + (2 * std_dev_samples)],\
                  [mean_population - (2* std_dev_population), mean_population + (2*std_dev_population)]], #input parameter ranges
    'outputs': ['z_scores'] #output variable name
    })

    from SALib.sample import latin

    #Generate 1000 samples using LHS
    param_values = latin.sample(problem, 1000)
    #Initialize an empty list to store the output values
    output_values = []
    ratios = []
    #Loop through each sample
    for i in range(len(param_values)):
    #Get the sampled values of the input parameters
        num_introd = param_values[i][0]
        county_samples = param_values[i][1]
        county_pop = param_values[i][2]

        #Calculate the ratio of introductions to samples per population
        ratio = float(num_introd) / (float(county_samples) / float(county_pop))
        ratios.append(ratio)
    mean= np.mean(ratios)
    std_dev = np.std(ratios)

    for ratio in ratios:
        #Calculate the z-score using the mean and std. dev of the ratios
        z_score = (ratio - mean) / std_dev
        #Append the output value to the list
        output_values.append(z_score)

    from SALib.analyze import sobol
    #Perform the Sobol analysis
    Si = sobol.analyze(problem, output_values)
    #Print the first-order sensitivity indices
    print(Si['S1'])
    #Print the total-order sensitivity indices
    print(Si['ST'])

#main function reads in the hardcoded_clusters.tsv file, filters the table down to the lexicon selection in the first column using the region column in the hardcoded_clusters.tsv file

def main(hardcoded, clusterswapped, lexicon, geojson, save_dir, save_name):

    #read in the hardcoded_clusters.tsv file
    df = pd.read_csv(hardcoded, sep='\t', header=0)
    df2 = pd.read_csv(clusterswapped, sep='\t', header=0)
    #read in the lexicon file
    lexicon = pd.read_csv(args.lexicon, sep=',', header=None)
    #filter the table down to the lexicon selection in the first column using the region column in the hardcoded_clusters.tsv file
    df_selected = df[df['region'].isin(lexicon[0])]
    
    #filter df_selected to those rows that do not have ":VA" as substring in the inferred_origin column
    #this hack for VA will need to be generalized for other regions
    df_selected = df_selected[~df_selected['inferred_origin'].str.contains(':VA')]
    
    #get state population data from census
    state_df=get_state_pop(51)

    #using the counties in the region column in df_selected and the counties in the name(s) attribute in a geojson generate a chlopleth map of the number of rows in df_selected per county
    #read in the geojson file
        #read in the geojson file
    
    #get the total number of samples which have a :VA in the region column from df2
    total_va_samples = df2[df2['region'].fillna('').str.contains(':VA')].shape[0]
    #get the total number of samples which have a :VA in the region column from df2 per region
    total_va_samples_per_region = df2[df2['region'].fillna('').str.contains(':VA')].groupby('region').size()

    gdf = gpd.read_file(args.geojson)
    #create a dictionary of the number of introductions per county
    introductions = defaultdict(int)
    for index, row in df_selected.iterrows():
        introductions[row['region']] += 1
    
    #get the total number of introductions
    total_introductions = sum(introductions.values())
    #using the ratio of introductions to samples calculate the z-score for each county
    ratios = {}
    for county, num_introd in introductions.items():
        #get the total number of samples from the region
        county_samples = total_va_samples_per_region[county]
        #use the fips code to get the population of the county from the state_df
        fips = int(gdf[gdf['name'] == county]['countyfp'].values[0])
        county_pop = state_df[state_df['COUNTY'] == fips]['POPESTIMATE2020'].values[0]

        ratios[county] = float(num_introd) / (float(county_samples) / float(county_pop))

        #use the county variable to get the gdf record using the name attribute and construct the fips from the countyfp and statefp attributes
        #get the fips code for the county

        #get the population of the county

    #print the mean and std. deviation of the populations, samples, and introductions
    #get the mean and std. dev of the ratios
    mean = np.mean(list(ratios.values()))
    std_dev = np.std(list(ratios.values()))
    mean_introductions = np.mean(list(introductions.values()))
    std_dev_introductions = np.std(list(introductions.values()))
    mean_samples = np.mean(list(total_va_samples_per_region.values()))
    std_dev_samples = np.std(list(total_va_samples_per_region.values()))
    mean_population = np.mean(list(state_df['POPESTIMATE2020'].values()))
    std_dev_population = np.std(list(state_df['POPESTIMATE2020'].values()))

    print('mean introductions/samples:', mean)
    print('std. dev introductions/samples:', std_dev)
    print('mean introductions:', mean_introductions)
    print('std. dev introductions:', std_dev_introductions)
    print('mean samples:', mean_samples)
    print('std. dev samples:', std_dev_samples)
    print('mean population:', mean_population)
    print('std. dev population:', std_dev_population)
    
    sobol_sensitivity_analysis(mean_introductions, std_dev_introductions, mean_samples, std_dev_samples, mean_population, std_dev_population)
    

    #calculate the z-score for each county using the mena and std. dev
    z_scores = {}
    for county, ratio in ratios.items():
        z_scores[county] = (ratio - mean) / std_dev

    #add the z-scores to the gdf
    gdf['z_scores'] = gdf['name'].map(z_scores)
    #add the introductions to the gdf
    gdf['introductions'] = gdf['name'].map(introductions)
    #create the chloropleth map
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    #gdf.plot(column='introductions', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8')
    gdf.plot(column='z_scores', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    #norm = colors.Normalize(vmin=gdf['introductions'].min(), vmax=gdf['introductions'].max())
    norm = colors.Normalize(vmin=gdf['z_scores'].min(), vmax=gdf['z_scores'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Z-score of introductions/samples')
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '.png', bbox_inches='tight')
    plt.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program converts hardcoded_clusters.tsv to a generalized EpiHiper seeding and creates a chloropleth map of the introductions into the state of VA with mean and std. dev calculated per variant per county")
    parser.add_argument("-i", "--input", help="The input hardcoded_clusters.tsv file", required=True)
    parser.add_argument("-j", "--input2", help="The input clusterswapped.tsv file", required=True)
    parser.add_argument("-l", "--lexicon", help="The input lexicon file", required=True)
    parser.add_argument("-d", "--save_dir", help="The output directory", required=True)
    parser.add_argument("-n", "--save_name", help="The output name", required=True)
    #option for the geojson to use for the chloropleth map
    parser.add_argument("-g", "--geojson", help="The input geojson file", required=True)
    args = parser.parse_args()
    main(args.input, args.input2, args.lexicon, args.geojson, args.save_dir, args.save_name)
