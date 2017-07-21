#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 17:16:23 2017

Hier komt documentatie tekst


@author: emiel
"""

import matplotlib.pyplot as plt
import matplotlib.finance as fnc
import matplotlib.ticker as ticker

def plotStock(self, whichPrice):
    
    # choose between open/cloe/high/low and plot datetime object and values. DIT KAN CHIQUER
    if whichPrice == 'OpenPrice':
        plot = plt.plot(self.StockData['DateTime'],self.StockData['open_price'] )
    elif whichPrice == 'ClosePrice':
        plot = plt.plot(self.StockData['DateTime'],self.StockData['close_price'] )
    elif whichPrice == 'LowPrice':
        plot = plt.plot(self.StockData['DateTime'],self.StockData['low_price'] )
    elif whichPrice == 'HighPrice':
        plot = plt.plot(self.StockData['DateTime'],self.StockData['high_price'] )
    elif whichPrice == 'CandleStick':
        plot, ax = plt.subplots()
        fnc.candlestick2_ochl(ax,self.StockData['open_price'] ,self.StockData['high_price'] ,self.StockData['low_price'] ,self.StockData['close_price'] , width=0.5, colorup='k', colordown='r', alpha=0.75)
        
        ax.xaxis.set_major_locator(ticker.MaxNLocator(15))
        
        def mydate(x,pos):
            try:
                return self.StockData['DateTime'][int(x)]
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
