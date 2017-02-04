from strategy3 import RotationalETF
from dbaccess import DatabaseManipulationSM
# from backtesting import Backtesting
import df_manipulation as dfm
import numpy as np


dbSM = DatabaseManipulationSM()

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
names = np.array(['IWM', 'SPY', 'EFA', 'ICF', 'DBC', 'VWO', 'IAU', 'TLT', 'SHY'])
long_names = np.array(['iShares Russell 2000',
                       'SPDR S&P 500',
                       'iShares MSCI EAFE',
                       'iShares Cohen & Steers REIT',
                       'PowerShares DB Commodity Tracking',
                       'Vanguard FTSE Emerging Markets',
                       'iShares Gold Trust',
                       'iShares 20+ Year Treasury Bond',
                       'iShares 1-3 Year Treasury Bond'])

context = {}

# Parameters
context['start_date'] = '2012-01-01'
# context['end_date'] = '2015-06-27'
context['weights'] = np.array([1, 1, 1, -1])
context['top_in'] = 1
context['top_out'] = 1
context['period'] = 'monthly'
context['max_drawdown'] = 0.05

data_cut = [None] * len(data)
for i, df in enumerate(data):
    data_cut[i] = dfm.cut_dates(df, context['start_date'], 'default')
df_merged = dfm.merge_dfs(data_cut)

comp_price_type = 'adj_close_price'
column_names = ['price_date'] + [x for x in df_merged.columns.values if x.startswith(comp_price_type)]
comp_data = df_merged.loc[:, column_names]

for i, name in enumerate(column_names[1:]):
    comp_data.rename(columns={name: ''.join(['price_', str(i + 1)])}, inplace=True)

# To adjust
context['last_order'] = '2016-10-26'
context['max_notional'] = 1100
context['positions'] = np.array([0, 8, 0, 0, 0, 0, 0, 0, 0])
context['check'] = 'monthly'
context['start_day'] = 26


a = RotationalETF(comp_data, context)
order, log = a.calc_results()

print names[order != 0]
print long_names[order != 0]
print order
price_names = np.array(column_names[1:])
print df_merged[price_names[order != 0]].iloc[-1].values

"""
# To backtest
plot_data = {}
plot_data['benchmark'] = SPY
bt = Backtesting(context, comp_data, plot=True, plot_title='Backtesting_2012onward.pptx')
"""