# -*- coding: utf-8 -*-
"""
Created on Sat May 20 23:08:18 2017

@author: Valerie
"""
import pandas as ClassPd
import numpy as ClassNp
import df_manipulation as m_Dfm

class ClassBacktesting:
    
    def __init__(self, l_Data, na_Order, na_OrderTime):
        """
            Description:    initializes the backtesting class
            Input:
                l_Data      (list of) dataframes with stock prizes
                na_Order    numpy array with the orders per time point
                na_OrderTime     numpy array with the time points (in datetime) corresponding to na_Order
        """        
        # Check that the inputs are the correct type
        if not isinstance(l_Data, list) and not isinstance(l_Data, ClassPd.DataFrame):
            raise TypeError("The stock data must be a list or a dataframe!")
        if not isinstance(na_Order, ClassNp.ndarray):
            raise TypeError("The order data must be a numpy array!")
        if not isinstance(na_OrderTime, ClassNp.ndarray):
            raise TypeError("The time order data must be a numpy array!")
            
        # Check if the order data and the order time data have the same length
        if len(na_Order) is not len(na_OrderTime):
            raise ValueError("The order and time order arrays don't have the same length!")
            
        # Check if the stock data and the order data have the same width (# of stocks)
        if not (isinstance(l_Data, ClassPd.DataFrame) and len(na_Order[0]) is 1) and not (len(l_Data) is len(na_Order[0])):
            raise ValueError("The stock data and order data arrays don't have the same number of stocks!")
        
        # Store the variables (if l_Data is a pandas dataframe, change it to a list)
        if isinstance(l_Data, ClassPd.DataFrame):
            self.l_Data = [l_Data]
        else:
            self.l_Data = l_Data
        self.na_Order = na_Order
        self.na_OrderTime = na_OrderTime
        
    def get_returns(self, vi_Notional, vs_PriceType = 'adj_close_price'):
        """
            Description:    determines the returns of the given data for the given orders
            Input:
                vi_Notional     the initial amount of money put into the strategy
                vs_PriceType    the price type on which the returns should be based
            Output: 
                na_Time         array with the dates corresponding to the points in the following arrays
                na_NrOfShares   the number of shares in portfolio at each day 
                                    (corresponding to dates in l_Data)
                na_ValueShares  the total value per stock at each day 
                na_ValueCash    the total value in cash at each day
        """
        
        # Check that vi_Notional is a scalar larger than 0
        if not isinstance(vi_Notional, int) and not isinstance(vi_Notional, float):
            raise TypeError("The notional value must be an integer or a float")
    
        # Convert l_Data to a single dataframe
        if len(self.l_Data) > 1:
            df_Data = m_Dfm.merge_dfs([df.loc[:, ('price_date', vs_PriceType)] for df in self.l_Data], 'price_date', [vs_PriceType])
        else:
            df_Data = self.l_Data[0]['price_date', vs_PriceType]
        
        # Initialize the array to keep track of the amount of shares, and the amount of money in stocks and in cash
        na_Time = df_Data['price_date'].values
        na_Prices = df_Data.iloc[:, 1:].values
        na_NrOfShares = ClassNp.zeros(shape=(len(self.l_Data[0]), len(self.na_Order[0, :])))
        na_ValueShares = ClassNp.zeros(shape=(len(self.l_Data[0]), len(self.na_Order[0, :])))
        na_ValueCash = ClassNp.ones(shape=(len(self.l_Data[0]), 1)) * vi_Notional
                                   
        # Start looping through the data
        vi_TimeInd = 0
        for vi_DataInd, dt_Date in enumerate(na_Time):
            # First copy the data of the previous date to this one
            if vi_DataInd > 0:
                na_NrOfShares[vi_DataInd, :] = na_NrOfShares[vi_DataInd - 1, :]
                na_ValueCash[vi_DataInd] = na_ValueCash[vi_DataInd - 1]
                
            # Then see if they need to be updated or not
            if vi_TimeInd < len(self.na_OrderTime) and dt_Date == self.na_OrderTime[vi_TimeInd]:
                # First check if there is a sell, if so, update the number of shares, and value of cash
                for vi_SecInd, vd_Order in enumerate(self.na_Order[vi_TimeInd, :]):
                    if vd_Order < 0 and na_NrOfShares[vi_DataInd, vi_SecInd] < 0:
                        raise ValueError("There are no shares to be sold!")
                    elif vd_Order < 0:
                        vi_SellShares = ClassNp.round(na_NrOfShares[vi_DataInd, vi_SecInd] * vd_Order)
                        na_NrOfShares[vi_DataInd, vi_SecInd] += vi_SellShares
                        na_ValueCash[vi_DataInd] += -1 * vi_SellShares * na_Prices[vi_DataInd, vi_SecInd]
                
                # Then, check if there is a buy, and use the present value of cash to determine how much to buy
                vd_CheckBuy = ClassNp.sum([x for x in self.na_Order[vi_TimeInd, :] if x > 0])
                if vd_CheckBuy > 0 and vd_CheckBuy <> 1:
                    raise ValueError("The sum of orders to buy is not 1!")
                vd_StartCash = na_ValueCash[vi_DataInd]
                for vi_SecInd, vd_Order in enumerate(self.na_Order[vi_TimeInd, :]):
                    if vd_StartCash > 0 and vd_Order > 0:
                        vi_BuyShares = ClassNp.floor(vd_StartCash * vd_Order / na_Prices[vi_DataInd, vi_SecInd])
                        na_NrOfShares[vi_DataInd, vi_SecInd] += vi_BuyShares
                        na_ValueCash[vi_DataInd] += -1 * vi_BuyShares * na_Prices[vi_DataInd, vi_SecInd]
                                        
                # Increase the pointer to the na_OrderTime
                vi_TimeInd += 1
                
            # Since the number of shares have now been updated, determine how much the value is
            na_ValueShares[vi_DataInd, :] = na_Prices[vi_DataInd, :] * na_NrOfShares[vi_DataInd, :]
            
        df_Returns = ClassPd.DataFrame(data={'price_date': na_Time, 
                                            'returns': ClassNp.sum(na_ValueShares, axis=1) + na_ValueCash[:,0],
                                            'valuecash': na_ValueCash[:,0],
                                            'value_shares': ClassNp.sum(na_ValueShares, axis=1)})
        df_NrOfShares = ClassPd.DataFrame(columns = [col.replace(vs_PriceType, 'NrOfShares') for col in df_Data.columns])    
        df_NrOfShares.loc[:, 'price_date'] = na_Time
        df_NrOfShares.loc[:, 1:] = na_NrOfShares
                         
        df_ValueShares = ClassPd.DataFrame(columns = [col.replace(vs_PriceType, 'ValueShares') for col in df_Data.columns])    
        df_ValueShares.loc[:, 'price_date'] = na_Time
        df_ValueShares.loc[:, 1:] = na_ValueShares
                  
        return df_Returns, df_NrOfShares, df_ValueShares