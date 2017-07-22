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


def merge_dfs(l_Df, vs_CommonCol, l_IncludeCols):
    """
        Description:        merges dataframes based on one column they have in common
        In:     
            l_Df            list of dataframes to be merged
            vs_CommonCol    name (string) of the column the dataframes should be merged on
            l_IncludeCols   list of the names of the columns that should be included in the
                                merged dataframe, if present in the original dataframes
    """
    # Make a copy of the original, just to be sure you're not changing the original
    l_DfCopy = l_Df
    
    df_Merged = None

    for vi_Index, df_Copy in enumerate(l_DfCopy):
        # Determine which columns should be included, and how they should be named
        l_OldNames = [x for x in df_Copy.columns if x in l_IncludeCols]
        l_NewNames = [x + '_' + str(vi_Index + 1) for x in l_OldNames]
        
        for vs_OldName, vs_NewName in zip(l_OldNames, l_NewNames):
            df_Copy.rename(columns={vs_OldName: vs_NewName}, inplace=True)
        
        # If this is the first dataframe, there is nothing to merge yet
        if vi_Index == 0:
            df_Merged = df_Copy.ix[:, [vs_CommonCol] + l_NewNames].copy()
        elif vi_Index > 0:
            df_Merged = df_Merged.merge(df_Copy.ix[:, [vs_CommonCol] + l_NewNames], how='left')

    return df_Merged


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
