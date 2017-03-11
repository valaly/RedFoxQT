#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:32:50 2017

@author: emiel
"""

# Initialise Strategy Class
from StrategyClass import Strategy
from StrategyClass import indicator

# Call functions/class      
DBC = Strategy('DBC')
DBC.readData()
DBC.plotStock('openPrice')

ABC = 


DBC_SMA = DBC.indicator('SMA')
DBC_SMA.calc(timeValue=100)
DBC_SMA.plotInd()
#
DBC_EMA = indicator('EMA')
DBC_EMA.calc(DBC,timeValue=50)
DBC_EMA.plotInd()

sjaak
#
##DBC_BB = indicator('BBANDS')
##DBC_BB.calc(DBC,timeValue=2, maType=2)
##DBC_BB.plotInd(label='probeer')
#
#probeersel = buySell('DBC_SMA_EMA_Cross')
#t1, y1 = probeersel.goldenCross(DBC_SMA, DBC_EMA)
#t2, y2 = probeersel.isSlope(DBC,0,0.05)
#probeersel.plotTY(t1,y1)
#probeersel.plotTY(t2,y2)
#T = probeersel.commonTY(t1,t2)
#probeersel.plotBuySell(T)
#
#
#
#
