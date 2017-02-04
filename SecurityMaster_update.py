from downloader import WebsiteData
from dbaccess import DatabaseManipulationSM
# from datachecker import DataCheck
import urllib2

#updateCsv = 'C:\Users\Valerie\Dropbox\IzLeuk\RedFox\Software\Python\RedFox_Project\SM_Database\database_update.csv'

# Access SecuritiesMaster directory
dbSM = DatabaseManipulationSM()
dbSM.load('database_update')
dbSM.load('symbol')
dbSM.load('exchange')

# If you want to just check a few symbols, enter the symbol id's here. Otherwise, set it to -1
# update_secs = [115, 116, 117, 121, 126, 130, 132, 133, 135, 137, 138, 139, 140, 141, 142, 143, 153, 156, 158]
#update_secs = [11, 54, 101, 105, 106, 107, 108, 109, 110]
update_secs = [11, 54, 101, 105, 106, 107, 108, 109, 110]

# 11 = EFA
#

remove_row = []
shorter_csv = []
check_sec = []

# For every point in the update database
for index, symbol in enumerate(dbSM.data['database_update']['content'].symbol_id):
    # If a specific few symbols need to be checked, and this is not one of them, continue
    if update_secs[0] != -1 and symbol not in update_secs:
        continue

    # Get all the information needed
    ticker = dbSM.data['symbol']['content'].ticker[symbol]
    all_csvs = dbSM.data['main']['content'].name
    vendor_id = dbSM.data['database_update']['content'].data_vendor_id[index]
    exchange_id = dbSM.data['symbol']['content'].exchange_id[symbol]
    country = dbSM.data['exchange']['content'].country[exchange_id]
    exch_abbrev = dbSM.data['exchange']['content'].abbrev[exchange_id]

    # Print information to keep track of which ticker is being handled
    print symbol, ticker

    # Get website
    API = dbSM.get_API_url(vendor_id, ticker)

    # Download CSV file
    tick_site = WebsiteData(API)
    try:
        dataframe = tick_site.get_csv_as_dataframe(API)
    except urllib2.HTTPError, e:
        if e.code == 404:
            print API
            print "".join(['The daily price data could not be downloaded for ', ticker, '. This security was hence '
                                                                                        'deleted from the database.'])
            remove_row.append(index)
            continue
        else:
            raise

    # If there is no csv yet for that ticker, download from the internet
    if all_csvs[all_csvs.str.endswith(''.join([ticker, '.csv']))].empty:
        # Add data to database
        dbSM.create_daily_price_csv(dataframe, vendor_id, symbol, ticker)

        # Start data checks
        #mov_avg_window = 20
        dbSM.load('main')
        dbSM.load(''.join(['daily_price_', ticker]))
        #dc = DataCheck(dbSM.data[''.join(['daily_price_', ticker])]['content'], ticker, country, exch_abbrev, symbol)
        #dc.compare_to_moving_average(mov_avg_window)
        #dc.compare_to_other_dataset()
        #dc.find_missing_data()

    # If so:
    else:
        # Update data in database
        temp = dbSM.update_daily_price_csv(dataframe, vendor_id, symbol, ticker)
        if temp == 1:
            shorter_csv.append(ticker)

        # This should be temporary, just to make sure that not all tickers are automatically checked
        # if ticker not in ['IWM', 'SPY', 'EFA', 'ICF', 'DBC', 'VWO', 'IAU', 'TLT', 'SHY']:
        #     continue

        # Perform data checks
        # dbSM.load(''.join(['daily_price_', ticker]))
        # dc = DataCheck(dbSM.data[''.join(['daily_price_', ticker])]['content'], ticker, country, exch_abbrev, symbol)
        # df_temp = dc.get_second_dataset()
        # df_temp.to_csv(''.join(['Data_Checks/', ticker, '_', str(symbol),
        #                        '_QUANDL_data.csv']), index=False)

        # if dc.unchecked_data is not None:
        #     df_od = dc.compare_to_other_dataset()
        #     ls_md = dc.find_missing_data()
        #     df_da = dc.compute_split_div_adj()

            # if (len(ls_md) == 0) and df_od.empty and df_da.empty:
            #     df = dc.adjust_daily_price(final=True)
            #     dbSM.save_csv(''.join(['daily_price_', ticker]), df)
            # else:
            #     print ''.join(['!!! DATA TO CHECK FOR => ', ticker, ' <= !!!'])
            #     check_sec.append(ticker)
        # else:
        #     print ''.join(['No unchecked data for ', ticker])

    # Delete that entry in dictionary (taking up lot of memory)
    del dbSM.data[''.join(['daily_price_', ticker])]
    del dataframe

# Start printing the summary
print '======================================================'
print '========               SUMMARY                ========'
print '======================================================'
print '==== Securities removed from database_update.csv  ===='

# Update the database_update file
if len(remove_row) == 0:
    print'None'
else:
    for row in remove_row:
        #dbSM.data['database_update']['content'] = dbSM.data['database_update']['content'].loc[
        #    dbSM.data['database_update']['content'].index != row]
        print dbSM.data['database_update']['content']['symbol_id'].iloc[row], ': ', dbSM.data['symbol']['content']['ticker'].iloc[dbSM.data['database_update']['content']['symbol_id'].iloc[row]]

    dbSM.data['database_update']['content'] = dbSM.data['database_update']['content'].drop(dbSM.data['database_update']['content'].index[remove_row])

    # Update the indices of the database_update
    dbSM.data['database_update']['content']['id'] = range(0, len(dbSM.data['database_update']['content']))
    dbSM.data['database_update']['content'].index = range(0, len(dbSM.data['database_update']['content']))

    # Save the new database_update
    dbSM.save_csv('database_update', dbSM.data['database_update']['content'])

print '====  Securities with a shorter csv than should   ===='
if len(shorter_csv) == 0:
    print 'None'
else:
    for csv in shorter_csv:
        print ticker, ': ', dbSM.data['symbol']['content']['ticker'].iloc[ticker]

print '====             Securities to check              ===='
if len(check_sec) == 0:
    print 'None'
else:
    for sec in shorter_csv:
        print ticker, ': ', dbSM.data['symbol']['content']['ticker'].iloc[ticker]

del dbSM
