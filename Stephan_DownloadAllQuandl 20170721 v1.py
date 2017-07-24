
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 18:27:13 2017

@author: Stephan
"""
"""

-------------------------------------------------------------------
PURPOSE OF THIS FILE:
    download all quandl data (listed in a file, could be incomplete) 
    into a csv so that i don't have to download everything every time.

-----------------------------------------------


"""
import numpy as np
import pandas as pd
import datetime # https://stackoverflow.com/questions/12030187/getting-current-date-and-current-time-only-respectively
from downloader import WebsiteData
import os

#import quandl 
#from dbaccess import DatabaseManipulation as dbM
#import matplotlib.pyplot as plt
#import talib

########################### ALTERNATIVE #################################
#quandl.ApiConfig.api_key = 'WvH2nhazmijXYvd8RPvB'
#mydata = quandl.get("EIA/PET_RWTC_D", collapse="monthly")
#
#all_data = quandl.get('WIKI/PRICES')
#########################################################################

########################### WORKING #################################

ClassWebsiteData = WebsiteData()
#b = ClassWebsiteData.get_quandl_data('AAPL','NYSE') #checked, downloads the right stuff.
#a.get_quandl_data

# Create path to save CSVs in - https://stackoverflow.com/questions/16211703/how-to-make-a-folder-in-python-mkdir-makedirs-doesnt-do-this-right?rq=1 
Current_Path = os.getcwd()
s_Data_Folder_Name = "Quandl_WIKI_Data"
if not os.path.isdir(''.join([os.getcwd(), '\\', s_Data_Folder_Name])): # check if this folder already exists, if not, create it
    os.mkdir(s_Data_Folder_Name)

# get names of all CSV's to download
ticker_filename = 'Quandl-WIKI-datasets-codes'
#db_path = ://Quandl-WIKI-datasets-codes.csv
df_info = pd.read_csv("Quandl-WIKI-datasets-codes_DOWNED20170721_v1.csv") # file should be in current working directory

# ------EXTRA INFO AND INTERESTING TID BITS. IF ANYTHING DOES NOT WORK LOOK HERE  ---------
# how to add a row entry to dataframe: db_info.loc[1,'Downloaded on Date'] = 5
# update download list to say that it's downloaded that entry
# df_info.loc[2,'Downloaded on Date'] = datetime.datetime.now().strftime("%Y%m%d")  # https://stackoverflow.com/questions/12030187/getting-current-date-and-current-time-only-respectively

# check if this works:
#if df_info.loc[2,'Downloaded on Date'] == datetime.datetime.now().strftime("%Y%m%d"):
#    print 'yes yes'
#else:
#    print 'no no'

### FOR 20170721 ONLY:
##bla = os.listdir('C:\DATA\OneDrive\My Documents\GitHub\RedFoxQT\Quandl_WIKI_Data')
#df_Downed = pd.read_csv("Quandl-WIKI-datasets-codes_DOWNED20170721vRough.csv") # file should be in current working directory
#df_info['Downloaded on Date'] = 'not-downed'
## check if this current Ticker has already been downloaded:
#for row, vs_Ticker in enumerate(df_info.loc[:, 'Ticker']):
#    if any(df_Downed['Downloaded 20170721'] == df_info.loc[row, 'Ticker']):
#        df_info.loc[row,'Downloaded on Date'] = datetime.datetime.now().strftime("%Y%m%d")
### check:
##if df_info.loc[3000, 'Downloaded on Date'] == 'not-downed':
##    print 'yes'

# -------------------------------------------------------------------------------------

# add a NaN column to the list of tickers that we want to download so that we can fill that column later once the ticker has been downloaded:
if not 'Downloaded on Date' in df_info.columns:
    df_info['Downloaded on Date'] = np.nan

for row, vs_Ticker in enumerate(df_info.loc[:, 'Ticker']): # reads over the column called 'Ticker'

    #print vs_Ticker
    
    # check if this Ticker was not downloaded already today. 
    if df_info.loc[row, 'Downloaded on Date'] == 'not-downed' :
    # to check the exact date: not df_info.loc[row, 'Downloaded on Date'] == datetime.datetime.now().strftime("%Y%m%d"): 
    
        # if not yet downloaded today, give it a try
        try: 
            # download from Quandl into a dataframe:
            df_Security = ClassWebsiteData.get_quandl_data(vs_Ticker) # downloads data from Quandl and puts it in a dataframe format (Valerie made it)
            ps_Date = pd.to_datetime(df_Security['Date'])
            
            # save to csv
            #dbM.save_csv('name', df_Security) #uses Valerie's code to save dataframe to a CSV
            path = ''.join([os.getcwd(), '\\', s_Data_Folder_Name, '\\', vs_Ticker, '.csv'])
            df_Security.to_csv(path)
            
            # update download list to say that it's downloaded that entry
            df_info.loc[row,'Downloaded on Date'] = datetime.datetime.now().strftime("%Y%m%d")  # https://stackoverflow.com/questions/12030187/getting-current-date-and-current-time-only-respectively
            
        except ValueError:
            print 'Current Ticker threw a ValueError: No Stock Exchange given, needed for this source. Ticker:', vs_Ticker
            df_info.loc[row, 'Downloaded on Date'] = 'ValueError'
            pass

df_info.to_csv("Quandl-WIKI-datasets-codes_DOWNED20170721_v1.csv")
