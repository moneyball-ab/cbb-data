# College Basketball Script
#
# Author(s):        TeneoPython01@gmail.com
# Developed:        10/11/2019
# Last Updated:     10/11/2019
#
# Purpose:          This script is used to run the program
#
# Special Notes:    This is an early protoype

import pandas as pd #to handle data in pandas dataframes
pd.set_option('display.max_rows', 1000) #allow printing lots of rows to screen
pd.set_option('display.max_columns', 1000) #allow printsin lots of cols to screen
pd.set_option('display.width', 1000) #don't wrap lots of columns

import requests #to pull data
import numpy as np #to do conditional pandas operations

#define team and last year of the season of interest
#e.g., 2018-2019 season is last_year = 2019
team = 'Wake Forest'
last_year = 2019

#format team string to be compatible with URL request
team = team.lower().replace(' ','-')

#request URL with schedule data
r = requests.get(
    'https://www.sports-reference.com/cbb/schools/' +
    team +
    '/' +
    str(last_year) +
    '-schedule.html'
).text

#load the HTML table data into pandas dataframe
df = pd.DataFrame()
df = pd.read_html(r)[1]

print(
    df[
        [
            'G',
            'Date',
            'Time',
            'Type',
            'Opponent',
            'Unnamed: 7',
            'Tm',
            'Opp'        
        ]
    ]
)