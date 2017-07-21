#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 17:22:18 2017

<<<<<<< HEAD

Hier komt documentatie tekst

@author: emiel
"""

import os
import pandas as pd
=======
@author: Emiel & Valerie

Documentation text to come
"""

import os
import pandas as ClassPd
>>>>>>> Emiel_Branch
from datetime import datetime as dt
from calendar import monthrange
from datetime import timedelta as timedelta
import calendar

<<<<<<< HEAD
## Reading Data --------------------------------------------- 
def readData(self):

    #READ  data  
    path = r"/Users/emiel/Dropbox/MySharedDocuments/04_RedFox/02_PythonFiles/SM_Database/daily_price"
    os.chdir(path)
    with open('daily_price_'+self.name+'.csv', 'rb') as csvfile:
        self.StockData = pd.read_csv(csvfile)   
#            self.StockData['DateTime'] = pd.to_datetime(self.StockData['price_date'].values).date
        
        self.StockData['DateTime'] = [dt.strptime(x, '%Y-%m-%d') for x in self.StockData['price_date']]
    
=======
def f_ReadCsv(vs_Name, vs_Path="", vs_Prefix="", vs_Postfix=""):
    """
        Description:        reads a csv file into a dataframe
        Input:  
            vs_Name         (part of) the name of the csv file 
                            (for example 'IWM')
            vs_Path         path to the csv file, in case this is different than current directory
            vs_Prefix       prefix of the csv file 
                            (for example in case of 'daily_price_IWM.csv', the prefix is 'daily_price_')
            vs_Postfix      prefix of the csv file
                            (for example in case of 'IWM_daily_price.csv', the postifx is '_daily_price')
        Output:
            df_Data         dataframe with all the csv colums, PLUS a column 'date_time', 
                            which contains datetime version of the 'price_date' column 
    """    
    
    vs_CsvName = ''.join([vs_Path, vs_Prefix, vs_Name, vs_Postfix, '.csv'])
    df_Data = ClassPd.read_csv(vs_CsvName)   
    df_Data['date_time'] = ClassPd.to_datetime(df_Data['price_date'].values).date

    return df_Data    
        

 
>>>>>>> Emiel_Branch
def f_SubtractMonths(self,sourcedate,months):
    month = sourcedate.month - months - 1
    year = int(sourcedate.year + month / 12 )
    month = month % 12 + 1
    day = min(sourcedate.day,calendar.monthrange(year,month)[1])
    
    # find nearest date
    dt_OneMonthAgo = dt(year,month,day)
    dt_OneMonthAgoCorrected = self.f_FindNearestDate(self.StockData['DateTime'],dt_OneMonthAgo)
    
    
    
    return dt_OneMonthAgoCorrected

def f_FindNearestDate(self, items, pivot):
    return min(items, key=lambda x: abs(x - pivot))


def f_MonthDelta(self, arg_date1, arg_date2):
    delta = 0
    d1 = arg_date1
    d2 = arg_date2
    
    while True:
        mdays = monthrange(d1.year, d1.month)[1]
        d1 += timedelta(days=mdays)
        if d1 <= d2:
            delta += 1
        else:
            break
    return delta

def f_CutDates(self, start_date, end_date):
    if (start_date == 'default') or (start_date < self.StockData['price_date'].iloc[0]):
        start_date = self.StockData['price_date'].iloc[0]
    if (end_date == 'default') or (end_date > self.StockData['price_date'].iloc[-1]):
        end_date = self.StockData['price_date'].iloc[-1]

<<<<<<< HEAD
    self.StockData = self.StockData.loc[(self.StockData['price_date'] >= start_date) & (self.StockData['price_date'] <= end_date)].copy()
    
=======
    self.StockData = self.StockData.loc[(self.StockData['price_date'] >= start_date) & (self.StockData['price_date'] <= end_date)].copy()
>>>>>>> Emiel_Branch
