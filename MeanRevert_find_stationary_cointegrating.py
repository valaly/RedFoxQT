from meanrevert import MeanReverting
from dbaccess import DatabaseManipulationSM
import pandas as pd

symbols = range(0, 104)
start_date = '2011-01-01'
end_date = '2015-07-15'

dbSM = DatabaseManipulationSM()
dbSM.load('exchange')
dbSM.load('symbol')
index = range(0,2025)
df = pd.DataFrame(index=index, columns=['ticker', 'adf', 'hurst', 'half_life', 'cadf'])

for ind in symbols:
    ticker = dbSM.data['symbol']['content'].ticker[symbols[ind]]
    name = ''.join(['daily_price_', ticker])
    dbSM.load(name)

line = 0
for ind1 in symbols:
    name1 = ''.join(['daily_price_', dbSM.data['symbol']['content'].ticker[symbols[ind1]]])
    y1_adj = dbSM.data[name1]['content'].ix[:, ['price_date', 'adj_close_price']]

    if y1_adj['price_date'].iloc[0] > start_date:
        continue

    for ind2 in symbols[(ind1 + 1):]:
        name2 = ''.join(['daily_price_', dbSM.data['symbol']['content'].ticker[symbols[ind2]]])
        y2_adj = dbSM.data[name2]['content'].ix[:, ['price_date', 'adj_close_price']]

        if y2_adj['price_date'].iloc[0] > start_date:
            continue

        mr = MeanReverting(df1=y1_adj, df2=y2_adj, start_date=start_date, end_date=end_date)
        print ind1, ind2, line
        # Write lines to csv if either one of them is likely to be stationary, or combined cointegrating
        if (mr.df['cadf']['certainty'] >= 0.9) & (mr.df['AR']['half_life'] < 20):
            # Write tickers, mr.df['AR']['half_life'], mr.df['cadf']['certainty']
            df.loc[line, 'ticker'] = ''.join([dbSM.data['symbol']['content'].ticker[symbols[ind1]], '_',
                                              dbSM.data['symbol']['content'].ticker[symbols[ind2]]])
            df.loc[line, 'cadf'] = mr.df['cadf']['certainty']
            df.loc[line, 'half_life'] = mr.df['AR']['half_life']
            line += 1

    if (mr.df1['adf']['certainty'] >= 0.9) & (mr.df1['hurst']['results'] < 0.5):
            df.loc[line, 'ticker'] = dbSM.data['symbol']['content'].ticker[symbols[ind1]]
            df.loc[line, 'adf'] = mr.df1['adf']['certainty']
            df.loc[line, 'hurst'] = mr.df1['hurst']['results']
            line += 1

df.to_csv('Stationary_cointegrating.csv')
