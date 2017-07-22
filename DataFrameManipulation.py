#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 17:22:18 2017

@author: Emiel & Valerie

Documentation text to come
"""

import pandas as ClassPd
import numpy as ClassNp
from datetime import datetime as Dt
import datetime as ClassDt
from calendar import monthrange
from datetime import timedelta as timedelta
import dateutil.relativedelta as Du


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


def f_FindNearestDate(na_DateTime, vs_Date):
    """
        Description:        finds the date in a list closest the date provided
        Input:
            na_DateTime     numpy array or pandas series with datetime dates
            vs_Date         string or datetime date of the date to compare l_DateTime to
        Output:
            dt_Min          datetime date of the date closest to vs_Date 
            vi_MinInd       index of dt_Min in na_DateTime
    """
    
    if not isinstance(na_DateTime, ClassNp.ndarray) and not isinstance(na_DateTime, ClassPd.Series):
        raise TypeError("The date list must be a numpy array or a pandas series!")
    
    if isinstance(vs_Date, str):
        dt_CompareDate = Dt.strptime(vs_Date, '%Y-%m-%d').date()
    elif isinstance(vs_Date, ClassDt.date):
        dt_CompareDate = vs_Date
    else:
        raise TypeError("The date to find must be a string or a datetime date!")
    
    dt_Min = min(na_DateTime, key=lambda x: abs(x - dt_CompareDate))
    vi_MinInd = ClassNp.where(na_DateTime == dt_Min)
    
    return dt_Min, vi_MinInd


def f_CutDates(df_Data, vs_StartDate='default', vs_EndDate='default'):
    """
        Description:        trims a dataframe to start at vs_StartDate and end at vs_EndDate
        Input:
            df_Data         pandas dataframe with a column 'price_date' with strings of dates
            vs_StartDate    string of date at which data should start. If this is before the first date in the data, nothing will change.
            vs_EndDate      string of date at which data should end. If this is after the last date in the data, nothing will change
        Output:
            df_Data         trimmed dataframe
    """
    
    if (vs_StartDate == 'default') or (vs_StartDate < df_Data['price_date'].iloc[0]):
        vs_StartDate = df_Data['price_date'].iloc[0]
    if (vs_EndDate == 'default') or (vs_EndDate > df_Data['price_date'].iloc[-1]):
        vs_EndDate = df_Data['price_date'].iloc[-1]

    df_Data = df_Data.loc[(df_Data['price_date'] >= vs_StartDate) & (df_Data['price_date'] <= vs_EndDate)].copy()
    return df_Data


def f_FindCommonDates(l_Data):
    """
        Description:        finds the first and last date for which all dataframes in the list have data
        Input:      
            l_Data          (list of) dataframes with stock prices. The dataframes should contain at least
                            'price_date': column with the dates in string format
        Output:
            vs_StartDate    string of first date present in all dataframes
            vs_EndDate      string of last date present in all dataframes
    """
    
    vs_StartDate = l_Data[0]['price_date'].iloc[0]
    vs_EndDate = l_Data[0]['price_date'].iloc[-1]
    
    for df_Data in l_Data:
        if vs_StartDate < df_Data['price_date'].iloc[0]:
            vs_StartDate = df_Data['price_date'].iloc[0]
        if vs_EndDate > df_Data['price_date'].iloc[-1]:
            vs_EndDate = df_Data['price_date'].iloc[-1]
            
    return vs_StartDate, vs_EndDate
    

def f_CountTimePeriod(vs_Date1, vs_Date2, vs_Period):
    """
        Description:        counts the number of times a certain period has passed between two dates
        Input:
            vs_Date1        string or datetime date indicating the first day of the time period to consider
            vs_Date2        string or datetime date indicating the last day of the time period to consider
            vs_Period       the period to take into account. Currently possible:
                                 - 'monthly'
        Output:
            vi_Delta        integer with the number of times the period has passed
    """
    
    if isinstance(vs_Date1, str):
        dt_CompareDate1 = Dt.strptime(vs_Date1, '%Y-%m-%d').date()
    elif isinstance(vs_Date1, ClassDt.date):
        dt_CompareDate1 = vs_Date1
    else:
        raise TypeError("The 1st date to find must be a string or a datetime date!")
        
    if isinstance(vs_Date2, str):
        dt_CompareDate2 = Dt.strptime(vs_Date2, '%Y-%m-%d').date()
    elif isinstance(vs_Date2, ClassDt.date):
        dt_CompareDate2 = vs_Date2
    else:
        raise TypeError("The 2nd date to find must be a string or a datetime date!")
    
    vi_Delta = 0
    if dt_CompareDate1 < dt_CompareDate2:
        dt_D1 = dt_CompareDate1
        dt_D2 = dt_CompareDate2
    else:
        dt_D1 = dt_CompareDate2
        dt_D2 = dt_CompareDate1
    
    if vs_Period.lower() in ['monthly', 'month']:
        while True:
            vi_DaysOfMonth = monthrange(dt_D1.year, dt_D1.month)[1]
            dt_D1 += timedelta(days=vi_DaysOfMonth)
            if dt_D1 <= dt_D2:
                vi_Delta += 1
            else:
                break
    else:
        raise ValueError("It's not yet possible to enter anything but 'month' as period!")
            
    return vi_Delta
    
def f_ListTimePeriod(na_DateTime, vs_Period):
    """
        Description:            create a list of dates corresponding to X periods ago for a certain timeframe 
                                (for example 1 month ago, 2 months ago, etc)
        Input:  
            na_DateTime         numpy array of pandas series containing datetime dates
            vs_Period           the period to take into account. Currently possible:
                                 - 'monthly'
        Output:
            na_Dates            numpy array of the dates corresponding to X periods ago
    """
    
    if isinstance(na_DateTime, ClassPd.Series):
        na_Dt = na_DateTime.values
    elif isinstance(na_DateTime, ClassNp.ndarray):
        na_Dt = na_DateTime
    else:
        raise TypeError("The date list must be a numpy array or a pandas series!")
    
    dt_D1 = na_Dt[0]
    dt_D2 = na_Dt[-1]
    dt_XPeriodsAgo = dt_D2
    
    l_Dates = []
    vi_Periods = 1
    while dt_D1 <= dt_XPeriodsAgo:
        if vs_Period.lower() in ['monthly', 'month', 'months']:
            dt_XPeriodsAgo = dt_D2 + Du.relativedelta(months=-vi_Periods)
        else:
            raise ValueError("It's not yet possible to enter anything but 'month' as period!")
        l_NearDate = f_FindNearestDate(na_Dt, dt_XPeriodsAgo)
        l_Dates.append(l_NearDate[0])
        vi_Periods += 1
    
    na_Dates = ClassNp.array(l_Dates)
    
    return na_Dates