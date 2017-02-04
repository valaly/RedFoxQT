import os
import sys
import urllib2
import datetime as dt
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from holidays import Holiday
from downloader import WebsiteData
from presenter import Presenter


class DataCheck(object):
    def __init__(self, dataframe, ticker, country, exchange_abbrev, symbol):
        self.country = country
        self.ticker = ticker
        self.exchange = exchange_abbrev
        self.symbol_id = str(symbol)
        self.start_date = '1995-01-01'
        self.orig_names = ['open_price', 'close_price', 'high_price', 'low_price', 'adj_close_price', 'volume']

        self.full_data = self.get_start_part(dataframe, self.start_date)

        checker = self.full_data.data_checked.copy()
        checker0 = checker[:-1]
        '''
        ind_changes = [index for index, item in enumerate(checker0) if item != checker[index + 1]]
        if not ind_changes:
            self.full_data.loc[:, 'data_checked'] = False
        else:
            self.full_data['data_checked'].ix[:ind_changes[-1]] = True
            self.full_data['data_checked'].ix[(ind_changes[-1] + 1):] = False
        '''
        self.unchecked_data = self.get_unchecked_part(self.full_data)

        ##########
        #self.data = self.get_start_part(self.get_unchecked_part(dataframe), self.start_date)
        #self.price_date = self.data.price_date

    def find_missing_data(self):
        if not os.path.exists('Data_Checks'):
            os.makedirs('Data_Checks')
        location = 'Data_Checks'

        missing_dates = []
        holiday_list = Holiday(self.country)

        # Determine where to start
        dates = self.unchecked_data['price_date']
        if self.start_date > self.unchecked_data['price_date'][0]:
            dates = dates.loc[self.unchecked_data['price_date'] >= self.start_date]
            dates.index = range(0, len(dates))

        date0 = dt.datetime.strptime(dates[0], '%Y-%m-%d').date()
        for index, date in enumerate(dates):
            if index == 0:
                continue
            date1 = dt.datetime.strptime(date, '%Y-%m-%d').date()

            # Find which day it should be, taking weekend into account
            day_inc = 1
            if date0.weekday() == 4:
                day_inc = 3
            date_shouldbe = date0 + dt.timedelta(days=day_inc)

            # date1 should be day after date0
            if date1 != date_shouldbe:
                # Check if it's a holiday
                hlist = holiday_list.holidays(date_shouldbe.year)
                if date_shouldbe not in hlist:
                    missing_dates.append(date_shouldbe)

            # Define new date0
            date0 = date1

        if len(missing_dates) != 0:
            with open(''.join([location, '/', self.ticker, '_', self.symbol_id,
                               '_missing_dates.txt']), 'w') as file_miss:
                for item in missing_dates:
                    print>> file_miss, item.isoformat()

        return missing_dates

    def compare_to_other_dataset(self):
        if not os.path.exists('Data_Checks'):
            os.makedirs('Data_Checks')
        location = 'Data_Checks'

        df_2 = self.get_second_dataset()
        df_3 = self.get_third_dataset()

        comp_df = df_2
        comp2_df = df_3
        orig_df = self.unchecked_data

        semi_new_df = orig_df.merge(comp_df, how='left')
        new_df = semi_new_df.merge(comp2_df, how='left')

        # Start comparing the values
        dif_df = pd.DataFrame(index=[],
                              columns=['id', 'price_date', 'item', 'suggested_value', 'original_value',
                                       'second_value', 'third_value', 'diff_perc_1to2', 'diff_perc_1to3'])

        comp_names = ['Open', 'Close', 'High', 'Low', 'Adj_Close', 'Volume']
        comp2_names = ['Open2', 'Close2', 'High2', 'Low2', 'Adj_Close2', 'Volume2']

        vol_cap = 5  # [%]
        price_cap = 0.1  # [%]

        for index, name in enumerate(self.orig_names):
            try:
                dif_tmp = new_df.loc[np.round(new_df[name], 2) != new_df[comp_names[index]]]
                dif_val = dif_tmp.loc[np.round(dif_tmp[name], 2) != dif_tmp[comp2_names[index]]]
                dif_select = dif_val.ix[:, ['id', 'price_date', name, comp_names[index], comp2_names[index]]]

                dif_select.loc[:, 'item'] = [name] * len(dif_select)
                dif_select.rename(columns={name: 'original_value'}, inplace=True)
                dif_select.rename(columns={comp_names[index]: 'second_value'}, inplace=True)
                dif_select.rename(columns={comp2_names[index]: 'third_value'}, inplace=True)
                temp = dif_select.second_value.loc[
                    dif_select.second_value == dif_select.third_value]
                dif_select.loc[temp.index, 'suggested_value'] = temp.values
                dif_select.loc[:, 'diff_perc_1to2'] = np.round(((dif_select.original_value.T / dif_select.second_value)
                                                                * 100 - 100).T, 2)
                dif_select.loc[:, 'diff_perc_1to3'] = np.round(((dif_select.original_value.T / dif_select.third_value)
                                                                * 100 - 100).T, 2)

                if name == 'volume':
                    dif_caps = dif_select.loc[((dif_select.diff_perc_1to2.abs() > vol_cap)
                                              & (dif_select.diff_perc_1to3.abs() > vol_cap))
                                              | ((dif_select.diff_perc_1to2.isnull())
                                              & (dif_select.diff_perc_1to3.isnull()))]
                else:
                    dif_caps = dif_select.loc[((dif_select.diff_perc_1to2.abs() > price_cap)
                                              & (dif_select.diff_perc_1to3.abs() > price_cap))
                                              | ((dif_select.diff_perc_1to2.isnull())
                                              & (dif_select.diff_perc_1to3.isnull()))]

                dif_df = pd.concat([dif_df, dif_caps.reindex_axis(dif_df.columns, axis=1)])

            except KeyError:
                print ''.join(['Item ', comp_names[index], ' was not available in the comparable dataset.'])
                continue

        dif_df = dif_df.sort_index(by='price_date', ascending=True)

        if not dif_df.empty:
            dif_df.to_csv(''.join([location, '/', self.ticker, '_', self.symbol_id,
                                   '_difference_data.csv']), index=False)
            df_2.to_csv(''.join([location, '/', self.ticker, '_', self.symbol_id,
                                '_QUANDL_data.csv']), index=False)

        return dif_df

    def compare_to_moving_average(self, window):
        if not os.path.exists('Data_Checks'):
            os.makedirs('Data_Checks')
        location = 'Data_Checks'

        pres = Presenter()
        pres.start_presentation(title=''.join(['Data Checks ', self.ticker]),
                                subtitle=dt.datetime.today().date().isoformat())
        mov_df = pd.DataFrame(index=[], columns=['id', 'price_date', 'item', 'value', 'lower_limit', 'upper_limit'])

        for name in self.orig_names:
            mov_avg = pd.rolling_mean(self.unchecked_data[name], window=window, min_periods=1)
            mov_std = pd.rolling_std(self.unchecked_data[name], window=window, min_periods=1)

            num_std = 3
            # Determine range
            up_lim = mov_avg + num_std * mov_std
            low_lim = mov_avg - num_std * mov_std

            # Plot it
            dates = pd.to_datetime(self.unchecked_data['price_date'])
            fig = plt.figure()
            plt.xticks(rotation=45)
            plt.gcf().subplots_adjust(bottom=0.15)
            plt.plot(dates.values, self.unchecked_data[name], 'r', label='Raw data')
            plt.plot(dates.values, mov_avg, 'b', label='Moving average')
            plt.plot(dates.values, up_lim, 'g', label=''.join([str(num_std), 'std']))
            plt.plot(dates.values, low_lim, 'g')
            plt.xlabel('Time')
            plt.ylabel('Value')
            plt.legend(loc='upper left')
            img_path = ''.join(['temp', self.ticker, '.png'])
            plt.savefig(img_path)
            plt.close(fig)

            pres.add_picture_slide(img_path, title=name)

            # Find all values that lie outside of this range
            extr = self.unchecked_data.loc[(self.unchecked_data[name] > up_lim) | (self.unchecked_data[name] < low_lim)]

            # Add to list
            extr_select = extr.ix[:, ['id', 'price_date', name]]

            extr_select.loc[:, 'item'] = [name] * len(extr_select)
            extr_select.loc[:, 'upper_limit'] = up_lim[extr_select.index]
            extr_select.loc[:, 'lower_limit'] = low_lim[extr_select.index]
            extr_select.rename(columns={name: 'value'}, inplace=True)

            mov_df = pd.concat([mov_df, extr_select.reindex_axis(mov_df.columns, axis=1)])

        # Print list
        mov_df.to_csv(''.join([location, '/', self.ticker, '_', self.symbol_id,
                               '_moving_avg_data.csv']), index=False)
        pres.save_presentation(''.join([location, '/', self.ticker, '_', self.symbol_id,
                                        '_plots.pptx']))

        os.remove(img_path)

        return mov_df

    def adjust_daily_price(self, path=None, final=False):
        new_df = self.full_data.copy()

        if path is not None:
            df = pd.read_csv(path)

            fix = df.loc[~df.suggested_value.isnull()]
            for ind in fix.index:
                # Adjust the dataframe
                new_df.loc[int(fix.id[ind]), fix.item[ind]] = fix.suggested_value.loc[ind]

                # Change the "last_updated_date"
                new_df.loc[int(fix.id[ind]), 'last_updated_date'] = dt.datetime.today().date().isoformat()

        if final:
            new_df.loc[:, 'data_checked'] = [True] * len(new_df)

        return new_df

    def compute_split_div_adj(self):
        if not os.path.exists('Data_Checks'):
            os.makedirs('Data_Checks')
        location = 'Data_Checks'

        # Always check starting with the oldest datapoint that hasn't been checked yet (that date is included then)
        sd_df = self.get_split_dividend_data(self.unchecked_data.price_date[0])

        adj_cl_df = self.full_data.ix[:, ['id', 'created_date', 'last_updated_date', 'data_checked', 'price_date',
                                          'adj_close_price', 'close_price']].copy()
        #adj_cl_df.rename(columns={'close_price': 'comp_adj_close'}, inplace=True)
        adj_cl_df.loc[:, 'comp_adj_close'] = adj_cl_df.ix[:, 'adj_close_price']
        index_false = adj_cl_df['data_checked'] == False
        adj_cl_df.loc[index_false, 'comp_adj_close'] = adj_cl_df.loc[index_false, 'close_price']

        for ind in reversed(sd_df.index):
            # Find index of corresponding date in daily_price dataframe
            tmp_ind = adj_cl_df.comp_adj_close.loc[adj_cl_df.price_date == sd_df.Date[ind]].index
            cl_price = adj_cl_df.comp_adj_close[tmp_ind - 1].values
            ind_to_change = adj_cl_df.loc[adj_cl_df.price_date < sd_df.Date[ind]].index

            if sd_df.Type[ind] == 'DIVIDEND':
                fac = (cl_price - float(sd_df.Rate[ind])) / cl_price
            elif sd_df.Type[ind] != 'SPLIT':
                print 'Did not recognize the type in the dividend/split adjustment, need to check this out!'
                fac = 1
            elif sd_df.Type[ind] == 'SPLIT':
                fac = 1

            # Computed adj. close data
            adj_cl_df.loc[ind_to_change, 'comp_adj_close'] = adj_cl_df.comp_adj_close.loc[ind_to_change] * fac
            ###
            #adj_cl_df.loc[ind_to_change, 'close_price'] *= fac
        ### NOW JUST MAKE SURE THAT IT ALSO AUTOMATICALLY UPDATES THE SAVED DAILY PRICE CLOSE PRICE
        # Should probably adjust the 'adjust_daily_price' thing?

        dif_df = adj_cl_df.loc[np.round(adj_cl_df.adj_close_price, 2) != np.round(adj_cl_df.comp_adj_close, 2)].copy()

        # Add a column of suggested value and insert the new adj_close_price
        # if created_date and last_updated_date aren't the same
        dif_df.loc[:, 'suggested_value'] = dif_df.comp_adj_close.loc[(dif_df.created_date != dif_df.last_updated_date)
                                                                     | (dif_df.data_checked == True)]
        dif_df.loc[:, 'item'] = ['adj_close_price'] * len(dif_df)

        # Save it as csv
        if not dif_df.empty:
            dif_df.to_csv(''.join([location, '/', self.ticker, '_', self.symbol_id,
                                   '_split_div_data.csv']), index=False)

        return dif_df

    def get_second_dataset(self):

        web = WebsiteData()
        df = web.get_quandl_data(self.ticker, self.exchange)

        df.rename(columns={'Date': 'price_date'}, inplace=True)
        df.rename(columns={'Adj. Close': 'Adj_Close'}, inplace=True)

        return df

    def get_third_dataset(self):
        # First option: get it from file --> going to do nasty stuff for this:
        # Should always be placed in Data_Checks folder
        # And name should be TICKER_SYMBOLID_NASDAQ.csv (so for example GOOGL_1_NASDAQ_data.csv)
        path = ''.join(['Data_Checks/', self.ticker, '_', self.symbol_id, '_NASDAQ_data.csv'])
        if os.path.exists(path):
            df = pd.read_csv(path)

            data_length = len(df)
            df = df.iloc[::-1]
            df.index = range(0, data_length)

            # Last row is not a date but a time, so should be dropped
            df = df.drop(df.tail(1).index)

            df.Volume2 = df.Volume2.astype(float)

            df.loc[:, 'date'] = pd.to_datetime(df.price_date).apply(lambda x: x.strftime('%Y-%m-%d'))

        else:
            wb = WebsiteData()

            # Weer lelijk stukje:
            website = ''.join(['http://www.nasdaq.com/symbol/', self.ticker, '/historical'])

            df = wb.get_nasdaq_data(website)

            data_length = len(df)
            df = df.iloc[::-1]
            df.index = range(0, data_length)

        df.rename(columns={'date': 'price_date'}, inplace=True)
        df.rename(columns={'open': 'Open2'}, inplace=True)
        df.rename(columns={'high': 'High2'}, inplace=True)
        df.rename(columns={'low': 'Low2'}, inplace=True)
        df.rename(columns={'close': 'Close2'}, inplace=True)
        df.rename(columns={'volume': 'Volume2'}, inplace=True)

        return df

    def get_split_dividend_data(self, start_date):

        end_date = dt.datetime.today().strftime('%Y-%m-%d')

        web = WebsiteData()
        df = web.get_yahoo_splitdiv(self.ticker, start_date, end_date)
        df_more = df

        while np.shape(df_more)[0] > 85:
            df_more = web.get_yahoo_splitdiv(self.ticker, start_date, df['Date'].iloc[-1])
            df = pd.concat([df, df_more.loc[1:]])
            df.index = range(0, len(df))

        # In case an item turns out to be incorrect
        #df.loc[22, 'Rate'] = 0
        #print df

        return df

    @staticmethod
    def get_unchecked_part(data):
        checker = data.data_checked
        checker0 = checker[:-1]

        ind_changes = [index for index, item in enumerate(checker0) if item != checker[index + 1]]

        if checker.iloc[-1] == True:
            return None
        elif not ind_changes:  # if the list is empty, aka, none of the values have been checked yet
            return data
        else:
            new_data = data.ix[(ind_changes[-1] + 1):, :].copy()
            new_data.index = range(0, len(new_data))
            return new_data

    @staticmethod
    def get_start_part(data, start_date):
        if start_date > data.price_date[0]:
            data = data.loc[data.price_date >= start_date]
            data.index = range(0, len(data))
        return data
