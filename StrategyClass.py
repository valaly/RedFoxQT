#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat Mar 11 15:33:32 2017

@author: emiel
"""

import numpy as np
import talib
import pandas as pd
import DataFrameManipulation as m_Dfm 


# Strategey Class
# define class
class Strategy(object):
    def __init__(self,l_Name, vs_Path="", vs_Prefix="",vs_Postfix=""):
        '''
        Discription:
                            Initates the Strategy Class. Checks if it is just a string (1 stock) or a list of strings (multiple stocks).
                            The dates of the stocks are automatically synchronized and cut into equal pieces.
        Input:
            l_Name:         Ticker Names
            vs_Path:        Path of .csv files
            vs_Prefix:      Prefix of the .csv file name
            vs_Postfix:     Postfix of the .csv file name
            
        Output:
            l_Data:         Red input data from csv files, with columns: date time, open_price, close_price etc.
            l_OutputData:   Initiated list of dataframes, with the first column the date time. Intention to be filled with indicators
            
        '''
        # Initiate
        self.l_OutputData = []
        
        
        # Store the variables (if l_Name is a string, change it to a list)
        if isinstance(l_Name, str):
            self.l_Name = [l_Name]
        else:
            self.l_Name = l_Name
      
        # Loop through all Tickers and write data to list
#        self.l_Data = [m_Dfm.f_ReadCsv(vs_Ticker, vs_Path, vs_Prefix, vs_Postfix) for vs_Ticker in self.l_Name]
        self.l_DataUnCut = [m_Dfm.f_ReadCsv(vs_Ticker, vs_Path, vs_Prefix, vs_Postfix) for vs_Ticker in self.l_Name]

        vs_StartDate, vs_EndDate = m_Dfm.f_FindCommonDates(self.l_DataUnCut)  
        self.l_Data = m_Dfm.f_CutDates(self.l_DataUnCut,vs_StartDate,vs_EndDate)
        
        for df in self.l_Data:
            self.l_OutputData.append(pd.DataFrame(data = {"price_date": df['price_date']}))
    #############################################################################################
    ####################################### INDICATORS ##########################################
    #######################################   BEGIN    ##########################################
    #############################################################################################      
        
        
        
            ## Strategy Components  ----------------------------------------------   
    def f_FirstOrderIndicator(self,vs_IndicatorName, **kwargs):
        '''
        Discription:
                                Calculates first order indicator.
                                Possible indicators:
                                    EMA
                                    SMA
                                    Volatility
                                    Performance
                                    ...
        Input:
            vs_IndicatorName:   Name of the indicator to be used
            **TimeValue:        Timevalue required for some of the indicators, like: EMA, SMA,...
            **DataType:         The price type being used. E.g. open_price, close_price. Default: adj_close_price
            
        Output:
           l_OutputData:        Adds one column to each element (data frame) the l_OutputData being the used indcator values. 
                                Column name, example:
                                    EMA_11__open_price --> EMA with TimeValue 11 days based on the open price
            
        '''
        
        self.l_OutputData = self._CalcIndicator('FirstOrder',   self.l_Data,    vs_IndicatorName,   self.l_OutputData,  arguments = kwargs)
        
    def f_SecondOrderIndicator(self, vs_IndicatorName,l_Data,**kwargs):
        
        '''
        Discription:
                                Calculates second order indicator.
                                Possible indicators:
                                    EMA
                                    SMA
                                    Volatility
                                    Performance
                                    ...
        Input:
            vs_IndicatorName:   Name of the indicator to be used
            **TimeValue:        Timevalue required for some of the indicators, like: EMA, SMA,...
            **DataType:         The first order indicator being used. E.g. EMA_11__open_price
            
        Output:
           l_OutputData:        Adds one column to each element (data frame) the l_OutputData being the used indcator values. 
                                Column name, example:
                                    Volatility__EMA_11__open_price --> Volatility of the EMA with TimeValue 11 days based on the open price
            
        '''
        
        
        self.l_OutputData = self._CalcIndicator('SecondOrder',  l_Data,         vs_IndicatorName,   self.l_OutputData,  arguments = kwargs)           

    def f_Weighting(self, l_IndicatorNames, l_WeightingFactors):
        
        '''
        Discription:
                                    This function weights a number of given indicators to their corresponsing weightings, and adds it up to one new indicator.
                                    This is done for each Stock in self.l_Name / l_Data / l_OutputData
        Input:
            l_IndicatorNames:       Names of the indicators to be used. This sould correspond to a column name of self.l_OutputData (e.g. Volatility__EMA_11__open_price_)
            l_WeightingFacteors:    List of weighting factors (numbers), corresponding to the Indicators in l_IndicatorNames.
            
        Output:
           l_OutputData:            Adds one column to each element (data frame) of l_OutputData being the weighted result. 
                                    Column name: 'Weighted'.

        '''

        # Weight each indicator for each Stock
        for i,df in enumerate(self.l_OutputData):
            # Create and array with zeros, length l_OutputData
            temp=[0]*len(self.l_OutputData[0])
            for j,name in enumerate(l_IndicatorNames):
                temp = temp + df[name]*l_WeightingFactors[j]
            self.l_OutputData[i]['Weighted'] = temp
    
    
    
    
    
    
    
    def f_Ranking(self,l_IndicatorName):
        '''
        Discription:
                                    This function ranks the stocks based on an indicator. This is done per date. 
        Input:
            l_IndicatorName:        Names of the indicator on which the ranking should be based. This sould correspond to a column name of self.l_OutputData (e.g. 'Weighted')
            
        Output:
           df_IndicatorOverview:    A new dateframe is created with 1+3*n columns (n = number of stocks): 
                                       Column 0:                Date Time                                   Name: price_date
                                       Column 1 - n:            Indicator Values of the stocks              Name: Tickers, e.g. 'DBC' , 'EFA'
                                       Column n+1 - 2n:         Index of ranked indicator values            Name: Ticker_sort, e.g. 'DBC_sort', 'EFA_sort'
                                       Column 2n+1 - 3n:        Tickers in ranked order                     Name: Rank number, e.g. Rank 1, Rank 2, ...       

        '''
        # Create a new data frame with Price Dates in the first column, indicator results in rest of the columns
        self.df_IndicatorOverview=pd.DataFrame(data = {"price_date": self.l_Data[0]['price_date']})
        for i,df in enumerate(self.l_OutputData):
            self.df_IndicatorOverview[self.l_Name[i]]=df[l_IndicatorName]
        
        # Initiate    
        l_Name_sort=[]
        l_RankNumber = []
        
        # Create empty columns which will later be filled with sorted index numbers. Name: Ticker_sort
        for i,name in enumerate(self.l_Name):
            self.df_IndicatorOverview[str(self.l_Name[i]+'_sort')]=np.nan
            
            # create a list with the name of the columns
            l_Name_sort.append(str(self.l_Name[i]+'_sort'))
        
        # Create empty columns which will later be filled with ranked Tickers. Name: rank_1, rank_2 .. 
        for i,name in enumerate(self.l_Name):
            self.df_IndicatorOverview[str('Rank_'+str(i+1))]=np.nan
            
            # create a list with the name of the columns
            l_RankNumber.append(str('Rank_'+str(i+1)))
        
        
        
        
        
        
        # Fill the previously created empty columns
        for i,df in enumerate(self.df_IndicatorOverview['price_date']):
            temp_ArrayToBeSorted = self.df_IndicatorOverview[self.l_Name].iloc[i,:].values
            temp_ArrayWithRankedIndices = temp_ArrayToBeSorted.argsort()
            self.df_IndicatorOverview.loc[i,l_Name_sort] = temp_ArrayWithRankedIndices
            self.df_IndicatorOverview.loc[i,l_RankNumber] = [x for (y,x) in sorted(zip(temp_ArrayWithRankedIndices,self.l_Name))]
        

    
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
    def _CalcIndicator(IndicatorOrder,l_Data,vs_IndicatorName,l_OutputData='',**kwargs):

        '''
        Discription:
                                Calculates the indicator of interest
        Input:
            IndicatorOrder:     String of the order number: 'FirstOrderIndicator' | 'SecondOrderIndicator'
            vs_IndicatorName:   Name of the indicator to be used
            **TimeValue:        Timevalue required for some of the indicators, like: EMA, SMA,...
            **DataType:         The price type being used. 
                                E.g. open_price, close_price. Default: adj_close_price
                                Or: EMA_11__open_price
            
            
        Output:
                                Adds one column to each element (data frame) the l_OutputData being the used indcator values. 
                                Column name, example:
                                    Volatility__EMA_11__open_price --> Volatility of the EMA with TimeValue 11 days based on the open price
        '''        
        
        
        
        
        argumentName=[]
        argumentValue=[]
        l_IndicatorValues=[]
        
        if isinstance(l_OutputData,str):
            l_OutputData=[]
            for df in l_Data:
                df_Init=pd.DataFrame(data = {"price_date": df['price_date']})
                l_OutputData.append(df_Init)
        
        
        # loop through **kwargs
        for key, value in kwargs['arguments'].iteritems():
            argumentName.append(key)
            argumentValue.append(value)
                        
        if 'TimeValue' in argumentName:
            vi_TimeValue = argumentValue[argumentName.index('TimeValue')]
            #dic_Output.update({"TimeValue":vi_TimeValue})        
        else:
            vi_TimeValue = 10
            print('Warning: Default TimeValue used: 10 days ')
        
        # Read and assign all input arguments            
    
        if 'DataType' in argumentName:
            vs_DataType = argumentValue[argumentName.index('DataType')]
            #dic_Output.update({"PriceType":vs_PriceType})
        else:
            if IndicatorOrder == 'FirstOrder':
                vs_DataType = 'adj_close_price'
                print('Warning: Default price used: adj_close_price')  
            elif IndicatorOrder == 'SecondOrder':
                raise ValueError('Give the name of the FirstOrder indicator which should be used as an input.')                            



        ## Here is whete the actual indicator is being calculated
        # loop through all Tickers
        for df_in,df_out in zip(l_Data,l_OutputData):
            # Check Indicator Type and Calculate Result        
            if vs_IndicatorName == 'SMA':
                df_out.loc[:,'_'.join([vs_IndicatorName,str(vi_TimeValue),'',vs_DataType])]=talib.SMA(np.array(df_in[vs_DataType]),timeperiod = vi_TimeValue)


            elif vs_IndicatorName == 'EMA':
                df_out.loc[:,'_'.join([vs_IndicatorName,str(vi_TimeValue),'',vs_DataType])]=talib.EMA(np.array(df_in[vs_DataType]),timeperiod = vi_TimeValue)
            
            
#            elif vs_IndicatorName == 'MonthlyPerformance':
#                '''The monthly performance is calculated as follows: natural logarithm of (price/price_1_month_earlier + 1).'''
#                
#                # To determin the price_1_mont_earlier --> shift dates one month back, and correct for weekends etc.
#                na_Dates = m_Dfm.f_ListTimePeriod(df_in['date_time'], 'monthly')
#                
#                
#                result = np.log(np.array(df_in[vs_DataType])/np.array(df_in[vs_DataType]-vi_TimeValue)+1)
            

            elif vs_IndicatorName == 'Volatility':
                for df_in,df_out in zip(l_Data,l_OutputData):                
                    l_MonthlyVolatility =[]
                    for i in range(len(np.array(df_in[vs_DataType]))):
                        # Calculate the monthly volatility | Take standard deviation of the past month (21days) multiplied by sqrt(T)
                        d_MonthlyVolatility_PerDay = np.std(np.array(df_in[vs_DataType][i-21:i]))*np.sqrt(12)
                        l_MonthlyVolatility = np.append(l_MonthlyVolatility,d_MonthlyVolatility_PerDay)
                    df_out.loc[:,'_'.join([vs_IndicatorName,'',vs_DataType])] = l_MonthlyVolatility

#                     
#            elif vs_IndicatorName == 'Performance':
#                result= f_CalcResult(ld_UsedPrice)
#    #        dic_Output.update({"Result" :result})
#        
    #        # Pass datetime object to output
    #        dic_Output.update({"dt_object":self.StockData['DateTime']})
    
        return l_OutputData

    #############################################################################################
    ####################################### STATIC FUNCTIONS ####################################
    #######################################       END        ####################################
    #############################################################################################   
 
 
    