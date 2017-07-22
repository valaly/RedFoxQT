import datetime as dt
import pandas as pd
import numpy as np


def cut_dates(df, start_date, end_date):
    if (start_date == 'default') or (start_date < df['price_date'].iloc[0]):
        start_date = df['price_date'].iloc[0]
    if (end_date == 'default') or (end_date > df['price_date'].iloc[-1]):
        end_date = df['price_date'].iloc[-1]

    df = df.loc[(df['price_date'] >= start_date) & (df['price_date'] <= end_date)].copy()
    return df


def merge_dfs(list_df):
    merged_df = None
    base_columns = ['open_price_', 'high_price_', 'low_price_', 'close_price_', 'adj_close_price_', 'volume_']

    for i, df in enumerate(list_df):
        new_columns = [x + str(i + 1) for x in base_columns]
        df.rename(columns={'open_price': new_columns[0]}, inplace=True)
        df.rename(columns={'high_price': new_columns[1]}, inplace=True)
        df.rename(columns={'low_price': new_columns[2]}, inplace=True)
        df.rename(columns={'close_price': new_columns[3]}, inplace=True)
        df.rename(columns={'adj_close_price': new_columns[4]}, inplace=True)
        df.rename(columns={'volume': new_columns[5]}, inplace=True)

        if i == 0:
            merged_df = df.ix[:, ['price_date'] + new_columns].copy()
        if i > 0:
            merged_df = merged_df.merge(df.ix[:, ['price_date'] + new_columns], how='left')

    return merged_df


def get_date_range(start_date, end_date, period, period_date=1, last_point_now=True):
    # start_date, end_date: string, format 'YYYY-MM-DD'
    # period: string, options: 'daily', 'weekly', 'biweekly', 'monthly', 'bimonthly', 'annually'
    # period_date: string, format string or integer, depending on when:
    #   weekly: 1 (Monday), 2 (Tuesday), ... 7 (Sunday)
    #   biweekly??
    #   monthly: 1, 2, ... , 28 (28-31 is automatically end of month)
    #   bimonthly??
    #   quarterly: for now, only the day can be switched
    #   annually: 'January 1', or 'jan 1' etc
    #   Only things to work for now: 'daily', 'monthly + period_date', 'annually, xth day of the year'

    # Convert start and end date to datetime
    start = dt.datetime.strptime(start_date, '%Y-%m-%d')
    end = dt.datetime.strptime(end_date, '%Y-%m-%d')

    dr = []
    if period.lower() == 'daily':
        # Daily is every calendar day --> shifting is hard to do with business days (what shifting??)
        dr = pd.date_range(start, end, freq='D').date

    elif period.lower() in ['week', 'weekly']:
        dr = pd.date_range(start, end, freq='W').date
        dr = dr + dt.timedelta(days=period_date)

    elif period.lower() in ['monthly', 'month']:
        freqm = 'MS'
        if type(period_date) is not int:
            period_date = 1
        if period_date >= 28:
            freqm = 'M'
            period_date = 1
        dr = pd.date_range((start + dt.timedelta(days=(1 - start.day))),
                            (end + dt.timedelta(days=(1 - end.day))), freq=freqm).date
        dr = dr + dt.timedelta(days=(period_date - 1))

    elif period.lower() in ['quarter', 'quarterly']:
        endyear = end.year + 1 if end.month > 1 else end.year
        dr = pd.date_range(dt.date(start.year, 1, 1), dt.date(endyear, 1, 1), freq='QS').date
        dr = dr + dt.timedelta(days=(int(period_date[3:]) - 1))

    elif period.lower() in ['annually', 'annual', 'yearly']:
        # For now annual means first day of the year
        endyear = end.year + 1 if end.month > 1 else end.year
        dr = pd.date_range(dt.date(start.year, 1, 1), dt.date(endyear, 1, 1), freq='AS').date
        if period_date != 1:
            month = int(period_date[0:2])
            day = int(period_date[3:])
            dr = np.array([dt.date(d.year, month, day) for d in dr])

    if last_point_now & (dr[-1] != end.date):
        dr[-1] = end.date()

    return dr


def find_nearest_date(dr, date, period):
    '''
    dr: serie to find dates in
    date: serie/string of dates to find
    '''
    if isinstance(date, pd.tslib.Timestamp) or isinstance(date, dt.date):
        date = [date]

    nearest_index = np.empty(np.shape(date)).astype(int)
    nearest_date = np.empty(np.shape(date)).astype(dt.date)

    for di, day in enumerate(date):
        ind = np.argmin(abs(dr - day))

        ih = il = ind
        if dr[ind] != day:
            ih = ind + 1 if ind < (len(dr) - 2) else ind
            il = ind - 1 if ind > 0 else ind

        if (period.lower() in ['week', 'weekly']) & (dr[ind].strftime('%W') != day.strftime('%W')):
            ind = ih if dr[ih].strftime('%W') == day.strftime('%W') else ind
            ind = il if dr[il].strftime('%W') == day.strftime('%W') else ind

        if (period.lower() == 'monthly') & (dr[ind].month != day.month):
            ind = ih if dr[ih].month == day.month else ind
            ind = il if dr[il].month == day.month else ind

        if (period.lower() in ['annually', 'annual', 'yearly']) & (dr[ind].year != day.year):
            ind = ih if dr[ih].year == day.year else ind
            ind = il if dr[il].year == day.year else ind

        nearest_index[di] = ind
        nearest_date[di] = dr[ind]

    if np.shape(date)[0] == 1:
        nearest_index = nearest_index[0]
        nearest_date = nearest_date[0]

    return nearest_index, nearest_date
