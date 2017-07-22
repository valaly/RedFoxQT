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

import DataFrameManipulation as dfm


# Initialise Strategy Class
from StrategyClass import Strategy












# playground
DBC = dfm.read('DBC')
DBC.FirstOrderIndicator('SMA')

#
##### ROTATIONAL ETF - STRATEGY 3 ###############################################
#
#### STRATEGY STEP 1: Which stocks? ---------------------------------------------
### Select Stocks
#DBC = Strategy('DBC') 
#EFA = Strategy('EFA')
#IAU = Strategy('IAU')
#ICF = Strategy('ICF')
#IWM = Strategy('IWM')
#
### Read priceinformation 
#DBC.readData()
#EFA.readData()
#IAU.readData()
#ICF.readData()
#IWM.readData()
#
## cut dates --> automatiseren
#start_date  = '2008-01-01'
#end_date    = '2012-12-30'
#
#DBC.f_CutDates( start_date, end_date)
#EFA.f_CutDates( start_date, end_date)
#IAU.f_CutDates( start_date, end_date)
#ICF.f_CutDates( start_date, end_date)
#IWM.f_CutDates( start_date, end_date)
#
### Cut data to same timerange
## Determine 
#
#### STRATEGY STEP 2: Which strategy? -------------------------------------------
### First order indicator
## Volatilty
#portfolio_volatilities =    pd.DataFrame({'DBC':DBC.FirstOrderIndicator('Volatility')['Result'],
#                                          'EFA':EFA.FirstOrderIndicator('Volatility')['Result'],
#                                          'IAU':IAU.FirstOrderIndicator('Volatility')['Result'],
#                                          'ICF':ICF.FirstOrderIndicator('Volatility')['Result'],
#                                          'IWM':IWM.FirstOrderIndicator('Volatility')['Result'],})
#
#
### Second order indicator
## Average Volatility
#portfolio_average = portfolio_volatilities.mean(axis=1)
#
## Performance Indicator
##DBC.f_CalcPerformance(DBC.StockData['DateTime'].iloc[-1],portfolio_average)
##EFA.f_CalcPerformance(EFA.StockData['DateTime'].iloc[-1],portfolio_average)
##IAU.f_CalcPerformance(IAU.StockData['DateTime'].iloc[-1],portfolio_average)
##ICF.f_CalcPerformance(ICF.StockData['DateTime'].iloc[-1],portfolio_average)
##IWM.f_CalcPerformance(IWM.StockData['DateTime'].iloc[-1],portfolio_average)
#
## Performance Indicator
#portfolio_performance = pd.DataFrame({'DBC':DBC.f_CalcPerformance(DBC.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'EFA':EFA.f_CalcPerformance(EFA.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'IAU':IAU.f_CalcPerformance(IAU.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'ICF':ICF.f_CalcPerformance(ICF.StockData['DateTime'].iloc[-1],portfolio_average),
#                                      'IWM':IWM.f_CalcPerformance(IWM.StockData['DateTime'].iloc[-1],portfolio_average)})
#
### Single buy or Sell Criteria
#
#
## Multiple buy or Sell Criteria
#
#
#
### STRATEGY STEP 3: Plot! 
#
#
##out = DBC.f_CalcReturn(DBC.StockData['DateTime'].iloc[-1], DBC.StockData['close_price'], time='monthly')
#
#
#
#
#
#
## Calculate (Average) Volatility - Required as input for performance
#
#
#
##en = np.where(out == out[10])
##outt = DBC.StockData['OneMonthBackDate']
##outt[outt.isin(outt[2])]
##DBC.StockData['OneMonthBackDate']                