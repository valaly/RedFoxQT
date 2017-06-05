#import os
import numpy as ClassNp
from dbaccess import DatabaseManipulationSM
#from backtesting import Backtesting
import df_manipulation as m_Dfm
import pandas as ClassPd
import datetime as ClassDt
from strategy3 import RotationalETF
from ClassBacktesting import ClassBacktesting

o_DBSM = DatabaseManipulationSM()

# Get data for strategy
o_DBSM.load('daily_price_IWM')
o_DBSM.load('daily_price_SPY')
o_DBSM.load('daily_price_EFA')
o_DBSM.load('daily_price_ICF')
o_DBSM.load('daily_price_DBC')
o_DBSM.load('daily_price_VWO')
o_DBSM.load('daily_price_IAU')
o_DBSM.load('daily_price_TLT')
o_DBSM.load('daily_price_SHY')

IWM = o_DBSM.data['daily_price_IWM']['content']
SPY = o_DBSM.data['daily_price_SPY']['content']
EFA = o_DBSM.data['daily_price_EFA']['content']
ICF = o_DBSM.data['daily_price_ICF']['content']
DBC = o_DBSM.data['daily_price_DBC']['content']
VWO = o_DBSM.data['daily_price_VWO']['content']
IAU = o_DBSM.data['daily_price_IAU']['content']
TLT = o_DBSM.data['daily_price_TLT']['content']
SHY = o_DBSM.data['daily_price_SHY']['content']

# Make a list with all data
l_Data = [IWM, SPY, EFA, ICF, DBC, VWO, IAU, TLT, SHY]

# Set parameters & variables
dic_Context = {}
dic_Context['start_date'] = '2012-01-01'
dic_Context['end_date'] = '2012-03-01'
dic_Context['max_notional'] = 1000
dic_Context['weights'] = ClassNp.array([1, 1, 1, -1])
dic_Context['top_in'] = 1
dic_Context['top_out'] = 1
dic_Context['order_day'] = 1
dic_Context['risk_free_rate'] = 0.01
dic_Context['start_day'] = 25
dic_Context['positions'] = ClassNp.zeros(len(l_Data))
dic_Context['period'] = 'monthly'
dic_Context['max_drawdown'] = 0.05
dic_Context['positions'] = ClassNp.array([0, 0, 0, 0, 0, 0, 0, 0, 0])

# Make sure all data has the same start & end point      
l_PerfData = [None] * len(l_Data)
l_TestData = [None] * len(l_Data)
for vi_Tmp, df_Tmp in enumerate(l_Data):
    l_PerfData[vi_Tmp] = m_Dfm.cut_dates(df_Tmp, dic_Context['start_date'], dic_Context['end_date'])
    l_TestData[vi_Tmp] = m_Dfm.cut_dates(df_Tmp, 'default', dic_Context['end_date'])

# Create the test data dataframe
# This data is only the price data needed for computing the order
# !! Note to self: Use close prices --> this isn't very general yet....
vs_TestPriceType = 'close_price'
df_Test = m_Dfm.merge_dfs(l_TestData, 'price_date', [vs_TestPriceType])
l_ColumnNames = ['price_date'] + [x for x in df_Test.columns.values if x.startswith(vs_TestPriceType)]
df_TestData = df_Test.loc[:, l_ColumnNames]

for vi_Tmp, vs_Name in enumerate(l_ColumnNames[1:]):
    df_TestData.rename(columns={vs_Name: ''.join(['price_', str(vi_Tmp + 1)])}, inplace=True)

# Create the performance data dataframe
# This data is the price data needed for calculating the performance (returns)
# !! Note to self: Use adjusted close price --> also not general yet...
vs_PerfPriceType = 'adj_close_price'
df_Perf = m_Dfm.merge_dfs(l_PerfData, 'price_date', [vs_PerfPriceType])
l_ColumnNames = ['price_date'] + [x for x in df_Perf.columns.values if x.startswith(vs_PerfPriceType)]
df_PerfData = df_Perf.loc[:, l_ColumnNames]

for vi_Tmp, vs_Name in enumerate(l_ColumnNames[1:]):
    df_PerfData.rename(columns={vs_Name: ''.join(['price_', str(vi_Tmp + 1)])}, inplace=True)

# Initialize order and log arrays
na_Order = ClassNp.zeros(shape=(ClassNp.shape(df_Perf)[0], ClassNp.shape(df_PerfData)[1] - 1), dtype=ClassNp.int)
l_Log = [None] * ClassNp.shape(df_Perf)[0]

# Determine the date at which to start
ps_Date = ClassPd.to_datetime(df_TestData['price_date'].values).date
vi_StartPoint = m_Dfm.find_nearest_date(ps_Date,
                                            ClassDt.datetime.strptime(df_Perf['price_date'][0], '%Y-%m-%d').date(),
                                            'daily')[0]

# Select only the dates after the start point
ps_Date = ps_Date[vi_StartPoint:]

# Create date array to execute strategy on - one for weekly, one for monthly, depending on dic_Context
ps_Dm = m_Dfm.get_date_range(df_Perf['price_date'].values[0], df_Perf['price_date'].values[-1],
                                'monthly', dic_Context['start_day'], last_point_now=False)
ps_Dw = m_Dfm.get_date_range(df_Perf['price_date'].values[0], df_Perf['price_date'].values[-1],
                                'weekly', 1, last_point_now=False)

# Use na_Cw & na_Cm to combine the dates to check on. If there is a date both as 'monthly' and 'weekly', pick 'monthly'
# The order of concatenation and ClassNp.unique is important for this to go correct
na_DmN = m_Dfm.find_nearest_date(ps_Date, ps_Dm, 'monthly')[0]
na_Cm = ClassNp.ones(ClassNp.shape(na_DmN))
na_DwN = m_Dfm.find_nearest_date(ps_Date, ps_Dw, 'weekly')[0]
na_Cw = ClassNp.zeros(ClassNp.shape(na_DwN))

na_DrCompl = ClassNp.concatenate([na_DmN, na_DwN])  # all dates to check
na_CrCompl = ClassNp.concatenate([na_Cm, na_Cw])    # 1 if month, 0 if week

# Remove all the double values (keep monthly checks)
na_Dr, na_IndU = ClassNp.unique(na_DrCompl, return_index=True)
na_Cr = na_CrCompl[na_IndU]

vi_DrInd = 0
vi_Ind = 0
na_OrderMatrix = ClassNp.zeros(shape=(ClassNp.shape(na_Order)[0], ClassNp.shape(na_Order)[1]))
#l_TmpOrderDate = []

# Run strategy for all dates
while (vi_Ind < len(ps_Date)) & (vi_DrInd < len(na_Dr)):
    vi_Ind = na_Dr[vi_DrInd]
    dic_Context['check'] = 'monthly' if na_Cr[vi_DrInd] == 1 else 'weekly'
    vi_DrInd += 1

    o_R = RotationalETF(df_TestData.loc[:(vi_Ind + vi_StartPoint), :], dic_Context, backtest=True)
    na_Order[vi_Ind, :], l_Log[vi_Ind] = o_R.calc_results()

    dic_Context['positions'] += na_Order[vi_Ind, :]
    if sum(na_Order[vi_Ind, :]) != 0:
        dic_Context['last_order'] = df_TestData.loc[vi_Ind + vi_StartPoint, 'price_date']

    print vi_Ind, len(ps_Date), dic_Context['check'], ps_Date[vi_Ind]
    print dic_Context['positions']
    
    #l_TmpOrderDate.extend([df_TestData.loc[vi_Ind + vi_StartPoint, 'price_date']])
    
    if ClassNp.amax(na_Order[vi_Ind, :]) > 0:
        na_OrderMatrix[vi_Ind, :] = na_Order[vi_Ind,:] / ClassNp.amax(na_Order[vi_Ind, :])
    elif ClassNp.amin(na_Order[vi_Ind, :]) < 0:
        na_OrderMatrix[vi_Ind, :] = na_Order[vi_Ind,:] / ClassNp.abs(ClassNp.amin(na_Order[vi_Ind, :]))
    else:
        na_OrderMatrix[vi_Ind, :] = na_Order[vi_Ind, :]
    
#ps_OrderDate = ClassPd.to_datetime(l_TmpOrderDate).date  
na_OrderDate = df_Perf['price_date'].values
                                   
"""
Now to start the backtesting!!
"""

test = ClassBacktesting(l_Data, na_OrderMatrix, na_OrderDate)
df_Returns, df_NrOfShares, df_ValueShares = test.get_returns(1000)

# voor return een matrix maken met hoeveel geld er in elk aandeel zit, plus extra kolom met #geld in cash
# de som van de rij is dan de hoeveelheid geld in totaal in die strategie
# welke tijdsframe moet dit dan zijn? elke keer dat er een transactie gedaan wordt opnieuw bekijken?
# of elke dag bekijken?
# is dat variabel te maken? willen we dat opzich?
# dit is eigenlijk gewoon aangeven waar de cash in zit

# nadat de matrix berekend is, willen we waarschijnlijk ook een kolom met gewoon de returns
# dus de som van de rijen

# en zodra we dat hebben, kunnen we al die variabelen daar op los laten

# initial capital = 

# data = (how to specify if we want to use OHLC??)
