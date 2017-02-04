from dbaccess import DatabaseManipulationSM
import matplotlib.pyplot as plt
from df_manipulation import *
import df_manipulation as dfm

dbSM = DatabaseManipulationSM()

dbSM.load('daily_price_SPY')
SPY_all = dbSM.data['daily_price_SPY']['content']

start_date = '1995-01-01'
end_date = '2015-01-01'
upgrade = 'monthly'
periodic_contribution = 500
npv_rate = 0.03

SPY = dfm.cut_dates(SPY_all, start_date, end_date)
SPY.index = np.arange(len(SPY.index))

dr = SPY['price_date']

# Get interval dates
date_pd = dfm.get_date_range(start_date, end_date, period=upgrade)

# Hoeveel stocks gekocht worden hangt af van closing price, NIET adj_close price
ind = dfm.find_nearest_date(pd.to_datetime(dr.values).date, date_pd, period=upgrade)[0]

orders = np.floor(periodic_contribution / SPY.loc[ind, 'close_price'].values)
price = SPY.loc[ind, 'close_price'].values

npv_invested = np.npv(npv_rate, np.ones(len(orders)) * periodic_contribution)

# Returns berekenen door bij te houden hoeveel stocks gekocht zijn, en tegen welke prijs.
cum_orders = np.cumsum(orders)
cum_invested = np.cumsum(orders * price)

total_orders = np.zeros(len(dr))
total_invested = np.zeros(len(dr))

for indi, i in enumerate(ind):
    if indi < (len(ind) - 1):
        total_orders[i:ind[indi + 1]] = cum_orders[indi]
        total_invested[i:ind[indi + 1]] = cum_invested[indi]
    else:
        total_orders[i:] = cum_orders[indi]
        total_invested[i:] = cum_invested[indi]

total_returned = total_orders * SPY['adj_close_price'].values

benchmark = SPY['adj_close_price'] / SPY['adj_close_price'].iloc[0] * npv_invested

price_date = pd.to_datetime(dr.values).date

fig = plt.figure()
plt.plot(price_date, benchmark, label='Benchmark')
plt.plot(price_date, total_returned, label='Dollar Cost Averaged')
plt.legend(loc='upper left')

fig = plt.figure()
plt.plot(price_date, total_invested, label='Total invested')
plt.plot(price_date, total_returned, label='Total returned')
plt.legend(loc='upper left')

plt.show()
