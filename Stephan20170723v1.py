# -*- coding: utf-8 -*-
"""
Created on Sun Apr 09 18:27:13 2017

@author: Stephan
"""
"""
ek wil met 'n eenvoudige startegy (bvb SMA's cross) 'n hele klomp securities 
afscan en dan kyk watse een die beste perform vir 'n given time.
wil transaction costs include, en dit via De Giro doen.

koste is die laagste by de VS stocks (sien simulation excel), so wil nou
'n lot van daai stocks download (kan dalk met quandl), dan die SMA strat daarop
doen met 'n relatively short time window, including transaction costs.

waarskynlik is dit al duisend keer gedoen, want SMA is 'n soor 'hello world' 
van quant trading. but you never know.

kan as dit nie werk nie iets anders google wat dalk beter sal werk.

-----------------------------------------------
LOG
-----------------------------------------------

0520
kan van valerie se files gebruik create_daily_price_csv uit dbaccess om 
dataframe te maak van csv file

-----------------------------------------------
0605

debug - nou crash hy by OLN - 147

maak dat plots date het op die x-axis. 
(download die data one-time ipv dit elke keer online te gaan kry)
soek beste 10 stocks uit baie, ondersoek hoekom hulle goed werk met hierdie strat, test op training set.

20170721
-	Write python script to download all datafiles into one chunk that I can then use offline?
o	Pros:
	Don’t need internet to work with data
	Faster to read through CSV files than to download from internet
o	Cons
	Need to write script
	Need to make my return calculator work with that script
	Data will be outdated after a while so would have to re-download the data after a while.
o	Way of working:
	Download to dataframe
	Can’t save to multiple sheets of excel (CSV is defined as having only 1 sheet), so will download to many csv’s.
	Save dataframe to csv --> for the 3187 tickers in Quandl WIKI get roughly 1 GB of data in 3187 CSV files. 
-	Downloaded a lot of these files into CSV.
-	Write way to make code work with CSV files.


"""

#import quandl 
#from downloader import WebsiteData
#from dbaccess import DatabaseManipulation as dbM
#from Stephan_Strat_SMA_20170604 import ClassStephanStratSMA 
#import matplotlib.finance as fnc
#import matplotlib.ticker as ticker
#from datetime import datetime as dt # https://stackoverflow.com/questions/11376080/plot-numpy-datetime64-with-matplotlib


import numpy as np
import pandas as pd
import talib
import matplotlib.pyplot as plt
import matplotlib.dates as dts
import datetime
from datetime import datetime as dt
#from datetime import datetime as dt # https://stackoverflow.com/questions/11376080/plot-numpy-datetime64-with-matplotlib

# CRITICAL ADMIN
vi_SMA_factor_long = 21 # [days]
vi_SMA_factor_short = 9 # [days]
vs_price_type = 'Adj. Close' # can be 'Adj. Close', 'Adj. Open', 'Open', 'Close'...
vf_CASH = 1000 # USD to start with
vf_Fixed_Trans_Cost = 0.5 # USD, fixed
vf_Perc_Trans_Cost = 0 # fraction
vf_Fixed_PerStock_Cost = 0.004 # USD/stock

# read in all ticker names and if they have been downloaded or not.
df_info = pd.read_csv("Quandl-WIKI-datasets-codes_DOWNED20170721_v1.csv") # file should be in current working directory

# INITIATE THINGS
# file where we will save the results of the backtesting
df_Results = pd.DataFrame(index=df_info.index, columns=['ticker',
                                                        'end_cash',
                                                        'end_stock_flow', 
                                                        'len_train_set', 
                                                        'first_date', 
                                                        'last_date', 
                                                        'tracked_trades']) # create dataframe for the Results (end cash per ticker). index -> # rows, columns = # and names of columns
                         
# HERE WE GET THE TICKER NAME FOR THE SECURITY AND CAN LOOP OVER THE TICKERS TO DOWNLOAD THEM ALL    
for row, vs_Ticker in enumerate(df_info.loc[:, 'Ticker']): # reads over the column called 'Ticker' 
#    print row, ' ', vs_Ticker

    if df_info.loc[row, 'Downloaded on Date'] != 'not-downed' : # only do any analyses if there is a csv file with price data for this Ticker downloaded
    
        print row, ' ', vs_Ticker
        
        # get path of datafile (csv) to read in for each ticker. REPLACE WITH YOUR OWN PATH TO FOLDER THAT CONTAINS CSV FILES AND THEIR NAME
        path = ''.join(['C:\DATA\OneDrive\My Documents\GitHub\Data\Quandl_WIKI_Data', '/', vs_Ticker, '.csv'])
        df_Security = pd.read_csv(path) # downloads data from Quandl and puts it in a dataframe format (Valerie made it)
        
        # assign prices based on price_type and create training and testing set
        nai_Prices = df_Security[vs_price_type].values
        
        nai_Prices_Training_Set = nai_Prices[0:int(len(nai_Prices)/2)]
        nai_Prices_Testing_Set = nai_Prices[int(len(nai_Prices)/2):]
        
        # getting DATE that we can PLOT
        ps_Date = pd.to_datetime(df_Security['Date'])
        # ps_Date1 = dts.datestr2num(ps_Date)
        # df_Date = df_Date.dt.date
        # date_object = [dt.strptime(x, '%Y-%m-%d') for x in df_Security['Date']]
        ps_Date_Training_Set = ps_Date[0:int(len(nai_Prices)/2)]
        ps_Date_Testing_Set = ps_Date[int(len(nai_Prices)/2):]
#        na_Dates_Training_Set = dts.date2num(ps_Date[0:int(len(nai_Prices)/2)]) # how to : https://stackoverflow.com/questions/1574088/plotting-time-in-python-with-matplotlib
#        na_Dates_Testing_Set = dts.date2num(ps_Date[int(len(nai_Prices)/2):])
                               
        # calc indicators
        nai_SMA_long = talib.SMA(nai_Prices_Training_Set, vi_SMA_factor_long)
        nai_SMA_short = talib.SMA(nai_Prices_Training_Set, vi_SMA_factor_short)
        
        # FIND WHERE TO BUY/SELL
        # buy: diff SMA1-SMA2 turns from neg to pos.
        # sell: diff SMA1 - SMA2 turns from pos to neg
        nai_Buy = np.zeros(len(nai_SMA_long))
        for i in range(1,len(nai_SMA_long)):
            if nai_SMA_long[i]-nai_SMA_short[i] <=0 and nai_SMA_long[i-1]-nai_SMA_short[i-1] >0: # if (nai_SMA_long-nai_SMA_short) becomes negative
                nai_Buy[i] = 1
            elif nai_SMA_long[i]-nai_SMA_short[i] >=0 and nai_SMA_long[i-1]-nai_SMA_short[i-1] <0: # if (nai_SMA_long-nai_SMA_short) becomes positive
                nai_Buy[i]=-1
        
        # EXECUTE BUY/SELL AND CALCULATE RETURNS           
        nai_CASH_FLOW = np.zeros(len(nai_Prices_Training_Set)+1)
        nai_STOCK_FLOW = np.zeros(len(nai_Prices_Training_Set)+1) # the # of stocks in possession at any given time
        nai_TRANS_COST = np.zeros(len(nai_Prices_Training_Set)+1)
        nai_BUY_SELL_EXECUTED = np.zeros(len(nai_Prices_Training_Set)+1)
        nai_BUY_SELL_DATE_EXEC = np.empty(len(nai_Prices_Training_Set)+1, dtype = dt)
        nai_BUY_SELL_DATE_SIGNAL = np.empty(len(nai_Prices_Training_Set)+1, dtype = dt)
        nai_CASH_FLOW[0] = vf_CASH
        
        for i in range(len(nai_Prices_Training_Set)): # loop over the prices in Training_Set. 
        
            # if we get a buy or sell signal, we buy at next days price.
            if nai_Buy[i] == 1 and i < len(nai_Prices_Training_Set)-2 and nai_CASH_FLOW[i] > nai_Prices_Training_Set[i+1] : # don't buy anything at the 2nd to last element or last, even if it has a 'buy' signal there, because we need to be able to sell at the 2nd to last element. also don't buy anything unless you have the CASH_flow to do so.
               
                # buys it the next day @ price_type
                vi_stock_amount = np.floor(nai_CASH_FLOW[i]/nai_Prices_Training_Set[i+1]) # we can buy an integer amount of aandelen @ their price, depending on available cash
                vi_exact_price = nai_Prices_Training_Set[i+1]*vi_stock_amount 
                vi_transaction_cost = vf_Fixed_Trans_Cost + vf_Perc_Trans_Cost*vi_stock_amount + vf_Fixed_PerStock_Cost*vi_stock_amount
                
                # we can't go negative with cash_flow, so if we would have negative (due to transaction costs), we need to buy fewer stocks
                while nai_CASH_FLOW[i] - vi_exact_price - vi_transaction_cost < 0 and vi_stock_amount > 0:
                    vi_stock_amount = vi_stock_amount - 1
                    vi_exact_price = nai_Prices_Training_Set[i+1]*vi_stock_amount
                    vi_transaction_cost = vf_Fixed_Trans_Cost + vf_Perc_Trans_Cost*vi_stock_amount + vf_Fixed_PerStock_Cost*vi_stock_amount
                                                                             
                nai_CASH_FLOW[i+1] = nai_CASH_FLOW[i] - vi_exact_price - vi_transaction_cost
                nai_TRANS_COST[i+1] = vi_transaction_cost
                nai_STOCK_FLOW[i+1] = vi_stock_amount
                nai_BUY_SELL_EXECUTED[i+1] = 1
                nai_BUY_SELL_DATE_EXEC[i+1] = ps_Date[i+1]
                nai_BUY_SELL_DATE_SIGNAL[i] = ps_Date[i]
                                              
            elif ( nai_Buy[i] == -1 or i == len(nai_Prices_Training_Set)-2 ) and i < len(nai_Prices_Training_Set)-1 and nai_STOCK_FLOW[i] > 0: #sell at the 2nd to last element. don't sell at the very last element if there is a sell signal because we won't be able to process that sell (sell happens with next open_price). only try and sell something if we have something to sell (first signal might be sell)
                # sells it the next day @ price_type
                vi_transaction_cost = vf_Fixed_Trans_Cost + vf_Perc_Trans_Cost*nai_STOCK_FLOW[i] + vf_Fixed_PerStock_Cost*nai_STOCK_FLOW[i]
                nai_CASH_FLOW[i+1] = nai_CASH_FLOW[i] + nai_STOCK_FLOW[i]*nai_Prices_Training_Set[i+1] - vi_transaction_cost
                nai_TRANS_COST[i+1] = vi_transaction_cost 
                nai_STOCK_FLOW[i+1] = 0
                nai_BUY_SELL_EXECUTED[i+1] = -1
                nai_BUY_SELL_DATE_EXEC[i+1] = ps_Date[i+1]
                nai_BUY_SELL_DATE_SIGNAL[i] = ps_Date[i]
                              
            else:
                nai_CASH_FLOW[i+1] = nai_CASH_FLOW[i]
                nai_STOCK_FLOW[i+1] = nai_STOCK_FLOW[i]
                
        # ASSIGN RESULTS TO DATAFRAMES
        df_Track_Trades = pd.DataFrame(data = {'Buy_Sell_Signal': np.append(nai_Buy, np.nan) , 
                                               'Date_Signal' : nai_BUY_SELL_DATE_SIGNAL, 
                                               'Buy_Sell_Executed' : nai_BUY_SELL_EXECUTED, 
                                               'Date_Executed': nai_BUY_SELL_DATE_EXEC, 
                                               'Price' : np.append(nai_Prices_Training_Set, np.nan), 
                                               'Stock_Flow' : nai_STOCK_FLOW, 
                                               'Cash_Flow' : nai_CASH_FLOW, 
                                               'Trans_Cost' : nai_TRANS_COST })
        df_Results.loc[row, :] = [vs_Ticker, 
                                  nai_CASH_FLOW[-1],
                                nai_STOCK_FLOW[-1], 
                                     len(nai_Prices_Training_Set), 
                                        ps_Date_Testing_Set.iloc[0], 
                                        ps_Date_Testing_Set.iloc[-1], 
                                        df_Track_Trades]
    
nai_End_CASH = df_Results['end_cash'].tolist()
    
#    dict = {'Name': 'Zara', 'Age': 7, 'Class': 'First'}
#    print "dict['Name']: ", dict['Name']
    

#
plt.close("all") # Closing all previous figures
#        
plt.figure()
#plt.title('...')
plt.plot(nai_SMA_long, '-*', label="sma_long", color='grey')
plt.plot(nai_SMA_short, '-*', label="sma_short", color='red')
plt.plot(nai_Prices_Training_Set, label="Price Train set")
plt.legend()
        
plt.figure()
plt.plot(nai_Buy,label='Buy')

plt.figure()
plt.plot(nai_CASH_FLOW, label='cash flow')
#plt.plot(sell,label='Sell',color='red')
plt.legend()

#plt.figure(2)
#plt.plot_date(na_Dates_Training_Set, nai_CASH_FLOW[0:len(nai_CASH_FLOW)-1],'-', label='cash flow')
##plt.plot(sell,label='Sell',color='red')
#plt.legend()

plt.figure()
plt.plot(nai_TRANS_COST, label='Trans_cost')
plt.plot(np.cumsum(nai_TRANS_COST), label='cum trans_cost')
plt.legend()

plt.figure()
plt.plot(nai_STOCK_FLOW, label='Stock_flow')
plt.legend()

plt.figure()
plt.plot(df_Results['end_cash'], 'o', label='end cash')
plt.legend()

"""
# PLOTTING SOME ANALYSES
"""
# sort results by END CASH
df_Results_Sorted = df_Results.sort_values(['end_cash'], ascending=[False]) # how to sort: https://stackoverflow.com/questions/13636592/how-to-sort-a-pandas-dataframe-according-to-multiple-criteria 

# divide by time
ps_Results_Divided = df_Results_Sorted['end_cash']/df_Results_Sorted['len_train_set']

#df_Results_Sorted['cash_div_by_time'] = df_Results_Sorted['end_cash'] / df_Results_Sorted['len_train_set']

# plot some stuff
plt.figure()
ps_xaxis = range(len(df_Results_Sorted['ticker']))
plt.plot(ps_xaxis, df_Results_Sorted['end_cash'], 'bo')
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(ps_xaxis, ps_Results_Divided, 'r-')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
ax2.set_ylabel('cash_div_by_time', color='r')
ax2.tick_params('y', colors='r')

plt.figure()
ps_xaxis = range(len(df_Results_Sorted['ticker']))
plt.plot(ps_xaxis, df_Results_Sorted['end_cash'], 'bo')
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(ps_xaxis, df_Results_Sorted['len_train_set'], 'r-')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
ax2.set_ylabel('len_train_set', color='r')
ax2.tick_params('y', colors='r')

# how much return if you had invested in all?
vf_Total_Return = np.sum(df_Results_Sorted['end_cash']) # sum of all end-cash
vf_Total_Invested = len(df_Results_Sorted['ticker'])*vf_CASH # sum of investing vf_CASH in all stocks
vf_Total_Profit = vf_Total_Return - vf_Total_Invested

# BENCHMARK
# benchmark against buy and hold
df_Bench_Buy_Hold = pd.DataFrame(index=df_Results.index, columns=['ticker', 'Buy_Hold_Return'])
for row, vs_Ticker in enumerate(df_Results['ticker']):
    df_Track_Trades = df_Results.loc[row, 'tracked_trades']
    #next(vi_Counter for vi_Counter in df_Track_Trades['Buy_Sell_Executed'] if vi_Counter == 1)
#    ps_tmp_Buy_Sell_Executed = df_Track_Trades['Buy_Sell_Executed']

    # https://stackoverflow.com/questions/18327624/find-elements-index-in-pandas-series 
    if (1 in df_Track_Trades['Buy_Sell_Executed'].values) and (-1 in df_Track_Trades['Buy_Sell_Executed'].values):
        vf_Stock_Total = df_Track_Trades.loc[ df_Track_Trades[ df_Track_Trades['Buy_Sell_Executed'] == 1].index[0] , 'Stock_Flow'] # gives index of first Buy Executed, and with that gets the Price that it was executed for
        vf_Price_End = df_Track_Trades.loc[ df_Track_Trades[ df_Track_Trades['Buy_Sell_Executed'] == -1].index[-1] , 'Price']
        vf_Trans_Cost = df_Track_Trades.loc[ df_Track_Trades[ df_Track_Trades['Buy_Sell_Executed'] == 1].index[0] , 'Trans_Cost'] + df_Track_Trades.loc[ df_Track_Trades[ df_Track_Trades['Buy_Sell_Executed'] == -1].index[-1] , 'Trans_Cost']
        vf_Return = vf_Price_End*vf_Stock_Total - vf_CASH - vf_Trans_Cost
        df_Bench_Buy_Hold.loc[row, :] = [vs_Ticker, vf_Return]
    else:
        df_Bench_Buy_Hold.loc[row, :] = [vs_Ticker, np.nan]
        
df_Bench_Sorted = df_Bench_Buy_Hold.sort_values(['Buy_Hold_Return'], ascending=[False])

     
plt.figure()
ps_xaxis = range(len(df_Bench_Buy_Hold))
plt.plot(ps_xaxis, df_Results['end_cash'], 'bo', markerfacecolor = 'none')
plt.plot(ps_xaxis, df_Bench_Buy_Hold['Buy_Hold_Return'], 'ro', markerfacecolor = 'none')
plt.grid()

#ax1 = plt.gca()
#ax2 = ax1.twinx()
#ax2.plot(ps_xaxis, df_Bench_Sorted['Buy_Hold_Return'], 'r-')
#ax1.set_xlabel('ticker')
## Make the y-axis label, ticks and tick labels match the line color.
#ax1.set_ylabel('end_cash SMA_strat [USD]', color='b')
#ax1.tick_params('y', colors='b')
#ax2.set_ylabel('CAGR', color='r')
#ax2.tick_params('y', colors='r')
#ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='vf_CASH level')
#ax1.legend()
#plt.ylabel('USD')

#plt.figure()
#plt.plot(range(len(df_Bench_Sorted)), df_Bench_Sorted['Buy_Hold_Return'], 'o')
#plt.ylabel('USD')

#plt.figure()
#plt.plot(df_Bench_Buy_Hold['Buy_Hold_Return'])

#df_Track_Trades = df_Results.loc[1028, 'tracked_trades']
    

# GET CAGR
# https://en.wikipedia.org/wiki/Compound_annual_growth_rate
# to get the time difference in days: https://stackoverflow.com/questions/21414639/convert-timedelta-to-floating-point
# how to get differences in dates: 
    # bla = ps_Date_Training_Set.iloc[-1] - ps_Date_Training_Set.iloc[0] 
    # bla.total_seconds()/(3600*24) = time difference in days
# exponent: (10000/1000)**(1/()
ps_Time_Diff = df_Results_Sorted['last_date'] - df_Results_Sorted['first_date']
ps_Time_Diff = ps_Time_Diff.dt.days # changed timedeltas to float. how to https://stackoverflow.com/questions/35502927/from-timedelta-to-float-days-in-pandas
ps_Time_Diff = ps_Time_Diff/365 # days to years because we will use CAGR (annual)
ps_CAGR = (df_Results_Sorted['end_cash'] / vf_CASH )**(1/ps_Time_Diff) - 1
df_Results_Sorted['CAGR'] = ps_CAGR

plt.figure()
ps_xaxis = range(len(df_Results_Sorted['ticker']))
plt.plot(ps_xaxis, df_Results_Sorted['end_cash'], 'bo')
plt.grid()
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(ps_xaxis, df_Results_Sorted['CAGR'], 'r-')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
ax2.set_ylabel('CAGR', color='r')
ax2.tick_params('y', colors='r')
ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='vf_CASH level')
ax1.legend()

# sort by CAGR and plot again
df_Results_Sorted = df_Results_Sorted.sort_values(['CAGR'], ascending=[False]) # how to sort: https://stackoverflow.com/questions/13636592/how-to-sort-a-pandas-dataframe-according-to-multiple-criteria 

plt.figure()
ps_xaxis = range(len(df_Results_Sorted['ticker']))
plt.plot(ps_xaxis, df_Results_Sorted['end_cash'], 'bo', markerfacecolor='none')
plt.grid()
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(ps_xaxis, df_Results_Sorted['CAGR'], 'r-*')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
ax2.set_ylabel('CAGR', color='r')
ax2.tick_params('y', colors='r')
ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='start cash')
ax1.legend()

# add benchmark returns to sorted by CAGR and plot again
df_Results_Sorted.sort_index(inplace = True) # sort by index: https://stackoverflow.com/questions/22211737/python-pandas-how-to-sort-dataframe-by-index
df_Results_Sorted['Buy_Hold_Return'] = df_Bench_Buy_Hold['Buy_Hold_Return']
df_Results_Sorted = df_Results_Sorted.sort_values(['CAGR'], ascending=[False])

plt.figure()
ps_xaxis = range(len(df_Results_Sorted['ticker']))
plt.plot(ps_xaxis, df_Results_Sorted['end_cash'], 'bo', label='SMA1/SMA2 return', markerfacecolor='none')
#plt.xticks(ps_xaxis, df_Results_Sorted['ticker'], rotation = 45)
plt.grid()
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(ps_xaxis, df_Results_Sorted['CAGR'], 'r-*')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
ax2.set_ylabel('CAGR', color='r')
ax2.tick_params('y', colors='r')
ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='start cash')
ax1.plot(ps_xaxis, df_Results_Sorted['Buy_Hold_Return'], 'go', label = 'buy hold return', markerfacecolor='none')
ax1.legend()

# now sort benchmarked returns on returns divided by time
#ps_Results_Divided = df_Results_Sorted['end_cash']/df_Results_Sorted['len_train_set']
df_Results_Sorted.sort_index(inplace = True)
df_Results_Sorted['ret_div_time'] = df_Results_Sorted['end_cash']/df_Results_Sorted['len_train_set']
df_Results_Sorted = df_Results_Sorted.sort_values(['ret_div_time'], ascending=[False])

plt.figure()
ps_xaxis = range(len(df_Results_Sorted['ticker']))
plt.plot(ps_xaxis, df_Results_Sorted['ret_div_time'], 'bo', label='SMA1/SMA2 return/time', markerfacecolor='none')
#plt.xticks(ps_xaxis, df_Results_Sorted['ticker'], rotation = 45)
plt.grid()
ax1 = plt.gca()
#ax2 = ax1.twinx()
#ax2.plot(ps_xaxis, df_Results_Sorted['CAGR'], 'r-*')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
#ax2.set_ylabel('CAGR', color='r')
#ax2.tick_params('y', colors='r')
#ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='start cash')
ax1.plot(ps_xaxis, df_Results_Sorted['Buy_Hold_Return']/df_Results_Sorted['len_train_set'], 'go', label = 'buy hold return/time', markerfacecolor='none')
ax1.legend()

# PRE SELECT STOCKS
# select if CAGR > *number*
vi_CutOffCAGR = 0
df_Stocks_Selected = df_Results_Sorted[df_Results_Sorted['CAGR'] >= vi_CutOffCAGR]
df_Stocks_Deselected = df_Results_Sorted[df_Results_Sorted['CAGR'] < vi_CutOffCAGR] # the number of items in this list plus the number of items in the Selected list will not match the total number of items because some have NaN for their CAGR (negative end_cash) at the moment 20170722

# select if still active
dt_CutOffDate = datetime.datetime(2016, 07, 01, 0, 0) # fill in Year Month and Day in datetime.datetime(Y, M, d, 0, 0) where you want cut off to happen
df_Stocks_Selected = df_Stocks_Selected[df_Stocks_Selected['last_date'] >= dt_CutOffDate ]
df_Stocks_Deselected = df_Stocks_Deselected.append( df_Stocks_Selected[df_Stocks_Selected['last_date'] < dt_CutOffDate ]) 

# select if trading for >1y
#bla2.total_seconds()/(3600*24)
# ( ( df_Stocks_Select['last_date'] - df_Stocks_Select['first_date'] ).dt.days ) >= 365
vi_CutOffTradeTime = 365 # min length of training set in days 
df_Stocks_Selected = df_Stocks_Selected[df_Stocks_Selected['len_train_set'] >= vi_CutOffTradeTime ]


plt.figure('plot stuff with tickers')
ps_xaxis = range(len(df_Stocks_Selected['ticker']))
plt.plot(ps_xaxis, df_Stocks_Selected['end_cash'], 'bo', markerfacecolor='none')
plt.xticks(ps_xaxis, df_Stocks_Selected['ticker'], rotation = 45)
plt.grid()
ax1 = plt.gca()
ax2 = ax1.twinx()
ax2.plot(ps_xaxis, df_Stocks_Selected['CAGR'], 'r-*')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
ax2.set_ylabel('CAGR', color='r')
ax2.tick_params('y', colors='r')
ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='start cash')
ax1.legend()

plt.figure('ret SMA vs ret Buy/Hold')
ps_xaxis = range(len(df_Stocks_Selected['ticker']))
plt.plot(ps_xaxis, df_Stocks_Selected['end_cash'], 'bo', label='SMA1/SMA2 return', markerfacecolor='none')
#plt.xticks(ps_xaxis, df_Results_Sorted['ticker'], rotation = 45)
plt.grid()
ax1 = plt.gca()
#ax2 = ax1.twinx()
#ax2.plot(ps_xaxis, df_Results_Sorted['CAGR'], 'r-*')
ax1.set_xlabel('ticker')
# Make the y-axis label, ticks and tick labels match the line color.
ax1.set_ylabel('end_cash [USD]', color='b')
ax1.tick_params('y', colors='b')
#ax2.set_ylabel('CAGR', color='r')
#ax2.tick_params('y', colors='r')
#ax1.plot(ps_xaxis, vf_CASH*np.ones(len(ps_xaxis)), 'k-', label='start cash')
ax1.plot(ps_xaxis, df_Stocks_Selected['Buy_Hold_Return'], 'go', label = 'buy hold return', markerfacecolor='none')
ax1.legend()



"""
NEAT PLOTTING THINGS

# to plot on same x axis but different y - axes
https://matplotlib.org/devdocs/gallery/api/two_scales.html
https://stackoverflow.com/questions/15082682/matplotlib-diagrams-with-2-y-axis

# to plot a ticker (string) on the x-axis 
# plt.xticks(x, df_Sorted_Results['ticker'], rotation = 45) # plot with strings on x - axis : https://stackoverflow.com/questions/3100985/plot-with-custom-text-for-x-axis-points

# to plot the date on the x-axis using matplotlib: # how to : https://stackoverflow.com/questions/1574088/plotting-time-in-python-with-matplotlib
# Example:
# ps_Date = pd.to_datetime(df_Security['Date'])
# ps_Date = ps_Date.dt.normalize() # to get rid of the time and just keep the date
# na_Dates_Training_Set = dts.date2num(ps_Date[0:int(len(nai_Prices)/2)])
# from datetime import datetime as dt # https://stackoverflow.com/questions/11376080/plot-numpy-datetime64-with-matplotlib
 plt.figure(0)
 plt.plot_date(na_Dates_Training_Set, nai_SMA_long, '-*', label="sma_long", color='grey')
 plt.plot_date(na_Dates_Training_Set, nai_SMA_short, '-*', label="sma_short", color='red')
 plt.plot_date(na_Dates_Training_Set, nai_Prices_Training_Set, label="Price Train set")
 plt.legend()
#


"""

"""
# PLOTTING DATES ON THE X-AXIS. FROM Emiel's fancy date plot ding. vindplaats: https://github.com/valaly/RedFoxQT/blob/Emiel_Branch/StrategyClass.py, rond regel 277

"""

#hoe we het gaan doen:
    # get list of tickers
    # load list of tickers
    # go through each ticker
#for i in list_tickers:
#    data_per_ticker = a.get_quandl_data(i)
#    
#    analyze data_per_ticker
#    save output
#    



