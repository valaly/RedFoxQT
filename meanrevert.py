import statsmodels.tsa.stattools as ts
import statsmodels.api as sm
import pandas as pd
import math as m
import numpy as np
from numpy import log, polyfit, sqrt, std, subtract
from pandas.stats.api import ols


class MeanReverting(object):

    def __init__(self, df1, df2=None, date_col='price_date', price_col='adj_close_price', start_date='default',
                 end_date='default'):
        self.start_date = start_date
        self.end_date = end_date
        df1.rename(columns={price_col: 'price1'}, inplace=True)
        df1.rename(columns={date_col: 'date'}, inplace=True)
        self.df1 = {}
        self.df1['data'] = self._cut_dates(df1, self.start_date, self.end_date)
        self.df1['adf'] = self.comp_adf(self.df1['data']['price1'])
        self.df1['hurst'] = self.comp_hurst(self.df1['data']['price1'])
        self.df1['AR'] = self.comp_AR(self.df1['data']['price1'])

        if ~df2.empty:
            df2.rename(columns={price_col: 'price2'}, inplace=True)
            df2.rename(columns={date_col: 'date'}, inplace=True)
            self.df2 = {}
            self.df2['data'] = self._cut_dates(df2, start_date, end_date)
            self.df2['hurst'] = self.comp_hurst(self.df2['data']['price2'])
            self.df2['adf'] = self.comp_adf(self.df2['data']['price2'])
            self.df2['AR'] = self.comp_AR(self.df2['data']['price2'])

            self.df = {}
            self.df['data'] = self._merge_df(df1, df2, start_date, end_date)
            self.df['cadf'], self.df['data']['price_comb'] = self.comp_cadf(self.df['data'])
            self.df['AR'] = self.comp_AR(self.df['data']['price_comb'])

    def comp_adf(self, price):
        res = ts.adfuller(price, 1)

        adf = {}
        adf['results'] = {'test_stat': res[0],
                          'p_value': res[1],
                          'no_datapoint': res[3],
                          '1%': res[4]['1%'],
                          '5%': res[4]['5%'],
                          '10%': res[4]['10%']}

        if res[0] < res[4]['1%']:
            adf['certainty'] = 0.99
        elif res[0] < res[4]['5%']:
            adf['certainty'] = 0.95
        elif res[0] < res[4]['10%']:
            adf['certainty'] = 0.90
        else:
            adf['certainty'] = 0

        return adf

    def comp_hurst(self, price):
        # Create the range of lag values
        lags = range(2, 100)

        # Calculate the array of the variances of the lagged differences
        tau = [sqrt(std(subtract(price[lag:], price[:-lag]))) for lag in lags]

        # Use a linear fit to estimate the Hurst Exponent
        poly = polyfit(log(lags), log(tau), 1)

        # Return the Hurst exponent from the polyfit output
        hurst = {}
        hurst['results'] = poly[0]*2.0

        if hurst['results'] < 0.5:
            hurst['certainty'] = 1 - hurst['results']*2
        else:
            hurst['certainty'] = 0

        return hurst

        # Output:
        # Hurst Exponent H
        # H < 0.5:  mean-reverting
        # H = 0.5:  geometric brownian walk
        # H > 0.5:  trending
        # H around 0 means strongly mean reverting, H around 1 means strongly trending

    def comp_AR(self, price):
        AR = {}
        mod = sm.tsa.AR(np.asarray(price), freq='B')
        res = mod.fit(maxlag=1)
        AR['parameters'] = res.params
        AR['phi1'] = res.params[1]
        AR['half_life'] = m.log(0.5)/m.log(AR['phi1'])
        return AR

    def comp_cadf(self, df):
        # Calculate optimal hedge ratio "beta"
        res = ols(y=df['price1'], x=df['price2'])
        beta_hr = res.beta.x

        # Calculate the residuals of the linear combination
        df["res"] = df['price1'] - beta_hr*df['price2']

        # Calculate and output the CADF test on the residuals
        cadf = self.comp_adf(df["res"])
        cadf['beta'] = beta_hr

        return cadf, df['res']

    def _cut_dates(self, df, start_date, end_date):
        if (start_date == 'default') or (start_date < df['date'].iloc[0]):
            start_date = df['date'].iloc[0]
        if (end_date == 'default') or (end_date > df['date'].iloc[-1]):
            end_date = df['date'].iloc[-1]

        df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)]

        return df

    def _merge_df(self, df1, df2, start_date, end_date):
        # Merge the two
        df = df1.merge(df2, how='left')

        # Calculate min_start_date and max_end_date
        if df1['date'].iloc[0] < df2['date'].iloc[0]:
            min_start_date = df2['date'].iloc[0]
        else:
            min_start_date = df1['date'].iloc[0]
        if df1['date'].iloc[-1] < df2['date'].iloc[-1]:
            max_end_date = df1['date'].iloc[-1]
        else:
            max_end_date = df2['date'].iloc[-1]

        if (start_date == 'default') or (start_date < min_start_date):
            start_date = min_start_date
        if (end_date == 'default') or (end_date > max_end_date):
            end_date = max_end_date

        df = df.loc[(df['date'] >= start_date) & (df['date'] <= end_date)]

        return df
