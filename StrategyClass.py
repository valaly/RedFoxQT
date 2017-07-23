#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:33:32 2017

@author: emiel
"""

import numpy as np
import talib
import pandas as pd
 
# Strategey Class
# define class
class Strategy(object):
    def __init__(self,name):
        self.name = name
        self.description = "description??"
        
        
        
        
    #############################################################################################
    ####################################### INDICATORS ##########################################
    #######################################   BEGIN    ##########################################
    #############################################################################################      
        
        
        
            ## Strategy Components  ----------------------------------------------   
    def FirstOrderIndicator(self,vs_IndicatorName, **kwargs):
        
        # initiate
        dic_Output={"VariableType":'FirstOrderIndicator',"StockName":self.name, "IndicatorName":vs_IndicatorName}
        a = _CalcIndicator(vs_IndicatorName,kwargs)
#        dic_Output.update(CalcIndicator(vs_IndicatorName,kwargs))
        
        return dic_Output
    #
    
    def SecondOrderIndicator(self,vs_IndicatorName, **kwargs):
         # initiate
        dic_Output={"VariableType":'SecondOrderIndicator',"StockName":self.name, "IndicatorName":vs_IndicatorName}


        # Use FirstORderIndicator function for calculation
        dic_Output = CalcIndicator(dic_Indicator, vs_IndicatorName, kwargs)            
#        
#    
#    
#        if 'TimeValue' in argumentName:
#            vi_TimeValue = argumentValue[argumentName.index('TimeValue')]
#            dic_Output.update({"TimeValue":vi_TimeValue})
#    
#        # Check Indicator Type and Calculate Result        
#        if vs_IndicatorName == 'SMA':
#            result = talib.SMA(np.array(dic_Indicator['Result']),timeperiod = vi_TimeValue)
#        elif vs_IndicatorName == 'EMA':
#            result = talib.EMA(np.array(dic_Indicator['Result']),timeperiod = vi_TimeValue)
#        
#        
#        dic_Output.update({"Result":result})
#    
#        # Pass datetime object to output
#        dic_Output.update({"dt_object":self.StockData['DateTime']})
#    
    
#        argumentName=[]
#        argumentValue=[]
#        
#        
#        # loop through **kwargs
#        for key, value in kwargs.iteritems():
#            argumentName.append(key)
#            argumentValue.append(value)



        return dic_Output   
     
        
    
    
#    def determineSlope(self,YValues):
#        
#        slope=[0] * len(YValues)              
#        for i in range(1,len(YValues)):
#             slope[i] = (YValues[i]-YValues[i-1])
#             
#        # assign to class object & output function
#        #self.slope = slope
#        return slope
#    
#    
#    def f_CalcPerformance(self, dt_InputDate, argd_PortfolioAverage):
#        # deze functie gaat er tot nu toe vanuit dat de MAANDELIJKSE performance wordt gevraagd. 
#        
#        # swithc from daily to monthly
#        self.f_ToMonthly( dt_InputDate)
#    
#        # calculate monthly performance
#        self.StockDataMonthly['MonthlyPerformance'] = np.log(self.StockDataMonthly['open_price']/self.StockDataMonthly['open_price_MonthShifted'] + 1)
#        
#        # calculate one/three/six month performance
#        self.StockDataMonthly['OneMonthPerformance']    = self.StockDataMonthly['MonthlyPerformance']*argd_PortfolioAverage/self.StockDataMonthly['AnnualVolatility']
#        self.StockDataMonthly['ThreeMonthPerformance']  = np.sum(self.StockDataMonthly['OneMonthPerformance'].values,timeperiod=3)
#        self.StockDataMonthly['SixMonthPerformance']    = np.sum(self.StockDataMonthly['OneMonthPerformance'].values,timeperiod=6)
#        return []
    #############################################################################################
    ####################################### INDICATORS ##########################################
    #######################################    END     ##########################################
    #############################################################################################
        
        
        
        
            
    #############################################################################################
    ####################################### CRITERIA ############################################
    #######################################  BEGIN   ############################################
    #############################################################################################
    
    def f_CompareDfs(self):
        return []
    
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
                    t = np.append(t,self.StockData['DateTime'][i])
                    y = np.append(y,YValues[i])
        dic_Output.update({"y":y,"t":t})
        return dic_Output
    
    def CommonTY(self,dic_DataIn1, dic_DataIn2,args_Action):
        dic_Output ={"VariableType":'MultipleBuyOrSellCriteria',"Action":args_Action,"BuySellCriteria1":dic_DataIn1['BuySellCriteria'],"BuySellCriteria2":dic_DataIn2['BuySellCriteria']}
        
        # find common time values
        t = list(set(dic_DataIn1['t']).intersection(dic_DataIn2['t']))
        
        dic_Output.update({"t":t})
        return dic_Output
    
    
    #############################################################################################
    ####################################### CRITERIA ############################################
    #######################################   END    ############################################
    #############################################################################################
    
    
    
    








# WEET NOG NIET WAT HIER ME MOET ::: OPSPLITSEN

## Random functions --> New file voor aanmaken?
    def f_ToMonthly(self, dt_InputDate, time='monthly'): # very slow function
        # make first element the input date
        DateDeltaMonth=[]
        DateDeltaMonth.append(dt_InputDate)
        
            
        if time == 'monthly':
            
            # determine how many months in dataset
            vi_NrMonths = self.f_MonthDelta(self.StockData['DateTime'].iget(0), self.StockData['DateTime'].iget(-1)) # take first and last date
            
            # loop through all months
            for i in range(vi_NrMonths): 
                DateDeltaMonth.append(self.f_SubtractMonths(dt_InputDate,i+1))
        else:
            pass
        
        
        ## Calculate the Returns
        self.StockDataMonthly = pd.DataFrame({'DateTime':DateDeltaMonth})

        # find pricedate by data lists (andere prijzen nog toevoegen)
        self.StockDataMonthly['open_price'] = self.StockData['open_price'].loc[self.StockData['DateTime'].isin(self.StockDataMonthly['DateTime'].values)].values
       
        # calculate annual volatility
        self.StockData['AnnualVolatility'] = self.FirstOrderIndicator('Volatility')['Result']
        self.StockDataMonthly['AnnualVolatility'] = self.StockData['AnnualVolatility'].loc[self.StockData['DateTime'].isin(self.StockDataMonthly['DateTime'].values)].values
        
        # Shift one element to get the one month shifted dates
        self.StockDataMonthly['DateTimeMonthShifted'] =  self.StockDataMonthly['DateTime'].shift(-1)
        self.StockDataMonthly['open_price_MonthShifted'] = self.StockDataMonthly['open_price'].shift(-1)
        
        
        
        return []
    
    #############################################################################################
    ####################################### STATIC FUNCTIONS ####################################
    #######################################      BEGIN       ####################################
    #############################################################################################   

    @staticmethod
    def _CalcIndicator(df_Stock,vs_IndicatorName,**kwargs):
        dic_Output=[]
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
            ld_UsedPrice =df_Stock.StockData['open_price'] 
        elif vs_PriceType == 'ClosePrice':
            ld_UsedPrice =df_Stock.StockData['close_price'] 
        elif vs_PriceType == 'LowPrice':
            ld_UsedPrice =df_Stock.StockData['low_price'] 
        elif vs_PriceType == 'HighPrice':
            ld_UsedPrice =df_Stock.StockData['high_price'] 
    
            
    
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
                # Calculate the monthly volatility | Take standard deviation of the past month (21days) multiplied by sqrt(T)
                volatility = np.std(np.array(ld_UsedPrice[i-21:i]))*np.sqrt(12)
                result = np.append(result,volatility)
        
        elif vs_IndicatorName == 'ATR': # be carefull with the timevalue
            result=talib.ATR(np.array(self.StockData['high_price'] ),np.array(self.StockData['low_price'] ),np.array(self.StockData['close_price'] ),timevalue=21)
        
        elif vs_IndicatorName == 'NATR': # be carefull with the timevalue
            result=talib.NATR(np.array(self.StockData['high_price'] ),np.array(self.StockData['low_price'] ),np.array(self.StockData['close_price'] ),timevalue=21)
        
        elif vs_IndicatorName == 'Performance':
            result= f_CalcResult(ld_UsedPrice)
        dic_Output.update({"Result" :result})
    
        # Pass datetime object to output
        dic_Output.update({"dt_object":self.StockData['DateTime']})
    
        

    #############################################################################################
    ####################################### STATIC FUNCTIONS ####################################
    #######################################       END        ####################################
    #############################################################################################   
 
 
    