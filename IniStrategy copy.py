#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:32:50 2017

@author: emiel
"""


import numpy as np
import matplotlib.pyplot as plt

# Initialise Strategy Class
from StrategyClass import Strategy

plt.close("all")

#### ROTATIONAL ETF - STRATEGY 3 ###############################################

### STRATEGY STEP 1: Which stocks? ---------------------------------------------
## Select Stocks
DBC = Strategy('DBC') 
EFA = Strategy('EFA')
IAU = Strategy('IAU')
ICF = Strategy('ICF')
IWM = Strategy('IWM')

## Read priceinformation 
DBC.readData()
EFA.readData()
IAU.readData()
ICF.readData()
IWM.readData()


### STRATEGY STEP 2: Which strategy? -------------------------------------------
## First order indicator

# Volatilty


# Second order indicator


# Single buy or Sell Criteria


# Multiple buy or Sell Criteria



## STRATEGY STEP 3: Plot! 


#out = DBC.f_CalcReturn(DBC.StockData['DateTime'].iloc[-1], DBC.StockData['close_price'], time='monthly')






# Calculate (Average) Volatility - Required as input for performance



#en = np.where(out == out[10])
#outt = DBC.StockData['OneMonthBackDate']
#outt[outt.isin(outt[2])]
#DBC.StockData['OneMonthBackDate']                