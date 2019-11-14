#requires the following python packages:
#   sqlalchemy
#   to install: "sudo pip install sqlalchemy" in CLI
#
#   mysql-connector
#   to install: "sudo pip install mysql-connector" in CLI
#
#also requires a MySQL or MariaDB database with
#connection parameters defined in a dbconfig.ini file

import pandas as pd
pd.set_option('display.max_rows', 1000) #allow printing lots of rows to screen
pd.set_option('display.max_columns', 1000) #allow printsin lots of cols to screen
pd.set_option('display.width', 1000) #don't wrap lots of columns

import numpy as np
import sqlalchemy
import requests #to pull JSON data
import configparser
import datetime as dt #to track datetime stamps
from dateutil import tz #for timezone handling with datetime dtypes

global_now = dt.datetime.now()
global_now_year = int(global_now.year)

#this is the datetime mask native to the API output
api_mask = '%Y-%m-%dT%H:%M:%S.000Z' 
#this is the datetime mask for readable format
readable_mask = "%a %m/%d/%Y %I:%M%p %Z" #this is a readable format
year_mask = "%Y" #just the year
from_zone = tz.tzutc() #API datetimes are in UTC time
to_zone = tz.tzlocal() #Used for converting to local timezone


config = configparser.ConfigParser()
config.read('./config/dbconfig.ini')

config2 = configparser.ConfigParser()
config2.read('./config/config.ini')

class Database(object):

    def __init__(self):
        self.__connect('CONNECTION')
        self.num_past_years  = int(config2['SCHEDULE']['num past years'])
        self.year_list = list(range(global_now_year-self.num_past_years, global_now_year+1))
        self.team_watch_list = config2['SCHEDULE']['teams to watch'].split('\n')
        self.team_watch_list.pop(0)
    
    def __connect(self, config_header):
        # set connection parameters based on /config/dbconfig.ini
        prefix = config[config_header]['prefix']
        un = config[config_header]['un']
        pw = config[config_header]['pw']
        ip = config[config_header]['ip']
        db = config[config_header]['db']

        #create the connection object    
        con = sqlalchemy.create_engine(
            '{0}{1}:{2}@{3}/{4}'.format(prefix, un, pw, ip, db)
        )

        #clear the connection parameters for security
        un = ''
        pw = ''
        ip = ''
        db = ''

        #establish the connection
        self.connection = con

    def ingest(self, df, table_name, write_type):
        #ensure only acceptable write types are used,
        #and fall back on append in case a bad type
        #is passed.
        if write_type == 'replace':
            pass
        else:
            write_type = 'append'

        #write the df to the db table
        df.to_sql(con=self.connection, name=table_name, if_exists=write_type)
        
    def query(self, sqlstr):
        #run the query against the db
        df = pd.read_sql(sqlstr, con=self.connection)
        
        #drop the first field, which is the db table's
        #index field that is pulled from the sql
        df = df[df.columns[1:]]

        #return the result
        return df
    
    def drop_table(self, table_list):
        table_list = make_list(table_list)
        
        for table_item in table_list:
            self.connection.execute('DROP TABLE ' + table_item + ';')
    
    def table_to_csv(self, tables):
        tables = make_list(tables)
        
        for table_item in tables:
            sqlstr = 'SELECT * FROM ' + table_item
            df = self.query(sqlstr)
            
            path = './csv/'
            file = table_item + '.csv'
            df.to_csv(path + file)

    def add_dtstamp_to_df(self, df):
        df['last_updated'] = global_now
        
        return df

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