#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:32:50 2017

@author: emiel
"""


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime as dt
import DataFrameManipulation as m_Dfm


# Initialise Strategy Class
from StrategyClass import Strategy


## Initialise
vs_Path = '/Users/emiel/Dropbox/MySharedDocuments/04_RedFox/02_PythonFiles/SM_Database/daily_price/'
vs_Prefix = 'daily_price_'



#### ROTATIONAL ETF - STRATEGY 3 ###############################################

### STRATEGY STEP 1: Which stocks? ---------------------------------------------
## Select Stocks
l_Name = ['DBC' ,'EFA','IAU','ICF','IWM','SHY','SPY']



## Read priceinformation 
# Note: Data is cut based on optimal date
df_StockData = Strategy(l_Name, vs_Path, vs_Prefix)

### STRATEGY STEP 2: Which strategy? -------------------------------------------
## First order indicator


#df_StockData.FirstOrderIndicator('Volatility')
df_StockData.f_FirstOrderIndicator('SMA',TimeValue=8)
df_StockData.f_FirstOrderIndicator('SMA',TimeValue = 3)


#df_StockData.f_SecondOrderIndicator('EMA',DataType = 'EMA___open_price',TimeValue=20)
#df_StockData.f_SecondOrderIndicator('SMA',DataType = 'Volatility__adj_close_price')


#df_StockData.f_Weighting(['EMA_10__adj_close_price', 'EMA_10__open_price','SMA_10__Volatility__adj_close_price'],[1,2,3])

#df_StockData.f_Ranking('EMA_10__adj_close_price')

df_StockData.f_CompareDfs('SMA_8__adj_close_price','SMA_3__adj_close_price','equal')



# For Demo
Data = df_StockData.l_Data
OutputData = df_StockData.l_OutputData
#IndicatorOverview = df_StockData.df_IndicatorOverview


## STRATEGY STEP 3: Plot! 
