#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:32:50 2017

@author: emiel
"""

# Initialise Strategy Class
from StrategyClass import Strategy


## STRATEGY STEP 1: Which stocks? ---------------------------------------------

# Initialising Stock(s), loading price data
DBC = Strategy('DBC')
DBC.readData()



## STRATEGY STEP 2: Which strategy? -------------------------------------------
# First order indicator
b = DBC.FirstOrderIndicator('SMA',TimeValue=10,PriceType='LowPrice')
bb = DBC.FirstOrderIndicator('Volatility',TimeValue=10,PriceType='LowPrice')
# Second order indicator
c = DBC.SecondOrderIndicator(b,'SMA',TimeValue=100)


# Single buy or Sell Criteria
d = DBC.GoldenCross(b,c)
e = DBC.IsSlope(b['Result'],0.15,0.2)


# Multiple buy or Sell Criteria
f = DBC.CommonTY(d,e,'Sell')


## STRATEGY STEP 3: Plot! 
DBC.plotStock('OpenPrice')
DBC.PlotIndicator(b)
DBC.PlotIndicator(c)
DBC.plotTY(d)
DBC.plotTY(e)
DBC.PlotBuySell(f)

#DBC.MainPlot(b)