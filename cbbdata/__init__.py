# College Basketball Data Class Module
#
# Author(s):        TeneoPython01@gmail.com
#
# Purpose:          This script is used to establish the class
#
# Special Notes:    n/a



from pyquery import PyQuery as pq
import pandas as pd




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
    
    def __load_team_list(self):
        self.team_list.append('wake-forest')
        self.team_list.append('georgia')
    
    def __load_season_list(self):
        self.season_list.append(2019)
    
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
        
        return df