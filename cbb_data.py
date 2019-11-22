# College Basketball Script
#
# Author(s):        TeneoPython01@gmail.com
#
# Purpose:          This script is used to run the program
#
# Special Notes:    n/a

import pandas as pd #to handle data in pandas dataframes
pd.set_option('display.max_rows', 1000) #allow printing lots of rows to screen
pd.set_option('display.max_columns', 1000) #allow printsin lots of cols to screen
pd.set_option('display.width', 1000) #don't wrap lots of columns

import cbbdata as cbb
import dbutil as dbutil

db = dbutil.Database()
cbb_data = cbb.cbbData()

#load the watchlist schedules to the database
db.ingest(cbb_data.watchlist_schedule, 'cbb_schedule', 'replace')
db.ingest(cbb_data.rankings, 'cbb_rankings', 'replace')

#print(cbb_data.watchlist_schedule)
#print(cbb_data.rankings)