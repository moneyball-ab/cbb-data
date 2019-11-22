# College Basketball Data Class Module
#
# Author(s):        TeneoPython01@gmail.com
#
# Purpose:          This script is used to establish the class
#
# Special Notes:    n/a



from pyquery import PyQuery as pq
import pandas as pd
import numpy as np
import datetime as dt



global_now = dt.datetime.now()
global_now_year = int(global_now.year)




def make_list(var):
    if type(var) is not list:
        var = [ var ]

    return(var)

def rename_col(df, old_field_name, new_field_name):
    df = df.rename(
        columns = {
            old_field_name: new_field_name
        }
    )
    
    return df

def drop_col(df, fields_to_drop):
    fields_to_drop = make_list(fields_to_drop)
    
    df = df.drop(
        labels=fields_to_drop,
        axis=1
    )
    
    return df

def reorder_cols(df, new_order_list):
    old_cols_list = df.columns.tolist()
    
    old_order_list = list(range(len(old_cols_list)))
    new_order_list = make_list(new_order_list)
    
    num_old_cols = len(old_cols_list)
    num_new_cols = len(new_order_list)
    
    new_cols_list = []

    count = 0
    for old_item in old_cols_list:
        new_cols_list.append(old_cols_list[new_order_list[count]])
        count = count + 1
    
    df = df[new_cols_list]
    
    return df

def add_dtstamp_to_df(df):
    df['last_updated'] = global_now

    return df


#establish the class
class cbbData(object):

    #__init__() "MAGIC METHOD" sets the current season
    #and then runs a couple methods to set up class
    #properties using the config file and cfb APIs
    def __init__(self):
        self.team_list = []
        self.__load_team_list()
        
        self.season_list = []
        self.__load_season_list()
        
        self.watchlist_schedule = self.getSchedule(self.team_list, self.season_list)
        self.rankings = self.getRankings(self.season_list)
    
    def __load_team_list(self):
        self.team_list.append('wake-forest')
        self.team_list.append('georgia')
    
    def __load_season_list(self):
        self.season_list.append(2019)
        self.season_list.append(2020)
    
    def getSchedule(self, team_list, season_list):
        team_list = make_list(team_list)
        season_list = make_list(season_list)
        
        df = pd.DataFrame()
        
        for team_item in team_list:
            for season_item in season_list:
                #load pq object from schedule page
                url = 'https://www.sports-reference.com/cbb/schools/{}/{}-schedule.html'.format(team_item, str(season_item))
                html_page = pq(url)
                div = 'table#schedule'
                
                #grab the html for the schedule table
                html_str = html_page(div).outerHtml()

                #create a df from the html
                df_temp = pd.read_html(html_str)[0]

                #add fields
                df_temp['season'] = season_item
                df_temp['team'] = team_item
                
                df = df.append(df_temp)
        
        df = df.reset_index(drop=True)

        df = add_dtstamp_to_df(df)
        
        return df
    
    def getRankings(self, season_list):
        season_list = make_list(season_list)
        
        df = pd.DataFrame()

        for season_item in season_list:
            #load pq object from schedule page
            url = 'https://www.sports-reference.com/cbb/seasons/{}.html'.format(str(season_item))
            html_page = pq(url)
            div = 'table#polls'

            #grab the html for the schedule table
            html_str = html_page(div).outerHtml()

            #create a df from the html
            ranking_df = pd.read_html(html_str)[0]
            
            #ADD HERE: if conference field exists, drop it;  it's not in
            #2019 or 2020, but it was in 2018
            
            ranking_df = ranking_df.unstack().reset_index()

            #pivot the publish dates for the ranks from wide to long and rename
            ranking_df = ranking_df[ranking_df['level_0'] != 'School'].merge(ranking_df[ranking_df['level_0'] == 'School'], how='inner', on='level_1')
            ranking_df.columns = ['date','team_index','rank','label','team']
            ranking_df = ranking_df[['date','team','rank']]

            #add fields
            ranking_df['season'] = season_item

            df = df.append(ranking_df)

        df = df.reset_index(drop=True)

        #ranking data only shows month and day of publish date for rankings
        #and since the bball season starts in Nov and ends in Mar, we need
        #to do some work to convert this into a proper date datatype
        df['month'] = df['date'].map(str).apply(lambda x: x.split('/')[0].replace('Pre','11').replace('Final','5')).astype('int').round()
        df['day']   = df['date'].map(str).apply(lambda x: x.split('/')[-1].replace('Pre','1').replace('Final','1')).astype('int').round()
        df['year'] = np.where(df['month'] < 6, df['season'], df['season']-1)
        df['rank_pub_date'] = pd.to_datetime((df.year*10000+df.month*100+df.day).apply(str),format='%Y%m%d')
        df.drop(labels=['month','day','year','date'], axis=1, inplace=True)
        
        #reorder columns
        df = reorder_cols(df, [2,3,0,1])
        
        #convert rank to int
        df['rank'] = df['rank'].replace('-',None).astype(int).round()

        df = add_dtstamp_to_df(df)
        
        return df
    
    
    
    