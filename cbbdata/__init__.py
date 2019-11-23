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

import lxml
import cssselect

global_now = dt.datetime.now()
global_now_year = int(global_now.year)




def make_list(var):
    if type(var) is not list:
        var = [ var ]

    return(var)

def rename_cols(df, old_field_name, new_field_name):
    old_field_name = make_list(old_field_name)
    new_field_name = make_list(new_field_name)
    
    for counter in range(0,len(old_field_name)):
        df = df.rename(
            columns = {
                old_field_name[counter-1]: new_field_name[counter-1]
            }
        )
    
    return df

def drop_cols(df, fields_to_drop):
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

def update_col_val(df, column_to_update, value_to_replace, new_value):
    if value_to_replace == 'null':
        df[column_to_update] = np.where(df[column_to_update].isnull(), new_value, df[column_to_update])
    else:
        df[column_to_update] = np.where(df[column_to_update] == value_to_replace, new_value, df[column_to_update])
    
    return df

def add_dtstamp_to_df(df):
    df['last_updated'] = global_now

    return df

def get_urls(html_str):

    tree = lxml.html.fromstring(html_str)
    links = tree.cssselect('a')  # or tree.xpath('//a')

    out = []
    for link in links:
        # we use this if just in case some <a> tags lack an href attribute
        if 'href' in link.attrib:
            out.append(link.attrib['href'])
    return out

def df_to_csv(df_list, tablename_list):
    df_list = make_list(df_list)
    tablename_list = make_list(tablename_list)
    
    counter = 0
    for df_item in df_list:
        df_item.to_csv('./csv/' + str(tablename_list[counter]) + '.csv')
        counter = counter + 1

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
        self.teams = self.getTeams()
        
        df_to_csv(
            [self.watchlist_schedule, self.rankings, self.teams],
            ['cbb_schedule','cbb_rankings','cbb_teams']
        )
    
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
        
        df = rename_cols(
            df, 
            ['G', 'Date', 'Time', 'Type', 'Unnamed: 4', 'Opponent', 'Conf', 'Unnamed: 7', 'Tm', 'Opp', 'OT', 'W', 'L', 'Streak', 'Arena'],
            ['team_game_num', 'date', 'time', 'season_type', 'venue_type', 'opponent', 'conference', 'team_result', 'team_pts', 'opponent_pts', 'was_ot', 'win_count', 'loss_count', 'streak', 'venue']
        )
        
        df = update_col_val(df, 'venue_type', 'null', 'Home')
        df = update_col_val(df, 'venue_type', '@', 'Away')
        df = update_col_val(df, 'venue_type', 'N', 'Neutral')
        
        df = update_col_val(df, 'was_ot', 'null', 'Regulation')
        
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
        df = drop_cols(df, ['month','day','year','date'])
        #df.drop(labels=['month','day','year','date'], axis=1, inplace=True)
        
        #reorder columns
        df = reorder_cols(df, [2,3,0,1])
        
        #convert rank to int
        df['rank'] = df['rank'].replace('-',None).astype(int).round()

        df = add_dtstamp_to_df(df)
        
        return df
    
    def getTeams(self):
        df = pd.DataFrame()

        #load pq object from schedule page
        url = 'https://www.sports-reference.com/cbb/schools'
        html_page = pq(url)
        div = 'table#schools'

        #grab the html for the schedule table
        html_str = html_page(div).outerHtml()

        #create a df from the html
        df_scraped = pd.read_html(html_str)[0]
        df_scraped = df_scraped[df_scraped['Rk'] != 'Rk'].reset_index(drop=True)
        
        my_list = get_urls(html_str)

        for i in range(0,len(my_list)):
            my_list[i] = str(my_list[i]).split('/')[-2]

        df_abbreviations = pd.DataFrame(data=my_list, columns=['team_abb'])
        
        df_final = df_scraped.merge(df_abbreviations, how='inner', left_index=True, right_index=True)
        
        df_final = rename_cols(
            df_final, 
            ['Rk','School','City, State', 'From', 'To', 'Yrs', 'G', 'W', 'L', 'W-L%', 'SRS', 'SOS', 'AP', 'CREG', 'CTRN', 'NCAA', 'FF', 'NC'],
            ['team_id','team_and_mascot','team_city_state', 'team_first_yr', 'team_last_yr', 'team_years', 'game_count', 'win_count', 'loss_count', 'win_pct', 'srs_rating', 'str_of_sched', 'final_ap_polls_ranked', 'conf_reg', 'conf_tourn', 'ncaa_appearances', 'final_four_appearances', 'ncaa_champ_won']
        )
        
        df_final = reorder_cols(
            df_final,
            [0,1,18,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17]
        )

        #need to retype the dtypes here

        return df_final