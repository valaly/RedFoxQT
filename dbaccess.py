# Is called by:
#   - tcm

import re
import os
import pandas as pd
import datetime as dt
from downloader import WebsiteData
from bs4 import BeautifulSoup


class DatabaseManipulation(object):
    def __init__(self, name, file_csv):
        self.name = name
        self.fileCsv = file_csv
        self.fileInfo = pd.read_csv(self.fileCsv)

        self.data = {'main': {'name': self.fileCsv,
                              'header': self.fileInfo.columns.values,
                              'content': self.fileInfo}}

    def load(self, db_name):
        """Loads database file and adds it to the object
        Input:
            db_name                 name of database file (e.g. 'data_vendor')
                                    :type db_name: string
        Output:
            object.data[db_name]    name, path, and content of database file in dictionary format
        """
        if db_name == 'main':
            self.fileInfo = pd.read_csv(self.fileCsv)
            self.data['main']['content'] = self.fileInfo
            return

        col_name = 'name'
        csv_name = ''.join([db_name, '.csv'])

        if self.fileInfo.loc[self.fileInfo[col_name] == csv_name].empty:
            print ''.join(["Filename ", db_name, " is not present"])
            return
        else:
            db_entry = self.fileInfo.loc[self.fileInfo[col_name] == csv_name]
            index = db_entry.index.values[0]
            print 'Current path: ', os.getcwd()
            #db_path = os.path.join(db_entry.path[index], db_entry.name[index])
            db_path = ''.join(['../', db_entry.path[index], '/', db_entry.name[index]])
            db_info = pd.read_csv(db_path)
            dic = {'name': db_entry.name[index],
                   'path': db_entry.path[index],
                   'header': db_info.columns.values,
                   'content': db_info}
            self.data[db_name] = dic

            return dic

    def save_csv(self, name, dataframe):
        path = ''.join(['../', self.data[name]['path'], '/', self.data[name]['name']])
        dataframe.to_csv(path, index=False)

    #@staticmethod
    #def get_entries(df_name, col_name, val_name):
    #    return df_name.loc[df_name[col_name] == val_name]


class DatabaseManipulationSM(DatabaseManipulation):
    def __init__(self):
        name = 'Securities Master Database'
        file_csv = '../dbSM_fileInfo.csv'
        DatabaseManipulation.__init__(self, name, file_csv)

    def get_website_url(self, vendor_id, ticker):
        if 'data_vendor' not in self.data:
            self.load('data_vendor')

        web_template = self.data['data_vendor']['content'].website_url[vendor_id]
        website = web_template.replace('TICKER', ticker)
        return website

    def get_API_url(self, vendor_id, ticker):
        if 'data_vendor' not in self.data:
            self.load('data_vendor')

        API_template = self.data['data_vendor']['content'].API[vendor_id]
        API_url = API_template.replace('TICKER', ticker)
        return API_url

    def create_daily_price_csv(self, df, data_vendor, symbol_id, ticker):
        """Creates csv file for daily_price csv and adds line for csv to main file
        Input:
            df              dataframe with daily prices (e.g., Yahoo data)
            data_vendor     data vendor ID
            symbol_id       symbol ID
        """
        self.load('main')

        # Reverse order of data frame - in order to append new data at the end, and not keep changing data_point_id's
        data_length = len(df)
        df = df.iloc[::-1]
        df.index = range(0, data_length)

        date_string = dt.datetime.now().date().isoformat()

        # Fix dataframe format
        dp_df = self.fix_daily_price_format(data_vendor, symbol_id, df)

        # Adjust for splits
        dp_df = self.adjust_splits(dp_df, ticker, dp_df['price_date'][0])

        # Create csv file
        path = self.data['daily_price_template']['path']
        file_name = ''.join(['daily_price_', ticker, '.csv'])
        full_file = ''.join([path, '\\', file_name])
        dp_df.to_csv(full_file, index=False)

        # Add line for csv file to main file
        ind = max(self.data['main']['content'].index) + 1
        mf_df = pd.DataFrame(index=[ind], columns=self.data['main']['header'])
        mf_df.id = ind
        mf_df.name = file_name
        mf_df.path = path
        mf_df.created_date = date_string
        mf_df.last_updated_date = date_string
        mf_df.to_csv(self.data['main']['name'], index=False, header=False, mode='a')

    def update_daily_price_csv(self, df, data_vendor, symbol_id, ticker):
        """Creates csv file for daily_price csv and adds line for csv to main file
        Input:
            df              dataframe with daily prices (e.g., Yahoo data)
            data_vendor     data vendor ID
            symbol_id       symbol ID
        """
        # Load daily_price csv
        file_name = ''.join(['daily_price_', ticker])
        self.load(file_name)

        # Find latest date (will be at the bottom of csv file)
        last_date = self.data[file_name]['content'].iloc[-1]
        last_index = int(last_date.id)

        # Find this last date in new data
        last_entry = df.loc[df['Date'] == last_date.price_date]
        if last_entry.empty:
            print ''.join([ticker, ' already has more data points than the online csv?'])
            return 1    # 1 = error

        # Get the entries above this last date (aka newer entries)
        newer_entries = df.iloc[range(0, last_entry.index.values)]


        # If there are no newer entries, inform that the csv is up to date and stop
        if newer_entries.empty:
            print ''.join([ticker, ' is already up to date'])
            return 0

        # Reverse their sequence
        new_df = newer_entries.iloc[::-1]
        new_df.index = range(last_index + 1, last_index + 1 + len(new_df))

        # Convert it to a desired format
        fixed_df = self.fix_daily_price_format(data_vendor, symbol_id, new_df)

        # Add it to the existing dataframe
        df = pd.concat([self.data[file_name]['content'], fixed_df])

        # Adjust for splits
        df = self.adjust_splits(df, ticker, fixed_df['price_date'][fixed_df.index[0]])

        # Overwrite existing csv
        path = ''.join(['../', self.data[file_name]['path'], '/', self.data[file_name]['name']])
        df.to_csv(path, index=False)

        # Add it to the existing csv (to_csv)
        #fixed_df.to_csv(path, index=False, header=False, mode='a')

        return 0

    def fix_daily_price_format(self, vendor_id, symbol_id, old_df):
        if 'daily_price_template' not in self.data:
            self.load('daily_price_template')

        # Determine length of data_frame
        data_length = len(old_df)
        ind = old_df.index

        new_df = pd.DataFrame(index=ind, columns=self.data['daily_price_template']['header'])

        # Create id, data_vendor_id, and symbol_id column
        new_df.id = ind
        new_df.data_vendor_id = [vendor_id] * data_length
        new_df.symbol_id = [symbol_id] * data_length

        # Assign price_date, open_price, low_price, high_price, close_price, adj_close_price, volume column
        old_df.rename(columns={'Adj Close': 'Adj_Close'}, inplace=True)
        new_df.price_date = old_df.Date
        new_df.open_price = old_df.Open
        new_df.low_price = old_df.Low
        new_df.high_price = old_df.High
        new_df.close_price = old_df.Close
        new_df.adj_close_price = old_df.Adj_Close
        new_df.volume = old_df.Volume

        # Create created_date and last_updated_date column
        date_string = dt.datetime.now().date().isoformat()
        new_df.created_date = [date_string]*data_length
        new_df.last_updated_date = date_string

        # Create data_checked column
        new_df.data_checked = [False] * data_length

        return new_df

    def adjust_splits(self, df, ticker, start_date):
        end_date = dt.datetime.today().strftime('%Y-%m-%d')
        web = WebsiteData()

        splitdiv = web.get_yahoo_splitdiv(ticker, start_date, end_date)

        # Only selects splits, not dividend
        splits = splitdiv.loc[splitdiv['Type'] == 'SPLIT']

        # Adjust all unadjusted prices
        for ind in reversed(splits.index):
            tmp_ind = df.loc[df['price_date'] == splits['Date'][ind]].index
            ind_to_change = df.loc[df['price_date'] < splits['Date'][ind]].index

            splitting = map(float, splits['Rate'][ind].split(':'))
            fac = splitting[1] / splitting[0]

            df.loc[ind_to_change, ['open_price', 'high_price', 'low_price', 'close_price']] *= fac

        # Return df
        return df

    def create_fundamental_data_csv(self, site):
        key_words_bs = ['total\s*current\s*assets', 'total\s*current\s*liabilities', 'total\s*assets',
                        'total\s*liabilities']

        wd = WebsiteData()

        rd1 = wd.get_raw_data(site)[0]
        cut1 = wd.get_tagged_string(rd1.lower(), '<table ', '</table>')

        bs_table = [None] * len(cut1[0])
        for i, c in enumerate(cut1[0]):
            correct_table = True
            for word in key_words_bs:
                if not re.findall(word, c.lower()):
                    correct_table = False
                    break
            if not correct_table:
                continue
            bs_table[i] = c

        bs_table = [t for t in bs_table if t is not None]
        if len(bs_table) > 1:
            print "More than one balance sheet found!!"

        text = ''.join(['<table ', bs_table[0], '</table>'])

        soup = BeautifulSoup(text, 'lxml')
        rows = soup.find('table').findChildren('tr')

        values = [None] * len(rows)
        for i, r in enumerate(rows):
            col = r.findChildren('font')
            #col = r.findChildren(['font', 'p'])
            values[i] = [c.text.encode(errors='ignore') for c in col]
            values[i] = [v for v in values[i] if v not in ['', '$', ')', ' ', '*']]
            for j, v in enumerate(values[i]):
                try: # See if the value is a number
                    values[i][j] = int(v.replace(',', ''))
                except ValueError:
                    try:
                        values[i][j] = int(v.replace(',', '').replace('(', '-'))
                    except ValueError:
                        values[i][j] = v

        values = [v for v in values if v != []]

        if (type(values[0][-1]) == int) & (values[0][-1] > 1950) & (values[0][-1] < 2050):
            header = values[0]
            tmp_df = pd.DataFrame(values[1:])
        if (type(values[1][-1]) == int) & (values[1][-1] > 1950) & (values[1][-1] < 2050):
            header = values[1]
            tmp_df = pd.DataFrame(values[2:])
        print tmp_df
        # Items to retrieve
        tags = [['total\s*current\s*assets'],
                ['total\s*current\s*liabilities'],
                ['cash\s*and\s*cash\s*equivalents', 'cash\s*and\s*equivalents'],
                ['inventory', 'inventories'],
                ['accounts\s*receivable']]

        df_header = ['Total Current Assets',
                     'Total Current Liabilities',
                     'Cash and Cash Equivalents',
                     'Inventory',
                     'Accounts Receivable']

        df_years = [h for h in header if type(h) is int]

        comp_df = pd.DataFrame(columns=['item', 'year', 'value'])

        # Fix the tmp_df in case there are unnecessary columns messing things up
        last_row = len(tmp_df.columns) - 1
        if len(tmp_df.columns) > (len(df_years) + 1):
            nan_ind = tmp_df[pd.isnull(tmp_df.iloc[:, last_row])].index
            tmp_df.iloc[nan_ind, (last_row + 1 - len(df_years)):] = tmp_df.iloc[nan_ind, (last_row - len(df_years)):last_row].values
            tmp_df.drop((last_row - len(df_years)), axis=1, inplace=True)

        for i, t in enumerate(tags):
            tmp_row = tmp_df.loc[tmp_df.loc[:, 0].str.lower().str.contains('|'.join(t))]

            for j, y in enumerate(df_years):
                comp_df.loc[(len(df_years) * i + j), 'item'] = df_header[i]
                comp_df.loc[(len(df_years) * i + j), 'year'] = y
                if not tmp_row.empty:
                    comp_df.loc[(len(df_years) * i + j), 'value'] = tmp_row.iloc[0,
                                                               (len(tmp_df.columns) - len(df_years) + j)]
                    if (df_header[i] == 'Accounts Receivable') & ('net' not in tmp_row.iloc[0, 0]):
                        print 'Unsure if Accounts Receivable is net of allowances. Text on balance sheet reads:'
                        print ''.join(['"', tmp_row.iloc[0, 0], '"'])
                else:
                    comp_df.loc[(len(df_years) * i + j), 'value'] = 0
                    print ''.join([df_header[i], ' was not found in the balance sheet for year ', str(y)])

        return comp_df


class DatabaseManipulationTCM(DatabaseManipulation):
    def __init__(self):
        name = 'Transaction Cost Model Database'
        file_csv = 'dbTCM_fileInfo.csv'
        DatabaseManipulation.__init__(self, name, file_csv)
