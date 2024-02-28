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
    z_scores = {}
    for county, num_introd in introductions.items():
        #get the total number of samples from the region
        total_samples = total_va_samples_per_region[county]
        #calculate the z-score
        z_scores[county] = (num_introd - total_samples * total_introductions / total_va_samples) / np.sqrt(total_samples * total_introductions / total_va_samples)
    #add the z-scores to the gdf
    gdf['z_scores'] = gdf['name'].map(z_scores)
    #add the introductions to the gdf
    gdf['introductions'] = gdf['name'].map(introductions)
    #create the chloropleth map
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    #gdf.plot(column='introductions', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8')
    gdf.plot(column='z_scores', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8')
    ax.axis('off')
    #add a colorbar
    #norm = colors.Normalize(vmin=gdf['introductions'].min(), vmax=gdf['introductions'].max())
    norm = colors.Normalize(vmin=gdf['z_scores'].min(), vmax=gdf['z_scores'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Number of introductions')
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
