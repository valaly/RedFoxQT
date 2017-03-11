#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:33:32 2017

@author: emiel
"""

# Import
from datetime import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.finance as fnc
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

import os
import talib



# Strategey Class
# define class
class Strategy(object):
    def __init__(self,name):
        self.name = name
        self.description = "description??"

    def readData(self):
    
        #READ  data  
        path = r"/Users/emiel/Dropbox/MySharedDocuments/04_RedFox/02_PythonFiles/SM_Database/daily_price"
        os.chdir(path)
        with open('daily_price_'+self.name+'.csv', 'rb') as csvfile:
            AllData = pd.read_csv(csvfile)
            
            # determine date range
            self.price_date = AllData['price_date']
            # convert string to datetime object
            self.dt_object = [dt.strptime(x, '%Y-%m-%d') for x in self.price_date]
            
        
        # nog zorgen dat alle colommen worden gelezen, ipv handmatig 1 voor 1
        self.open_price = AllData['open_price']        
        self.close_price = AllData['close_price']
        self.low_price = AllData['low_price']
        self.high_price = AllData['high_price']

 
    def plotStock(self, whichPrice):
        
        # choose between open/cloe/high/low and plot datetime object and values. DIT KAN CHIQUER
        if whichPrice == 'openPrice':
            plot = plt.plot(self.dt_object, self.open_price)
        elif whichPrice == 'closePrice':
            plot = plt.plot(self.dt_object, self.close_price)
        elif whichPrice == 'lowPrice':
            plot = plt.plot(self.dt_object, self.low_price)
        elif whichPrice == 'maxPrice':
            plot = plt.plot(self.dt_object, self.high_price)
        elif whichPrice == 'candleStick':
            plot, ax = plt.subplots()
            fnc.candlestick2_ochl(ax, self.open_price, self.close_price, self.high_price, self.low_price, width=0.5, colorup='k', colordown='r', alpha=0.75)
            
            ax.xaxis.set_major_locator(ticker.MaxNLocator(15))
            
            def mydate(x,pos):
                try:
                    return self.dt_object[int(x)]
                except IndexError:
                    return ''
            
            ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
            
            plot.autofmt_xdate()
            plot.tight_layout()
            
            plt.show()
            
        # set labels
        plt.xlabel('Date')
        plt.ylabel('Value')
        
        # set label
        plt.setp(plot, label = self.name)
        
        
        # legend
        plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)
 
        # show plot
        plt.show()

'''
------------ SubClass 'indicator' ----------
'''

class indicator(Strategy): 
    def __init__(self, indicatorName):
        #Strategy.__init__(self, indicatorName)
        self.indicatorName = indicatorName
        
    
    def calc(self, **kwargs):
        # initiate
        argumentName=[]
        argumentValue=[]
        
         # transfer of values from stock class ---->> Not a nice solution. I am sure Val knows a better solution ;-)
#        self.stockName = stock.name
#        self.dt_object = stock.dt_object
        
        # loop through **kwargs
        for key, value in kwargs.iteritems():
            argumentName.append(key)
            argumentValue.append(value)
                        
        # check which indicator is to be calculated
            #   Implemented so far
            #   'Name' | 'Arguments'
            #   SMA - Simple Moving Average | timeValue
            #   EMA - Exponential Moving Average | timeValue
            #
            
        # define errors
        errorTooManyArguments = ['Too many input arguments for'+self.indicatorName]
        unknownArgument =['Unknown argument type or number for indicator type' + self.indicatorName]
        
        
        if self.indicatorName == 'SMA':
            if 'timeValue' in argumentName:
                
                # check umber of arguments equals 1
                if len(argumentName) == 1:
                    # argumentValue[0] not allowed to be 1 (or <1 or??)
                    self.argumentValue = argumentValue[0]
                    
                    # calculate results using talib
                    self.result = talib.SMA(np.array(stock.open_price),timeperiod = argumentValue[0])
                elif len(argumentName) == 0:
                    print 'For indicator type "SMA" is 1 argument required: timeValue'
                else:
                    print errorTooManyArguments
            else:
                print unknownArgument
                print 'Syntax: calc("SMA", timeValue="value")'
        # ------------------------------------------------------------------ #
        elif self.indicatorName == 'EMA':
                      
            # check arguments
            if 'timeValue' in argumentName:
                
                # check umber of arguments equals 1
                if len(argumentName) == 1:
                    # argumentValue[0] not allowed to be 1 (or <1 or??)
                    self.argumentValue = argumentValue[0]
                                        
                    # calculate results using talib
                    self.result = talib.EMA(np.array(stock.open_price),timeperiod = argumentValue[0])
                elif len(argumentName) == 0:
                    print 'For indicator type "EMA" is 1 argument required: timeValue'
                else:
                    print errorTooManyArguments
            else:
                print unknownArgument
                print 'Syntax: calc("EMA", timeValue="value")'
    
    
    def plotInd(self,**kwargs):
        # initiate
        argumentName=[]
        argumentValue=[]

        # Read **kwargs
        # loop through **kwargs
        for key, value in kwargs.iteritems():
            argumentName.append(key)
            argumentValue.append(value)
        
        ### len(self.result) of len(self.result[0])
        ### iets verzinnen dat ook 2 of 3 lijnen in 1 keer geplot kunnen worden omdat BBANDS meer dan 1 resultaat
            
        # plot
        plot = plt.plot(self.dt_object,self.result)
        
        # set label
        if 'label' in argumentName:
            print str(argumentName.index('label'))
            plt.setp(plot,label=argumentValue[argumentName.index('label')])
        else:
            plt.setp(plot, label=self.stockName + ' ' + self.indicatorName + ' ' + str(self.argumentValue))
        
        plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)
