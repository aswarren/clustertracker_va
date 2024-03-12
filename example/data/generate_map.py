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
import SALib
from collections import defaultdict




#This program converts hardcoded_clusters.tsv form clustertracker to a generalized EpiHiper seeding
#it also creates a chloropleth map of the introductions into the state

#function to graph the average temporal distribution of clusters per week per county
#use earliest_date as the date and region for the county
def get_temporal_distribution(df, df2, lexicon, save_dir, save_name, cases_df=None):

    #create a dictionary of the number of introductions per week per county
    #loop through each row in the dataframe
    #convert the earliest_date column to a datetime object
    #get the earliest year in the earliest_date column
    df['earliest_date'] = pd.to_datetime(df['earliest_date'])
    #create a dictionary of the number of introductions per week per county
    introductions = defaultdict(int) #stores using county name
    introductions_per_week = defaultdict(int)
    
    earliest_year2 = min(df['earliest_date']).year
    earliest_year3 = min(df2['date']).year
    earliest_year = min(earliest_year2, earliest_year3)
    cases_on = cases_df is not None
    if cases_on:
        earliest_date1 = min(cases_df['report_date'])
        earliest_year = min(earliest_date1.year, earliest_year)
        #loop through each row in the cases_df to setup the week
        cases_df['week'] = cases_df['report_date'].apply(lambda x: (x.isocalendar()[1] + (x.year - earliest_year) * 52))
        #group by week and region and take the max of total_cases
        cases_county_week_df = cases_df.groupby(['week', 'locality']).max('total_cases').reset_index()
        #get the case count per week by subtracting from the previous week
        cases_county_week_df['case_count'] = cases_county_week_df.groupby('locality')['total_cases'].diff().fillna(cases_county_week_df['total_cases'])

    df['week'] = df['earliest_date'].apply(lambda x: (x.isocalendar()[1] + (x.year - earliest_year) * 52))
    df2['week'] = df2['date'].apply(lambda x: (x.isocalendar()[1] + (x.year - earliest_year2) * 52))
    #table with week, region, count
    introductions_county_week_df = df.groupby(['week', 'region']).size().reset_index(name='intro_count')
    samples_county_week_df = df2.groupby(['week', 'region']).size().reset_index(name='sample_count')
    #use the lexicon to add fips to the introductions_county_week_df
    introductions_county_week_df['fips'] = introductions_county_week_df['region'].map(lexicon.set_index(0)[1])
    introductions = df.groupby('region').size().to_dict()
    introductions_per_week = df.groupby('week').size().to_dict()

    #merge introductions_county_week_df with samples_county_week_df
    introductions_county_week_df = introductions_county_week_df.merge(samples_county_week_df, on=['week', 'region'], how='left')
    if cases_on:
        #merge introductions_county_week_df with cases_county_week_df
        introductions_county_week_df = introductions_county_week_df.merge(cases_county_week_df, on=['week', 'locality'], how='left')
        #fill NaN values with 0
        introductions_county_week_df = introductions_county_week_df.fillna(0)
        #calculate the ratio of introductions to cases
        introductions_county_week_df['intro_to_cases'] = introductions_county_week_df['intro_count'].astype(float) / introductions_county_week_df['case_count']
        #calculate the ratio of introductions to samples/cases
        introductions_county_week_df['intro_to_coverage'] = introductions_county_week_df['intro_count'].astype(float) \
            / (introductions_county_week_df['sample_count'].astype(float) / introductions_county_week_df['case_count'])
    #create a list of the weeks
    weeks = list(range(1, int(max(introductions_per_week.keys())) + 1))
    #create a list of the number of introductions per week
    num_introductions = [introductions_per_week[week] for week in weeks]
    #create a bar plot of the number of introductions per week
    plt.bar(weeks, num_introductions)
    plt.xlabel('Week')
    plt.ylabel('Number of introductions')
    plt.title('Temporal distribution of introductions')
    #save figure
    plt.savefig(save_dir + '/' + save_name + '_introductions_temporal.png', bbox_inches='tight')
    plt.close()
    #create plot of the number of samples per week from df2
    samples_per_week = df2.groupby('week').size().to_dict()
    #create a list of the number of samples per week
    num_samples = [samples_per_week[week] for week in weeks]
    #create a bar plot of the number of samples per week
    plt.bar(weeks, num_samples)
    plt.xlabel('Week')
    plt.ylabel('Number of samples')
    plt.title('Temporal distribution of samples')
    #save figure
    plt.savefig(save_dir + '/' + save_name + '_samples_temporal.png', bbox_inches='tight')
    plt.close()
    return introductions, introductions_county_week_df


#given the state fips code, return the population of the state by county
def get_state_pop(state_fips):
    # Read the CSV file from the Census Bureau's website
    state_fips=51
    df = pd.read_csv("https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/counties/totals/co-est2020-alldata.csv", encoding = "latin-1")

    # Filter the data by the FIPS code (column name: STATE and COUNTY)
    # For example, to get the population size for the state of VA (FIPS code: 51)
    state_df = df[df["STATE"] == int(state_fips)]

    # Extract the population size (column name: POPESTIMATE2020) and the county name (column name: CTYNAME) for each county
    #state_pop = va_df[["POPESTIMATE2020", "CTYNAME"]]

    # Print the results
    return state_df

#perform sobol sensitivity analysis on a 2*std deviation range of parameters to determine the behavior of the calculation
def sobol_sensitivity_analysis(mean_introductions, std_dev_introductions, mean_samples, std_dev_samples, mean_population, std_dev_population):
    from SALib.util.problem import ProblemSpec

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
        ratio = float(num_introd) / ((float(county_samples) * 100000) / float(county_pop))
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
    Si = sobol.analyze(problem, np.array(output_values))
    #Print the first-order sensitivity indices
    print(Si['S1'])
    #Print the total-order sensitivity indices
    print(Si['ST'])

#main function reads in the hardcoded_clusters.tsv file, filters the table down to the lexicon selection in the first column using the region column in the hardcoded_clusters.tsv file

def main(hardcoded, clusterswapped, lexicon_file, geojson, save_dir, save_name, cases_file=None):

    #read in the hardcoded_clusters.tsv file
    df = pd.read_csv(hardcoded, sep='\t', header=0, parse_dates=['earliest_date'])
    df2 = pd.read_csv(clusterswapped, sep='\t', header=0)
    #read in the lexicon file
    lexicon = pd.read_csv(lexicon_file, sep=',', header=None)
    #filter the table down to the lexicon selection in the first column using the region column in the hardcoded_clusters.tsv file
    
    #the lexicon doesn't introduce '_' like apparently the cluster tracker table does
    df_selected = df[df['region'].str.replace('_',' ').isin(lexicon[0])]

    df_selected['region'] = df_selected['region'].str.replace('_',' ')
    
    #filter df_selected to those rows that do not have ":VA" as substring in the inferred_origin column
    #this hack for VA will need to be generalized for other regions
    df_selected = df_selected[~df_selected['inferred_origin'].str.contains(':VA')]

    cases_df = None
    earliest_year = None
    #get the case data from file if passed 
    #expected format report_date,fips,locality,vdh_health_district,total_cases,hospitalizations,deaths
    if cases_file:
        cases_df = pd.read_csv(cases_file, header=0, parse_dates=['report_date'])

        


    
    
    #get state population data from census
    state_df=get_state_pop(51)

    introductions, introductions_county_week_df = get_temporal_distribution(df_selected, lexicon, save_dir, save_name, earliest_year, cases_df)

    #using the counties in the region column in df_selected and the counties in the name(s) attribute in a geojson generate a chlopleth map of the number of rows in df_selected per county
    #read in the geojson file
        #read in the geojson file
    
    #get the total number of samples which have a :VA in the region column from df2
    total_va_samples = df2[df2['region'].fillna('').str.contains(':VA')].shape[0]
    #get the total number of samples which have a :VA in the region column from df2 per region
    total_va_samples_per_region = df2[df2['region'].fillna('').str.contains(':VA')].groupby('region').size()

    gdf = gpd.read_file(args.geojson)
    
    
    #get the total number of introductions
    total_introductions = sum(introductions.values())
   

    #using the ratio of introductions to samples calculate the z-score for each county
    ratios = {}
    county_pops={}
    ratios2 = {}
    
    for county, num_introd in introductions.items():
        #get the total number of samples from the region
        county_samples = total_va_samples_per_region[county]
        #get the fips code from the lexicon 2nd column and store it in the 
        fips = int(lexicon[lexicon[0] == county][1].values[0])
        #use the fips code to get the population of the county from the state_df
        #fips = int(gdf[gdf['name'] == county]['countyfp'].values[0])
        county_pop = state_df[state_df['COUNTY'] == fips]['POPESTIMATE2020'].values[0]
        county_pops[county]=county_pop
        #calculate samples per 100k people
        county_samples_per_100k = (float(county_samples) / float(county_pop)) * 100000
        ratios[county] = float(num_introd) / county_samples_per_100k
        ratios2[county] = float(num_introd) / county_samples

    #print the mean and std. deviation of the populations, samples, and introductions
    #get the mean and std. dev of the ratios
    mean_ratio100k = np.mean(list(ratios.values()))
    std_dev_ratio100k = np.std(list(ratios.values()))
    mean_ratio = np.mean(list(ratios2.values()))
    std_dev_ratio = np.std(list(ratios2.values()))
    mean_introductions = np.mean(list(introductions.values()))
    std_dev_introductions = np.std(list(introductions.values()))
    mean_samples = np.mean(list(total_va_samples_per_region.values))
    std_dev_samples = np.std(list(total_va_samples_per_region.values))
    mean_population = np.mean(list(state_df['POPESTIMATE2020'].values))
    std_dev_population = np.std(list(state_df['POPESTIMATE2020'].values))

    print(f"all samples: {total_va_samples} available after processing by clustertracker")
    print(f"filtered samples: {len(df_selected)}")
    print('mean introductions/samples:', mean_ratio100k)
    print('std. dev introductions/samples:', std_dev_ratio100k)
    print('mean introductions:', mean_introductions)
    print('std. dev introductions:', std_dev_introductions)
    print('mean samples:', mean_samples)
    print('std. dev samples:', std_dev_samples)
    print('mean population:', mean_population)
    print('std. dev population:', std_dev_population)
    
    sobol_sensitivity_analysis(mean_introductions, std_dev_introductions, mean_samples, std_dev_samples, mean_population, std_dev_population)
    

    #calculate the z-score for each county using the mena and std. dev
    z_scores = {}
    z_score_intro = {}
    z_score_pop = {}
    z_score_samples = {}
    z_score_ratio2 = {} #introductions per sample
    for county, ratio in ratios.items():
        county_pop=state_df[state_df['COUNTY'] == fips]['POPESTIMATE2020'].values[0]
        z_scores[county] = (ratio - mean_ratio100k) / std_dev_ratio100k
        z_score_intro[county] = (introductions[county] - mean_introductions) / std_dev_introductions
        z_score_pop[county] = (county_pops[county] - mean_population) / std_dev_population
        z_score_samples[county] = (total_va_samples_per_region[county] - mean_samples) / std_dev_samples
        z_score_ratio2[county] = (ratios2[county] - mean_ratio) / std_dev_ratio

    #add the introductions to the gdf
    gdf['introductions'] = gdf['name'].map(introductions)
    #add the z-scores to the gdf
    gdf['z_score_force'] = gdf['name'].map(z_scores) 
    gdf['z_score_intro'] = gdf['name'].map(z_score_intro)
    gdf['z_score_pop'] = gdf['name'].map(z_score_pop)
    gdf['z_score_samples'] = gdf['name'].map(z_score_samples)
    gdf['samples'] = gdf['name'].map(total_va_samples_per_region)
    gdf['z_score_ratio2'] = gdf['name'].map(z_score_ratio2)


    #if cases_file is not None, use the introductions_county_week_df to create a chloropleth map of the z-score of ratio of introduction to cases
    if cases_file:
        #calculate the mean and std. dev of the introductions to cases
        mean_intro_to_cases = np.mean(introductions_county_week_df['intro_to_cases'])
        std_dev_intro_to_cases = np.std(introductions_county_week_df['intro_to_cases'])
        #calculate the z-score for each county
        z_score_intro_to_cases = {}
        county_mean_intro_to_cases = introductions_county_week_df.groupby('region').mean('intro_to_cases').to_dict()
        for county, cur_mean in county_mean_intro_to_cases.items():
            z_score_intro_to_cases[county] = (cur_mean - mean_intro_to_cases) / std_dev_intro_to_cases
        #add the z-scores to the gdf
        gdf['intro_to_cases'] = gdf['name'].map(z_score_intro_to_cases)
        #create the chloropleth map for z_score_intro
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        #center the map and zoom on VA
        gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
        gdf.plot(column='intro_to_cases', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
        ax.axis('off')
        #add a colorbar
        norm = colors.Normalize(vmin=gdf['intro_to_cases'].min(), vmax=gdf['intro_to_cases'].max())
        cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
        cbar.set_label('Per county Z-score of introductions / cases')
        #add title
        ax.set_title(f"Z-score of introductions / cases: using {len(df_selected)} samples")
        #save the chloropleth map
        plt.savefig(save_dir + '/' + save_name + '_z_score_intro_to_cases.png', bbox_inches='tight')
        plt.close()


    #create the chloropleth map for z_score_force
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    #gdf.plot(column='introductions', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8')
    gdf.plot(column='z_score_force', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    #norm = colors.Normalize(vmin=gdf['introductions'].min(), vmax=gdf['introductions'].max())
    norm = colors.Normalize(vmin=gdf['z_score_force'].min(), vmax=gdf['z_score_force'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Per county Z-score of introductions / (samples per 100k)')
    #add title
    ax.set_title(f"Per county Z-score of introductions / (samples per 100k): using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '.png', bbox_inches='tight')
    plt.close()

    #create chloropleth map for z_score_ratio2
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    gdf.plot(column='z_score_ratio2', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    norm = colors.Normalize(vmin=gdf['z_score_ratio2'].min(), vmax=gdf['z_score_ratio2'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Per county Z-score of introductions / samples')
    #add title
    ax.set_title(f"Per county Z-score of introductions / samples: using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '_z_score_ratio2.png', bbox_inches='tight')
    plt.close()


    #create the chloropleth map for introductions
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    gdf.plot(column='introductions', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    norm = colors.Normalize(vmin=gdf['introductions'].min(), vmax=gdf['introductions'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Number of introductions')
    #add title
    ax.set_title(f"Introductions: using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '_introductions.png', bbox_inches='tight')
    plt.close()

    #create the chloropleth map for z_score_intro
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    gdf.plot(column='z_score_intro', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    norm = colors.Normalize(vmin=gdf['z_score_intro'].min(), vmax=gdf['z_score_intro'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Per county Z-score of introductions')
    #add title
    ax.set_title(f"Z-score of introductions: using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '_z_score_intro.png', bbox_inches='tight')
    plt.close()

    #create the chloropleth map for z_score_pop
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    gdf.plot(column='z_score_pop', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    norm = colors.Normalize(vmin=gdf['z_score_pop'].min(), vmax=gdf['z_score_pop'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Per county Z-score of population')
    #add title
    ax.set_title(f"Z-score of population: using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '_z_score_pop.png', bbox_inches='tight')
    plt.close()

    #create the chloropleth map for z_score_samples
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    gdf.plot(column='z_score_samples', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    norm = colors.Normalize(vmin=gdf['z_score_samples'].min(), vmax=gdf['z_score_samples'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Per county Z-score of samples')
    #add title
    ax.set_title(f"Z-score of samples: using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '_z_score_samples.png', bbox_inches='tight')
    plt.close()

    #create the chloropleth map for samples
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    #center the map and zoom on VA
    gdf = gdf.cx[-83.6753:-75.1664, 36.5408:39.4660]
    gdf.plot(column='samples', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='k')
    ax.axis('off')
    #add a colorbar
    norm = colors.Normalize(vmin=gdf['samples'].min(), vmax=gdf['samples'].max())
    cbar = fig.colorbar(cm.ScalarMappable(norm=norm, cmap='OrRd'), ax=ax, orientation='horizontal', fraction=0.05, pad=0.05)
    cbar.set_label('Number of samples')
    #add title
    ax.set_title(f"Samples: using {len(df_selected)} samples")
    #save the chloropleth map
    plt.savefig(save_dir + '/' + save_name + '_samples.png', bbox_inches='tight')
    plt.close()




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This program converts hardcoded_clusters.tsv to a generalized EpiHiper seeding and creates a chloropleth map of the introductions into the state of VA with mean and std. dev calculated per variant per county")
    parser.add_argument("-i", "--input", help="The input hardcoded_clusters.tsv file", required=True)
    parser.add_argument("-j", "--input2", help="The input clusterswapped.tsv file", required=True)
    parser.add_argument("-l", "--lexicon", help="The input lexicon file", required=True)
    parser.add_argument("-d", "--save_dir", help="The output directory", required=True)
    parser.add_argument("-n", "--save_name", help="The output name", required=True)
    parser.add_argument("-c", "--cases", default=None, help="The input cases file", required=False)
    #option for the geojson to use for the chloropleth map
    parser.add_argument("-g", "--geojson", help="The input geojson file", required=True)
    args = parser.parse_args()
    main(args.input, args.input2, args.lexicon, args.geojson, args.save_dir, args.save_name, cases_file=args.cases)
