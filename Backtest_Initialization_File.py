import os
import numpy as np
from dbaccess import DatabaseManipulationSM
#from backtesting import Backtesting
import df_manipulation as dfm
import pandas as pd
import datetime as dt
from strategy3 import RotationalETF

os.chdir('..')

dbSM = DatabaseManipulationSM()

# Get data for strategy
dbSM.load('daily_price_IWM')
dbSM.load('daily_price_SPY')
dbSM.load('daily_price_EFA')
dbSM.load('daily_price_ICF')
dbSM.load('daily_price_DBC')
dbSM.load('daily_price_VWO')
dbSM.load('daily_price_IAU')
dbSM.load('daily_price_TLT')
dbSM.load('daily_price_SHY')

IWM = dbSM.data['daily_price_IWM']['content']
SPY = dbSM.data['daily_price_SPY']['content']
EFA = dbSM.data['daily_price_EFA']['content']
ICF = dbSM.data['daily_price_ICF']['content']
DBC = dbSM.data['daily_price_DBC']['content']
VWO = dbSM.data['daily_price_VWO']['content']
IAU = dbSM.data['daily_price_IAU']['content']
TLT = dbSM.data['daily_price_TLT']['content']
SHY = dbSM.data['daily_price_SHY']['content']

data = [IWM, SPY, EFA, ICF, DBC, VWO, IAU, TLT, SHY]

# Set parameters & variables
context = {}
context['start_date'] = '2012-01-01'
context['end_date'] = '2012-03-01'
context['max_notional'] = 1000
context['weights'] = np.array([1, 1, 1, -1])
context['top_in'] = 1
context['top_out'] = 1
context['order_day'] = 1
context['risk_free_rate'] = 0.01
context['start_day'] = 25
context['positions'] = np.zeros(len(data))
context['period'] = 'monthly'
context['max_drawdown'] = 0.05
context['positions'] = np.array([0, 0, 0, 0, 0, 0, 0, 0, 0])

# Fix data       
perf_data = [None] * len(data)
test_data = [None] * len(data)
for i, df in enumerate(data):
    perf_data[i] = dfm.cut_dates(df, context['start_date'], context['end_date'])
    test_data[i] = dfm.cut_dates(df, 'default', context['end_date'])

perf_df = dfm.merge_dfs(perf_data)
test_df = dfm.merge_dfs(test_data)

# !! Note to self: Use close prices --> this isn't very general yet....
# test data is only the price data needed for computing the order
test_price_type = 'close_price'
column_names = ['price_date'] + [x for x in test_df.columns.values if x.startswith(test_price_type)]
test_data = test_df.loc[:, column_names]

for i, name in enumerate(column_names[1:]):
    test_data.rename(columns={name: ''.join(['price_', str(i + 1)])}, inplace=True)

# !! Note to self: Use adjusted close price --> also not general yet...
# perf data is the price data needed for calculating the performance (returns)
perf_price_type = 'adj_close_price'
column_names = ['price_date'] + [x for x in test_df.columns.values if x.startswith(perf_price_type)]
perf_data = perf_df.loc[:, column_names]

for i, name in enumerate(column_names[1:]):
    perf_data.rename(columns={name: ''.join(['price_', str(i + 1)])}, inplace=True)

# Initialize order and log arrays
order = np.zeros(shape=(np.shape(perf_df)[0], np.shape(perf_data)[1] - 1), dtype=np.int)
log = [None] * np.shape(perf_df)[0]

date_pd = pd.to_datetime(test_data['price_date'].values).date
start_point = dfm.find_nearest_date(date_pd,
                                            dt.datetime.strptime(perf_df['price_date'][0], '%Y-%m-%d').date(),
                                            'daily')[0]
date_pd = date_pd[start_point:]

# Create date array to execute strategy on - one for weekly, one for monthly, depending on context
dm = dfm.get_date_range(perf_df['price_date'].values[0], perf_df['price_date'].values[-1],
                                'monthly', context['start_day'], last_point_now=False)
dw = dfm.get_date_range(perf_df['price_date'].values[0], perf_df['price_date'].values[-1],
                                'weekly', 1, last_point_now=False)

# Use cw & cm to combine the dates to check on. If there is a date both as 'monthly' and 'weekly', pick 'monthly'
# The order of concatenation and np.unique is important for this to go correct
# !! Note to self: this is very specific to Strategy 3!!
dm_n = dfm.find_nearest_date(date_pd, dm, 'monthly')[0]
cm = np.ones(np.shape(dm_n))
dw_n = dfm.find_nearest_date(date_pd, dw, 'weekly')[0]
cw = np.zeros(np.shape(dw_n))

dr_c = np.concatenate([dm_n, dw_n])
cr_c = np.concatenate([cm, cw])

dr, ind_u = np.unique(dr_c, return_index=True)
cr = cr_c[ind_u]

dr_ind = 0
ind = 0
ordermatrix = np.zeros(shape=(np.shape(order)[0], np.shape(order)[1]+1))

while (ind < len(date_pd)) & (dr_ind < len(dr)):
    if (context['period'].lower() != 'daily'):
        ind = dr[dr_ind]
        context['check'] = 'monthly' if cr[dr_ind] == 1 else 'weekly'
        dr_ind += 1
    elif context['period'].lower() == 'daily':
        ind += 1

    a = RotationalETF(test_data.loc[:(ind + start_point), :], context, backtest=True)
    order[ind, :], log[ind] = a.calc_results()

    context['positions'] += order[ind, :]
    if sum(order[ind, :]) != 0:
        context['last_order'] = test_data.loc[ind + start_point, 'price_date']

    print ind, len(date_pd), context['check'], date_pd[ind]
    print context['positions']
    
    ordermatrix[ind, 0] = test_data.loc[ind+start_point, 'price_date']
    
    if np.amax(order[ind, :]) > 0:
        ordermatrix[ind, 1:] = order[ind,:] / np.amax(order[ind, :])
    elif np.amin(order[ind, :]) < 0:
        ordermatrix[ind, 1:] = order[ind,:] / np.abs(np.amin(order[ind, :]))
    else:
        ordermatrix[ind, 1:] = order[ind, :]
    
"""
Now to start the backtesting!!
"""

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
