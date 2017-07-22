from datetime import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.finance as fnc
import matplotlib.ticker as ticker
import pandas as pd
import numpy as np

import os
import talib


# define class
class stock:
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
    

class indicator:
    def __init__(self, indName):
        self.indName = indName
        
    
    def calc(self,stock, **kwargs):
        # initiate
        argumentName=[]
        argumentValue=[]
        
         # transfer of values from stock class ---->> Not a nice solution. I am sure Val knows a better solution ;-)
        self.stockName = stock.name
        self.dt_object = stock.dt_object
        
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
        errorTooManyArguments = ['Too many input arguments for'+self.indName]
        unknownArgument =['Unknown argument type or number for indicator type' + self.indName]
        
        
        if self.indName == 'SMA':
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
        elif self.indName == 'EMA':
                      
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
            plt.setp(plot, label=self.stockName + ' ' + self.indName + ' ' + str(self.argumentValue))
        
        plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)

        
class buySell:
    def __init__(self, name):
        self.name = name
        
        
    def goldenCross(self, indicator1,indicator2):
        # check if both indicators have same time axis
        
        # misschien beter om retunr te gebruiken ipv self.x
        
        # initiation
        x = []
        t = []
        y = []
        
        diff = []
        diff = np.append(diff,1000)

        for i in range(1,len(indicator1.result)):
            diff = np.append(diff,indicator2.result[i]-indicator1.result[i])
            if diff[i]*diff[i-1] < 0: # change of sign (-/+)
                x = np.append(x,i)
                t = np.append(t,indicator1.dt_object[i])
                y = np.append(y,indicator1.result[i])
        return t,y
        
    def determineSlope(self,yValues):
        
        slope=[0] * len(yValues)              # Gradient of SMA short
        for i in range(1,len(yValues)):
             slope[i] = (yValues[i]-yValues[i-1])
             
        # assign to class object & output function
        self.slope = slope
        return slope
             
    def isSlope(self,data,value1,value2):
        # should be suitable for both stock raw data and indicators
        if data.__class__.__name__ == 'indicator':
            yValues = data.result
        elif data.__class__.__name__ == 'stock':
            yValues = data.open_price # <------------------ DEFAULT VALUE = open_price 
        
        # determine slope
        slope = self.determineSlope(yValues)
        
        # determine which value is higher: For robustness
        if value1 >= value2:
            lowLimit = value2
            upLimit = value1
        else:
            lowLimit = value1
            upLimit = value2   
        
        # allocate space        
        x=[]
        t=[]
        y=[]
        
        for i in range(1,len(yValues)):
            if slope[i] > lowLimit:
                if slope[i] < upLimit:
                    x = np.append(x,i)
                    t = np.append(t,data.dt_object[i])
                    y = np.append(y,yValues[i])
        return t, y
            
    def commonTY(self,t1, t2):
        t = list(set(t1).intersection(t2))
        return t

    
    def plotTY(self,t,y):
        # plotting
        plt.plot(t ,y, 'o', label=self.name)
        plt.grid(True)
        plt.ylabel('Price')
        plt.xlabel('Time')
        plt.legend()

    def plotBuySell(self,t):
        for i in range(len(t)):
            plt.axvline(t[i], ymin=0, ymax = 1, linewidth=2, linestyle='dashed',color='k')


# Call functions/class      
DBC = stock('DBC')
DBC.readData()
DBC.plotStock('openPrice')

DBC_SMA = indicator('SMA')
DBC_SMA.calc(DBC,timeValue=100)
DBC_SMA.plotInd()

DBC_EMA = indicator('EMA')
DBC_EMA.calc(DBC,timeValue=50)
DBC_EMA.plotInd()

#DBC_BB = indicator('BBANDS')
#DBC_BB.calc(DBC,timeValue=2, maType=2)
#DBC_BB.plotInd(label='probeer')

probeersel = buySell('DBC_SMA_EMA_Cross')
t1, y1 = probeersel.goldenCross(DBC_SMA, DBC_EMA)
t2, y2 = probeersel.isSlope(DBC,0,0.05)
probeersel.plotTY(t1,y1)
probeersel.plotTY(t2,y2)
T = probeersel.commonTY(t1,t2)
probeersel.plotBuySell(T)



