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


#a.FirstOrderIndicator('SMA',TimeValue=11,dummy='hoi')
#a.SecondOrderIndicator(a.l_FirstOrderIndicatorValues,'SMA',DataType='SMA_11',TimeValue=100)


#### ROTATIONAL ETF - STRATEGY 3 ###############################################

### STRATEGY STEP 1: Which stocks? ---------------------------------------------
## Select Stocks
l_Name = ['DBC' ,'EFA','IAU','ICF','IWM']
#l_Name = 'DBC'

## Read priceinformation 
# Note: Data is cut based on optimal date
df_StockData = Strategy(l_Name, vs_Path, vs_Prefix)

### STRATEGY STEP 2: Which strategy? -------------------------------------------
## First order indicator
# Volatilty

#df_StockData.FirstOrderIndicator('Volatility')
df_StockData.FirstOrderIndicator('EMA')
df_StockData.FirstOrderIndicator('Volatility')

df_StockData.SecondOrderIndicator('EMA',df_StockData.l_OutputData,DataType='EMA_10__adj_close_price',TimeValue=11)
B = df_StockData.l_OutputData
### Second order indicator
## Average Volatility
#portfolio_average = df_StockData.l_FirstOrderIndicatorValues

# Performance Indicator
#DBC.f_CalcPerformance(DBC.StockData['DateTime'].iloc[-1],portfolio_average)
#EFA.f_CalcPerformance(EFA.StockData['DateTime'].iloc[-1],portfolio_average)
#IAU.f_CalcPerformance(IAU.StockData['DateTime'].iloc[-1],portfolio_average)
#ICF.f_CalcPerformance(ICF.StockData['DateTime'].iloc[-1],portfolio_average)
#IWM.f_CalcPerformance(IWM.StockData['DateTime'].iloc[-1],portfolio_average)

## Performance Indicator
#portfolio_performance = pd.DataFrame({'DBC':DBC.f_CalcPerformance(DBC.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'EFA':EFA.f_CalcPerformance(EFA.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'IAU':IAU.f_CalcPerformance(IAU.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'ICF':ICF.f_CalcPerformance(ICF.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'IWM':IWM.f_CalcPerformance(IWM.StockData['DateTime'].iloc[-1],portfolio_average)})
#
### Single buy or Sell Criteria


# Multiple buy or Sell Criteria



## STRATEGY STEP 3: Plot! 


#out = DBC.f_CalcReturn(DBC.StockData['DateTime'].iloc[-1], DBC.StockData['close_price'], time='monthly')






# Calculate (Average) Volatility - Required as input for performance



#en = np.where(out == out[10])
#outt = DBC.StockData['OneMonthBackDate']
#outt[outt.isin(outt[2])]
#DBC.StockData['OneMonthBackDate']                