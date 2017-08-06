# DOWNLOADER MODULE
# Function:
#   Downloads information from internet
#
# Is called by:
#   - datachecker

from StringIO import StringIO
import pandas as pd
import urllib2
import datetime as dt
import os
import sys
import re

class WebsiteData(object):
    rawData = None

    def __init__(self, website=None):
        self.website = website

    # Collect raw data from website
    def get_raw_data(self, website=None):
        if website is None:
            website = self.website

        # Create a request
        req = urllib2.Request(website, headers={'User-Agent': 'Magic browser'})

        # Create a handle to read out later
        response = urllib2.urlopen(req)

        # Read content
        rawData = response.read()
        response.close()

        # Get the timestamp
        rawDataTimeStamp = str(dt.datetime.now())

        return rawData, rawDataTimeStamp

    def get_csv_file(self, location='', name='Temp', site_csvfile=None):
        """Downloads csv file from given website and saves it at given location under given name
        Input:
            site_csvfile    url with which to obtain the csv file
            location        path to save the csv file to. If no path is given (i.e., ''), it will be saved in
                                a 'Temp' folder in the project folder
            name            name to save the csv file as
        Output:
            csv_name        complete name (including path) of saved csv file
        """
        if site_csvfile is None:
            site_csvfile = self.website

        if not location:
            if not os.path.exists('Temp'):
                os.makedirs('Temp')
            location = 'Temp'

        if not name[-4:] == '.csv':
            name = ''.join([name, '.csv'])

        # Get complete name to save file to
        local_spreadsheet = ''.join([location, '/', name])

        # Retrieve the csv as a string
        response = urllib2.urlopen(site_csvfile)
        csv = response.read()

        # Save the string to a file
        csvstr = str(csv).strip("b'")
        lines = csvstr.split("\\n")
        f = open(local_spreadsheet, "w")
        for line in lines:
            f.write(line + "\n")
        f.close()

        return local_spreadsheet

    def get_csv_as_dataframe(self, site=None, names=None):
        if site is None:
            site = self.website

        # Retrieve the csv as a string
        response = urllib2.urlopen(site)

        site_str = response.read()
        df = pd.io.parsers.read_table(StringIO(site_str), sep=',', index_col=False, names=names, header=0)
        return df

    def get_quandl_data(self, ticker, exchange=None):
        
        try:
            site_str = 'https://www.quandl.com/api/v1/datasets/WIKI/TICKER.csv?auth_token=y5EKtU94W7v5KsXc9EvN'
            site_str = site_str.replace('TICKER', ticker)

            df = self.get_csv_as_dataframe(site=site_str)

        except urllib2.HTTPError:
            try:                   
                if exchange is None:
                    raise ValueError("No Stock Exchange given, needed for this source")
                    
                site_str = \
                    'https://www.quandl.com/api/v1/datasets/GOOG/EXCHANGE_TICKER.csv?auth_token=y5EKtU94W7v5KsXc9EvN'
                site_str = site_str.replace('TICKER', ticker)
                site_str = site_str.replace('EXCHANGE', exchange)

                df = self.get_csv_as_dataframe(site=site_str)

            except urllib2.HTTPError:
                print ''.join(['An error occurred trying to get the second dataset from Quandl for ',
                               ticker, ', ', exchange])
                sys.exit(1)

        data_length = len(df)
        df = df.iloc[::-1]
        df.index = range(0, data_length)

        return df

    def get_nasdaq_data(self, website=None):
        if website is None:
            website = self.website

        rd = self.get_raw_data(website)[0]

        first_selec = rd.split('Results for:')[1]

        rest_data = self.get_tagged_string(first_selec, '<tbody>', '</tbody>')[0]

        day, rest_data_2, waste = self.get_tagged_string(rest_data, '<tr>', '</tr>')

        nd = pd.DataFrame(index=range(0, len(day) - 1), columns=['date', 'open', 'high', 'low', 'close', 'volume'])

        for i, d in enumerate(day[1:]):
            item_day, rest_data_3, waste = self.get_tagged_string(d, '<td>', '</td>', strip_newline=True)

            nd.loc[i, 'date'] = ''.join([item_day[0][6:], '-', item_day[0][:2], '-', item_day[0][3:5]])
            nd.loc[i, 'open'] = item_day[1]
            nd.loc[i, 'high'] = item_day[2]
            nd.loc[i, 'low'] = item_day[3]
            nd.loc[i, 'close'] = item_day[4]
            nd.loc[i, 'volume'] = item_day[5].replace(',', '')

        nd['open'] = nd['open'].astype(float)
        nd['high'] = nd['high'].astype(float)
        nd['low'] = nd['low'].astype(float)
        nd['close'] = nd['close'].astype(float)
        nd['volume'] = nd['volume'].astype(float)

        return nd

    def get_sec_annual_financial(self, ticker, year):
        key_words = ['Total\s*current\s*assets', 'Total\s*current\s*liabilities', 'Total\s*assets',
                     'Total\s*liabilities']

        site_str = 'http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=TICKER&' \
                   'type=10-K&dateb=&owner=exclude&count=100'
        site = site_str.replace('TICKER', ticker)
        # First, get list with all the 10-K results
        rd1 = self.get_raw_data(site)[0]

        # Two options: get one specific date, or all past dates
        if year != 'all':
            year_tag = ''.join(['<td>', str(year), '-'])
            wc = False
        else:
            year_tag = '<td>(.+?-.+?-.+?)</td>'
            wc = True

        cut1 = self.get_tagged_string(rd1, '>10-K', year_tag, end_wildcard=wc)
        str1 = [cut1[0]] if type(cut1[0]) is str else cut1[0]

        sites = [None] * len(str1)
        for i, st1 in enumerate(str1):
            cut2 = self.get_tagged_string(st1, '<a href="', '" id=')
            str2 = [cut2[0]] if type(cut2[0]) is str else cut2[0]
            site2 = ''.join(['http://www.sec.gov/', str2[0]])
            rd2 = self.get_raw_data(site2)[0]

            cut3 = self.get_tagged_string(rd2, '"Document Format Files"')
            cut4 = self.get_tagged_string(cut3[1], '<a href="', '">')

            str4 = [cut4[0]] if type(cut4[0]) is str else cut4[0]
            docu_site = [None] * len(str4)
            ds_ind = 0
            for st4 in str4:
                site3 = ''.join(['http://www.sec.gov', st4])
                if site3[-4:] != '.htm':
                    continue

                rd3 = self.get_raw_data(site3)[0]

                correct_docu = True
                for word in key_words:
                    #if not word in rd3:
                    if not re.findall(word, rd3):
                        correct_docu = False
                        break
                if not correct_docu:
                    continue
                docu_site[ds_ind] = site3
                ds_ind += 1

            sites[i] = [s for s in docu_site if s is not None]
            if len(sites[i]) > 1:
                print "Multiple reports for one year!"
            # How to deal with multiple balance sheets per year? tags found in cut1[2]
            # For now we'll assume that there will be just one form per year

        year_list = [c for c, s in zip(cut1[2], sites) if s]
        site_list = [s[0] for s in sites if s]

        return site_list, year_list

    def get_yahoo_splitdiv(self, ticker, start_date, end_date):
        base = 'http://ichart.finance.yahoo.com/x?'

        start_year = dt.datetime.strptime(start_date, '%Y-%m-%d').year
        start_month = dt.datetime.strptime(start_date, '%Y-%m-%d').month - 1
        start_day = dt.datetime.strptime(start_date, '%Y-%m-%d').day

        end_year = dt.datetime.strptime(end_date, '%Y-%m-%d').year
        end_month = dt.datetime.strptime(end_date, '%Y-%m-%d').month
        end_day = dt.datetime.strptime(end_date, '%Y-%m-%d').day

        what = 'v'

        param = ''.join(['a=', str(start_month),
                         '&b=', str(start_day),
                         '&c=', str(start_year),
                         '&d=', str(end_month),
                         '&e=', str(end_day),
                         '&f=', str(end_year),
                         '&s=', ticker,
                         '&g=', what])

        site = ''.join([base, param])

        names = ['Type', 'Date', 'Rate']

        try:
            df = self.get_csv_as_dataframe(site=site, names=names)

            # Convert Date to a comparable form
            df.Date = df.Date.apply(lambda x: ''.join([str(x)[0:4], '-', str(x)[4:6], '-', str(x)[6:8]]))

            df = df[:-4]

        except pd.parser.CParserError:
            df = pd.DataFrame(columns=names)

            print ''.join(['No (new) dividend/split data was found for ', ticker])

        # Cut the last four rows (useless)

        return df

    @staticmethod
    def get_tagged_string(string, start_tag, end_tag=None, end_wildcard=False, strip_newline=False):
        """Returns string between tags from larger string
        Input:
            string      larger string
            start_tag    tag after which desired string starts
            end_tag      tag before which desired string ends
        Output:
            desired string
        """
        end_tag_orignal = end_tag

        start_split = string.split(start_tag)
        end_tag_list = None
        if end_tag is not None:
            if len(start_split) == 2:
                if end_wildcard:
                    m = re.search(end_tag_orignal, start_split[0])
                    if m:
                        end_tag = m.group(1)
                end_split = start_split[1].split(end_tag)
                end_tag_list = end_tag
            else:
                end_split = [None, None]
                end_split[0] = [None] * (len(start_split) - 1)
                end_split[1] = [None] * (len(start_split) - 1)
                end_tag_list = [None] * (len(start_split) - 1)
                for i, line in enumerate(start_split[1:]):
                    if end_wildcard:
                        m = re.search(end_tag_orignal, start_split[i + 1])
                        if m:
                            end_tag = m.group(1)
                    if end_tag in start_split[i + 1]:
                        tmp = start_split[i + 1].split(end_tag)
                        end_split[0][i] = tmp[0]
                        end_split[1][i] = tmp[1]
                        end_tag_list[i] = end_tag
                end_split[1] = [s1 for s0, s1 in zip(end_split[0], end_split[1]) if s0 is not None]
                end_tag_list = [st for s0, st in zip(end_split[0], end_tag_list) if s0 is not None]
                end_split[0] = [s0 for s0 in end_split[0] if s0 is not None]
                if (len(end_split[0]) == 1) & (len(end_split[1]) == 1):
                    end_split[0] = end_split[0][0]
                    end_split[1] = end_split[1][0]

            if strip_newline:
                end_split[0] = map(lambda s: s.lstrip().rstrip(), end_split[0])
                end_split[1] = map(lambda s: s.lstrip().rstrip(), end_split[1])
        else:
            end_split = start_split

        return end_split[0], end_split[1], end_tag_list
