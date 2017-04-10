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
        
        
## Reading Data --------------------------------------------- 
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

 
    

## Strategy Components  ----------------------------------------------   
    def FirstOrderIndicator(self,vs_IndicatorName, **kwargs):
        
        # initiate
        dic_Output={"VariableType":'FirstOrderIndicator',"StockName":self.name, "IndicatorName":vs_IndicatorName, "IndicatorOrder":'First'}
        argumentName=[]
        argumentValue=[]
        
        # loop through **kwargs
        for key, value in kwargs.iteritems():
            argumentName.append(key)
            argumentValue.append(value)
                        
        
        
        
        # Read and assign all input arguments            
        if 'PriceType' in argumentName:
            vs_PriceType = argumentValue[argumentName.index('PriceType')]
            dic_Output.update({"PriceType":vs_PriceType})
        else:
            vs_PriceType = 'OpenPrice'
            
        if vs_PriceType == 'OpenPrice':
            ld_UsedPrice = self.open_price
        elif vs_PriceType == 'ClosePrice':
            ld_UsedPrice = self.close_price
        elif vs_PriceType == 'LowPrice':
            ld_UsedPrice = self.low_price
        elif vs_PriceType == 'HighPrice':
            ld_UsedPrice = self.high_price

            

        if 'TimeValue' in argumentName:
            vi_TimeValue = argumentValue[argumentName.index('TimeValue')]
            dic_Output.update({"TimeValue":vi_TimeValue})
        


# check which indicator is to be calculated
            #   Implemented so far
            #   'Name' | 'Arguments'
            #   SMA - Simple Moving Average | timeValue
            #   EMA - Exponential Moving Average | timeValue
            #
            
          
        
        # Check Indicator Type and Calculate Result        
        if vs_IndicatorName == 'SMA':
            result = talib.SMA(np.array(ld_UsedPrice),timeperiod = vi_TimeValue)
        elif vs_IndicatorName == 'EMA':
            result = talib.EMA(np.array(ld_UsedPrice),timeperiod = vi_TimeValue)
        elif vs_IndicatorName == 'ReturnPerformance':
            #The monthly performance is calculated as follows: natural logarithm of (price/price_1_month_earlier + 1).
            result = np.log(np.array(ld_UsedPrice)/np.array(ld_UsedPrice-vi_TimeValue)+1)
        elif vs_IndicatorName == 'Volatility':
            result=[]
            for i in range(len(np.array(ld_UsedPrice))):
                result.append(i) = np.std(np.array(ld_UsedPrice[i-21:i]))*np.sqrt(252)
        
        
        dic_Output.update({"Result" :result})

        # Pass datetime object to output
        dic_Output.update({"dt_object":self.dt_object})

        
        return dic_Output
#
    
    def SecondOrderIndicator(self,dic_Indicator,vs_IndicatorName, **kwargs):
         # initiate
        dic_Output={"VariableType":'SecondOrderIndicator',"StockName":self.name, "IndicatorName":vs_IndicatorName, "IndicatorOrder":'Second'}
        argumentName=[]
        argumentValue=[]
        
        # loop through **kwargs
        for key, value in kwargs.iteritems():
            argumentName.append(key)
            argumentValue.append(value)
            
        

    
        if 'TimeValue' in argumentName:
            vi_TimeValue = argumentValue[argumentName.index('TimeValue')]
            dic_Output.update({"TimeValue":vi_TimeValue})
    
        # Check Indicator Type and Calculate Result        
        if vs_IndicatorName == 'SMA':
            result = talib.SMA(np.array(dic_Indicator['Result']),timeperiod = vi_TimeValue)
        elif vs_IndicatorName == 'EMA':
            result = talib.EMA(np.array(dic_Indicator['Result']),timeperiod = vi_TimeValue)
        
        
        dic_Output.update({"Result":result})

        # Pass datetime object to output
        dic_Output.update({"dt_object":self.dt_object})
    

        return dic_Output   
    




    def GoldenCross(self, dic_Indicator1,dic_Indicator2):
        dic_Output ={"VariableType":'SingleBuyOrSellCriteria',"Indicator1":dic_Indicator1,"Indicator2":dic_Indicator2,"BuySellCriteria":'GoldenCross'}
        
        
        # initiation
        x = []
        t = []
        y = []
        
        diff = []
        diff = np.append(diff,1000)

        for i in range(1,len(dic_Indicator1['Result'])):
            diff = np.append(diff,dic_Indicator2['Result'][i]-dic_Indicator1['Result'][i])
            if diff[i]*diff[i-1] < 0: # change of sign (-/+)
                x = np.append(x,i)
                t = np.append(t,dic_Indicator1['dt_object'][i])
                y = np.append(y,dic_Indicator1['Result'][i])
        
        dic_Output.update({"y":y,"t":t})
        return dic_Output


    def determineSlope(self,YValues):
        
        slope=[0] * len(YValues)              
        for i in range(1,len(YValues)):
             slope[i] = (YValues[i]-YValues[i-1])
             
        # assign to class object & output function
        #self.slope = slope
        return slope


    def IsSlope(self,YValues,vdValue1,vdValue2):
        dic_Output ={"VariableType":'SingleBuyOrSellCriteria',"LowerThreshold":vdValue1,"UpperThreshold":vdValue2,"BuySellCriteria":'IsSlope'}
#        

        # determine slope
        slope = self.determineSlope(YValues)
        
        # determine which value is higher: For robustness
        if vdValue1 >= vdValue2:
            lowLimit = vdValue2
            upLimit = vdValue1
        else:
            lowLimit = vdValue1
            upLimit = vdValue2   
        
        # allocate space        
        x=[]
        t=[]
        y=[]
        
        for i in range(1,len(YValues)):
            if slope[i] > lowLimit:
                if slope[i] < upLimit:
                    x = np.append(x,i)
                    t = np.append(t,self.dt_object[i])
                    y = np.append(y,YValues[i])
        dic_Output.update({"y":y,"t":t})
        return dic_Output

    def CommonTY(self,dic_DataIn1, dic_DataIn2,args_Action):
        dic_Output ={"VariableType":'MultipleBuyOrSellCriteria',"Action":args_Action,"BuySellCriteria1":dic_DataIn1['BuySellCriteria'],"BuySellCriteria2":dic_DataIn2['BuySellCriteria']}
        
        # find common time values
        t = list(set(dic_DataIn1['t']).intersection(dic_DataIn2['t']))
        
        dic_Output.update({"t":t})
        return dic_Output

### Required for Strategy 3
#'''The strategy evaluates each security in the basket by weighing the 1-month, 3-month, and 6-month return performance and the 6-month volatility performance. 
#Based on that, the current position is revised once a month with the possibility to sell the current position and buy a different security. Every week the position is evaluated to determine if it should be terminated, but not with the possibility to buy a different security.'''
#'''    
#return performance 
#volatility performance
#
#'''

## Plotters ---------------------------------------------
#    def MainPlot(self, arg_Data,**kwargs):
#        # initiate
#        argumentName=[]
#        argumentValue=[]
#        
#        # Read **kwargs
#        # loop through **kwargs
#        for key, value in kwargs.iteritems():
#            argumentName.append(key)
#            argumentValue.append(value)
#            
#        if 'VariableType' in argumentName:
#            if argumentValue[0]['VariableType']=='MultipleBuyOrSellCriteria':
#                print 'MultipleBuyOrSellCriteria'
#            else:
#                print 'niets'
#        else:
#            print "VariableType is unclear"
            
            
            
            
            
        
    def plotStock(self, whichPrice):
        
        # choose between open/cloe/high/low and plot datetime object and values. DIT KAN CHIQUER
        if whichPrice == 'OpenPrice':
            plot = plt.plot(self.dt_object, self.open_price)
        elif whichPrice == 'ClosePrice':
            plot = plt.plot(self.dt_object, self.close_price)
        elif whichPrice == 'LowPrice':
            plot = plt.plot(self.dt_object, self.low_price)
        elif whichPrice == 'HighPrice':
            plot = plt.plot(self.dt_object, self.high_price)
        elif whichPrice == 'CandleStick':
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


    def PlotIndicator(self,dic_Indicator,**kwargs):
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
        plot = plt.plot(dic_Indicator['dt_object'],dic_Indicator['Result'])
        
        # set label
        if 'label' in argumentName:
            print str(argumentName.index('label'))
            plt.setp(plot,label=argumentValue[argumentName.index('label')])
        else:
            plt.setp(plot, label=dic_Indicator['StockName'] + ' ' + dic_Indicator['IndicatorName'] + ' ' + dic_Indicator['IndicatorOrder'] + ' ' + str(dic_Indicator['TimeValue']))
        
        plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)

    def plotTY(self,dic_DataIn):
        # plotting
        plt.plot(dic_DataIn['t'] ,dic_DataIn['y'], 'o', label=self.name + ' ' + dic_DataIn['BuySellCriteria'])
        plt.grid(True)
        plt.ylabel('Price')
        plt.xlabel('Time')
        plt.legend()

    def PlotBuySell(self,dic_DataIn):
        for i in range(len(dic_DataIn['t'])):
            plt.axvline(dic_DataIn['t'][i], ymin=0, ymax = 1, linewidth=2, linestyle='dashed',color='k', label=dic_DataIn['Action'])
            if i == 0:
                plt.legend()# only one time creating legend item
            

















