from strategy3 import RotationalETF
from strategy4 import Graham1
from presenter import Presenter
from performance_measures import PerformanceMeasures
import datetime as dt
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import df_manipulation as dfm


class Backtesting(object):

    def __init__(self, context, data, plot=False, plot_title='Backtesting.pptx', plot_data=None):
        """ Initializes Backtesting class

        :param context: dictionary filled with vital information for backtesting and running the strategy algorithm
        :param data: list of the dataframes of the various securities needed for performance measurements
        :param plot: boolean for whether to plot or not. Default is False
        :param plot_title: string title to save plot presentation as. Default is 'Backtesting.pptx'
        :param plot_data: dictionary with additional information to use for plotting
        :return: N.A.
        """

        self.context = context
        self.plot = plot
        if self.context['start_date'] is None:
            self.context['start_date'] = 'default'
        if self.context['end_date'] is None:
            self.context['end_date'] = 'default'

        # self.perf_data is one big dataframe of all dataframes in data, cut to provided start and end date
        # Will be used to determine performance (returns) of strategy
        # self.test_data is also one big dataframe, but cut only to provided end date
        # Will be used to determine orders from strategy
        self.perf_data = [None] * len(data)
        self.test_data = [None] * len(data)
        for i, df in enumerate(data):
            self.perf_data[i] = dfm.cut_dates(df, self.context['start_date'], self.context['end_date'])
            self.test_data[i] = dfm.cut_dates(df, 'default', self.context['end_date'])

        self.perf_df = dfm.merge_dfs(self.perf_data)
        self.test_df = dfm.merge_dfs(self.test_data)

        if self.plot:
            self.plot_data = plot_data
            self.presname = plot_title
            self.pres = Presenter(new_pres=self.presname, title='Backtesting')
            if self.plot_data['benchmark'] is not None:
                self.plot_data['benchmark'] = dfm.cut_dates(plot_data['benchmark'],
                                                            self.context['start_date'], self.context['end_date'])

    def basic_checks(self):
        """ Performs basic checks

        :return: relative returns per year
        """

        # !! Note to self: Use close prices --> this isn't very general yet....
        # test data is only the price data needed for computing the order
        test_price_type = 'close_price'
        column_names = ['price_date'] + [x for x in self.test_df.columns.values if x.startswith(test_price_type)]
        test_data = self.test_df.loc[:, column_names]

        for i, name in enumerate(column_names[1:]):
            test_data.rename(columns={name: ''.join(['price_', str(i + 1)])}, inplace=True)

        # !! Note to self: Use adjusted close price --> also not general yet...
        # perf data is the price data needed for calculating the performance (returns)
        perf_price_type = 'adj_close_price'
        column_names = ['price_date'] + [x for x in self.test_df.columns.values if x.startswith(perf_price_type)]
        perf_data = self.perf_df.loc[:, column_names]

        for i, name in enumerate(column_names[1:]):
            perf_data.rename(columns={name: ''.join(['price_', str(i + 1)])}, inplace=True)

        # Run strategy
        order, log = self._employ_strategy(test_data)

        # Use orders to get returns (ret is return per order, returns is total return)
        returns_rel, returns_abs, ret_abs = self._calc_return(order, perf_data)

        # Initiate PerformanceMeasures class
        date = self.perf_df['price_date'].values
        pm = PerformanceMeasures(date, returns_rel)

        # Get return per year
        return_py = pm.returns_py
        years = pm.years

        # Get compounded annualized growth rate
        cagr = pm.calc_cagr()

        # Get volatility
        vol_scl, vol_vec = pm.calc_annual_volatility()

        # Get worst & best month
        return_pm = pm.returns_pm
        months = pm.months
        best_month, worst_month = pm.calc_best_worst_month()

        # Get Sharpe ratio
        sharpe_monthly = pm.calc_sharpe_ratio(self.context['risk_free_rate'])

        # Get maximum drawdown & maximum drawdown duration
        max_drawdown, peak_valley = pm.calc_drawdowns()

        if self.plot:
            if self.plot_data is None:
                names = np.array2string(np.arange(1, len(self.perf_data) + 1))
            else:
                names = self.plot_data['names']

            text = ''.join([''.join([str(y), ':   ', str(a), '\n']) for y, a in zip(years, return_py)])

            self.pres.add_text_slide(text, title='Return per year')

            pd_date = pd.to_datetime(date)
            plt_title = ''.join(['Initial amount: ', str(self.context['max_notional'])])

            # Plot of the returns
            self.pres.add_graph_slide(x=pd.to_datetime(date), y=returns_rel, graph_type='plot',
                                 ylabel='Return [-]', slide_title='Relative Returns')

            # Parameters that can be plotted against pd_date
            abs_ret_with_strategy = returns_abs + self.context['max_notional']
            if self.plot_data['benchmark'] is not None:
                abs_ret_with_benchmark = self.plot_data['benchmark']['adj_close_price'].values \
                                * self.context['max_notional'] / self.plot_data['benchmark']['adj_close_price'].iloc[0]
            abs_ret_with_strategy_stock_specific = ret_abs + self.context['max_notional']
            adj_price_names = [''.join(['adj_close_price_', str(ind_sec + 1)])
                              for ind_sec, ret_sec in enumerate(ret_abs.T)]
            adj_price_val_temp = self.perf_df[adj_price_names]
            #abs_ret_with_specific_stock =

            ### DIT STUK MOET GEWOON KUNNEN ZONDER FOR LOOP, BIJVOORBEELD DOOR DF OF MATRIX?
            #for ind_sec, ret_sec in enumerate(ret_abs.T):
            #    abs_ret_with_strategy_stock_specific = ret_sec + self.context['max_notional']
            #    adj_price_val = self.perf_df[''.join(['adj_close_price_', str(ind_sec + 1)])]
            #    abs_ret_with_specific_stock = adj_price_val.values * self.context['max_notional'] / adj_price_val[0]

            # Plot strategy returns versus benchmark returns
            if self.plot_data['benchmark'] is not None:
                self.pres.add_graph_slide(graph_type='plot', x=pd_date, y=[returns_abs + self.context['max_notional'],
                                                self.plot_data['benchmark']['adj_close_price'].values
                                                * self.context['max_notional']
                                                / self.plot_data['benchmark']['adj_close_price'].iloc[0]],
                                     labels=['Strategy Returns', 'Benchmark Returns'],
                                     ylabel='Absolute Returns & Adjusted Close Prices',
                                     slide_title='Strategy vs. Benchmark', plot_title=plt_title)

            for ind_sec, ret_sec in enumerate(ret_abs.T):
                # Plot of breakdown of returns
                self.pres.add_graph_slide(graph_type='plot', x=pd_date, y=[ret_sec + self.context['max_notional'],
                                                                           returns_abs + self.context['max_notional']],
                           labels=[''.join(['Returns ', names[ind_sec]]), 'Total Returns'],
                           ylabel='Absolute Returns [monetary unit]', slide_title='Absolute Returns',
                           plot_title=plt_title)

            for ind_sec, ret_sec in enumerate(ret_abs.T):
                # Plot of the returns and securities adjusted close price
                adj_price_val = self.perf_df[''.join(['adj_close_price_', str(ind_sec + 1)])]
                self.pres.add_graph_slide(graph_type='plot', x=pd_date,
                                          y=[adj_price_val.values * self.context['max_notional'] / adj_price_val[0],
                           returns_abs + self.context['max_notional']],
                           labels=[''.join(['Adj Close ', names[ind_sec]]), 'Strategy Returns'],
                           ylabel='Absolute Returns and Adjusted Close Prices',
                           slide_title='Abs. Returns & Adj. Close Prices', plot_title=plt_title)

            if self.plot_data['benchmark'] is not None:
                for ind_sec, ret_sec in enumerate(ret_abs.T):
                    # Plot benchmark adjusted close price to securities adjusted close price
                    adj_price_val = self.perf_df[''.join(['adj_close_price_', str(ind_sec + 1)])]
                    self.pres.add_graph_slide(graph_type='plot', x=pd_date,
                                              y=[adj_price_val.values * self.context['max_notional'] / adj_price_val[0],
                                         self.plot_data['benchmark']['adj_close_price'].values
                                         * self.context['max_notional']
                                         / self.plot_data['benchmark']['adj_close_price'].iloc[0]],
                               labels=[''.join(['Adj Close ', names[ind_sec]]), 'Benchmark Returns'],
                               ylabel='Adjusted Close Prices',
                               slide_title='Securities vs. Benchmark', plot_title=plt_title)
            self.pres.save_presentation(self.presname)

        return returns_abs

    def _employ_strategy(self, test_df):
        """ Executes the strategy

        :param test_df:
        :return:
        """

        # Initialize order and log arrays
        order = np.zeros(shape=(np.shape(self.perf_df)[0], len(self.perf_data)))
        log = [None] * np.shape(self.perf_df)[0]

        date_pd = pd.to_datetime(test_df['price_date'].values).date
        start_point = dfm.find_nearest_date(date_pd,
                                            dt.datetime.strptime(self.perf_df['price_date'][0], '%Y-%m-%d').date(),
                                            'daily')[0]
        date_pd = date_pd[start_point:]

        # Create date array to execute strategy on - one for weekly, one for monthly, depending on context
        dm = dfm.get_date_range(self.perf_df['price_date'].values[0], self.perf_df['price_date'].values[-1],
                                'monthly', self.context['start_day'], last_point_now=False)
        dw = dfm.get_date_range(self.perf_df['price_date'].values[0], self.perf_df['price_date'].values[-1],
                                'weekly', 1, last_point_now=False)

        # Use cw & cm to combine the dates to check on. If there is a date both as 'monthly' and 'weekly', pick 'monthly'
        # The order of concatenation and np.unique is important for this to go correct
        # !! Note to self: this is very specific to Strategy 3!!
        dm_n = dfm.find_nearest_date(date_pd, dm, 'monthly')[0]
        cm = np.ones(np.shape(dm_n))
        dw_n = dfm.find_nearest_date(date_pd, dw, 'weekly')[0]
        cw = np.zeros(np.shape(dw_n))

        dr_c = np.concatenate([dm_n, dw_n])
        cr_c = np.concatenate([cm, cw])

        dr, ind_u = np.unique(dr_c, return_index=True)
        cr = cr_c[ind_u]

        dr_ind = 0
        ind = 0

        while (ind < len(date_pd)) & (dr_ind < len(dr)):
            if (self.context['period'].lower() != 'daily'):
                ind = dr[dr_ind]
                self.context['check'] = 'monthly' if cr[dr_ind] == 1 else 'weekly'
                dr_ind += 1
            elif self.context['period'].lower() == 'daily':
                ind += 1

            a = RotationalETF(test_df.loc[:(ind + start_point), :], self.context, backtest=True)
            order[ind, :], log[ind] = a.calc_results()

            self.context['positions'] += order[ind, :]
            if sum(order[ind, :]) != 0:
                self.context['last_order'] = test_df.loc[ind + start_point, 'price_date']

            print ind, len(date_pd), self.context['check'], date_pd[ind]

        return order, log

    '''
    # Employ strategy used for strategy2
    def _employ_strategy(self, test_df, perf_df):
        order = np.zeros(shape=(np.shape(self.perf_df)[0], len(self.perf_data)))
        log = [None] * np.shape(self.perf_df)[0]

        dr = dfm.get_date_range(self.perf_df['price_date'].values[0], self.perf_df['price_date'].values[-1],
                                self.context['period'], self.context['start_day'])

        date_pd = pd.to_datetime(test_df['price_date'].values).date
        start_point = dfm.find_nearest_date(date_pd,
                                            dt.datetime.strptime(self.perf_df['price_date'][0], '%Y-%m-%d').date(),
                                            'daily')[0]

        self.context['returns'] = None
        self.context['return_date'] = None
        self.context['return_prices'] = None

        date_pd = date_pd[start_point:]
        dr_ind = 0
        ind = 0

        while ind < (len(date_pd) - 1):
            if (self.context['period'].lower() != 'daily'):# & (date_pd[ind] != dr[dr_ind]):
                ind = dfm.find_nearest_date(date_pd, dr[dr_ind], self.context['period'])[0]
                dr_ind += 1
            elif self.context['period'].lower() == 'daily':
                ind += 1

            self.context['return_prices'] = perf_df.loc[:ind]
            self.context['check'] = 'monthly'
            a = RotationalETF(test_df.loc[:(ind + start_point), :], self.context, backtest=True)
            order[ind, :], log[ind] = a.calc_results()

            self.context['positions'] += order[ind, :]
            self.context['returns'] = self._calc_return(order[:(ind+1), :], perf_df.loc[:ind, :])[1]
            self.context['return_date'] = perf_df.loc[:ind, 'price_date']
            self.context['last_order'] = test_df.loc[ind + start_point, 'price_date']
            print ind, len(date_pd)
        return order, log
    '''

    def _calc_return(self, order_original, perf_df):
        """ Calculates the return based on an order array, and a price Dataframe

        :param order_original: array of orders
        :param perf_df: Dataframe with the prices necessary to compute the returns
        :return: the relative returns, absolute returns, and absolute returns per security
        """

        order = order_original.copy()
        no_sec = len(self.perf_data)
        price_names = np.array(['price_' + str(i) for i in xrange(1, no_sec + 1)])
        ret = np.zeros((np.shape(order)[0], no_sec))

        transaction_cost = 0

        # buy_list vs sell_list contains order bought vs sold that cannot be matched yet to determine the return
        # For example when something has been bought, but nothing or not enough has been sold yet, the residue will be
        # listed in these lists.
        buy_shares = np.zeros((np.shape(order)[0], no_sec))
        buy_price = np.zeros((np.shape(order)[0], no_sec))
        sell_shares = np.zeros((np.shape(order)[0], no_sec))
        sell_price = np.zeros((np.shape(order)[0], no_sec))

        # bl_first vs sl_first indicates which row in buy_list vs sell_list can be used to "match" bought/sold shares.
        # It automatically points to the oldest row with still outstanding shares. Initial value is -1
        # bl_last vs sl_last indicates which row in buy_list vs sell_list can be used to write outstanding shares to.
        bl_first = np.ones(no_sec).astype(int) * -1
        bl_last = np.zeros(no_sec).astype(int)
        sl_first = np.ones(no_sec).astype(int) * -1
        sl_last = np.zeros(no_sec).astype(int)

        for ind in range(0, np.shape(order)[0]):
            bl_first[(bl_first == -1) & (bl_last > 0)] = 0
            sl_first[(sl_first == -1) & (sl_last > 0)] = 0

            # Three situations, per type: buy, sell, nothing
            # If nothing, skip to next day
            # Only returns made on one day are determined, later they will be accumulated.

            # Situation A.A: Sell order & outstanding buys larger than sell order
            col_to_change = (order[ind, :] < 0) & (np.sum(buy_shares, 0) > -order[ind, :])
            if sum(col_to_change) != 0:
                share_cumsum = np.cumsum(buy_shares, 0)
                share_compl = (share_cumsum < -order[ind, :]) & col_to_change
                numb_shares = sum(buy_shares * share_compl, 0)[col_to_change]
                ret[ind, col_to_change] += numb_shares * perf_df.loc[ind, price_names[col_to_change]] \
                                           - sum(buy_shares * buy_price * share_compl, 0)[col_to_change]
                buy_shares[share_compl] = 0
                bl_first += sum(share_compl)
                order[col_to_change] += numb_shares

                ret[ind, col_to_change] += perf_df.loc[ind, price_names[col_to_change]] * -order[ind, col_to_change] * (1 - transaction_cost) \
                                           - buy_price[bl_first[col_to_change], col_to_change] \
                                             * -order[ind, col_to_change] * (1 + transaction_cost)
                buy_shares[bl_first[col_to_change], col_to_change] += order[ind, col_to_change]
                order[ind, col_to_change] = 0

            # Situation A.B: Sell order & outstanding buys smaller than or equal to sell order
            # --> just fill out all outstanding buys, and change order. This order will be added to sell list in A.C
            col_to_change = (order[ind, :] < 0) & (np.sum(buy_shares, 0) > 0) \
                            & (np.sum(buy_shares, 0) <= -order[ind, :])
            if sum(col_to_change) != 0:
                numb_shares = buy_shares[:, col_to_change]
                price_shares = buy_price[:, col_to_change]
                ret[ind, col_to_change] += np.sum(numb_shares, 0) * \
                                           perf_df.loc[ind, price_names[col_to_change]].values * (1 - transaction_cost) \
                                           - np.sum(numb_shares * price_shares, 0) * (1 + transaction_cost)
                order[ind, col_to_change] += np.sum(numb_shares, 0)
                buy_shares[:, col_to_change] = 0
                bl_first[col_to_change] = bl_last[col_to_change] - 1

            # Situation A.C: Sell order & no outstanding buys
            col_to_change = (order[ind, :] < 0) & (np.sum(buy_shares, 0) == 0)
            if sum(col_to_change) != 0:
                row_to_change = bl_last[col_to_change]
                sell_shares[row_to_change, col_to_change] = -order[ind, col_to_change]
                sell_price[row_to_change, col_to_change] = perf_df.loc[ind, price_names[col_to_change]]
                sl_last[col_to_change] += 1

            # Situation B.A: Buy order & outstanding sells larger than buy order
            col_to_change = (order[ind, :] > 0) & (np.sum(sell_shares, 0) > order[ind, :])
            if sum(col_to_change) != 0:
                share_cumsum = np.cumsum(sell_shares, 0)
                share_compl = (share_cumsum < order[ind, :]) & col_to_change
                numb_shares = sum(sell_shares * share_compl, 0)[col_to_change]
                ret[ind, col_to_change] += sum(sell_shares * sell_price * share_compl, 0)[col_to_change] * (1 - transaction_cost)\
                                           - numb_shares * perf_df.loc[ind, price_names[col_to_change]] * (1 + transaction_cost)
                sell_shares[share_compl] = 0
                sl_first += sum(share_compl)
                order[col_to_change] += -numb_shares

                ret[ind, col_to_change] += sell_price[sl_first[col_to_change], col_to_change] * order[ind, col_to_change] * (1 - transaction_cost)\
                                           - perf_df.loc[ind, price_names[col_to_change]] * order[ind, col_to_change] * (1 + transaction_cost)
                sell_shares[sl_first[col_to_change], col_to_change] += -order[ind, col_to_change]
                order[ind, col_to_change] = 0

            # Situation B.B: Buy order & outstanding sells smaller than buy order
            # --> just fill out all outstanding sells, and change order. This order will be added to buy list in B.C
            col_to_change = (order[ind, :] > 0) & \
                            (np.sum(sell_shares, 0) > 0) & (np.sum(sell_shares, 0) <= order[ind, :])
            if sum(col_to_change) != 0:
                numb_shares = sell_shares[:, col_to_change]
                price_shares = sell_price[:, col_to_change]
                ret[ind, col_to_change] += np.sum(numb_shares * price_shares, 0) * (1 - transaction_cost) \
                                           - np.sum(numb_shares, 0) * perf_df.loc[ind, price_names[col_to_change]] * (1 + transaction_cost)
                order[ind, col_to_change] += -np.sum(numb_shares, 0)
                sell_shares[:, col_to_change] = 0
                sl_first[col_to_change] = sl_last[col_to_change] - 1

            # Situation B.C: Buy order & no outstanding sells
            col_to_change = (order[ind, :] > 0) & (np.sum(sell_shares, 0) == 0)
            if sum(col_to_change) != 0:
                row_to_change = bl_last[col_to_change]
                buy_shares[row_to_change, col_to_change] = order[ind, col_to_change]
                buy_price[row_to_change, col_to_change] = perf_df.loc[ind, price_names[col_to_change]]
                bl_last[col_to_change] += 1

        ret_abs = np.array([sum(ret[:r]) for r in range(1, len(ret) + 1)])
        returns_abs = np.sum(ret_abs, 1)
        returns_rel = [i / self.context['max_notional'] + 1 for i in returns_abs]

        return returns_rel, returns_abs, ret_abs

    @staticmethod
    def _histogram(y, no_buckets=21, normed=True):
        # Create histogram based on input y
        # Divide into x equal sized buckets
        # Add percentage at the bottom
        hist, bins = np.histogram(y, bins=no_buckets)
        if normed:
            hist = hist.astype(float) / float(len(y))
        width = 0.7 * np.diff(bins)
        center = (bins[:-1] + bins[1:]) / 2
        plt.bar(center, hist, align='center', width=width)


class BacktestingFundamental(object):
    def __init__(self, context, plot=False, plot_title='Backtesting.pptx'):
        self.context = context
        self.plot = plot

        if self.plot:
            pres = Presenter()
            pres.start_presentation(title='Backtesting')
            self.presname = plot_title
            pres.save_presentation(self.presname)

        if self.context['strategy_type'] == 'index':
            self.index_strategy()

    def index_strategy(self):
        # Used to run the index strategy often enough to make another csv file with the calculated items in it,
        # so different strategies can be backtested or plotted very easily without having to run the strategy over
        # and over again.

        # Check for csv
        csv_name = ''.join(['backtesting_', self.context['index'], '.csv'])
        if os.path.isfile(csv_name):
            # Read csv
            df_index = pd.read_csv(csv_name)
            # Check if csv needs to be updated
            # Update csv if needed
        else:
            # Create csv
            st = Graham1(self.context, backtest=True)
            df_index = st.calc_results()
            df_index.to_csv(csv_name, index=False)

        # Use csv
        item_list = df_index.columns.values
        exclude = ['id', 'symbol_id', 'description', 'file_name', 'date', 'eom_price_1']
        price_name = 'eom_price_1'
        item_list = np.array([i for i in item_list if i not in exclude])
        # Number of years inbetween
        length_time = [1, 2, 3, 5]
        date_list = df_index['date'].unique()

        col_df = ['start_date', 'length_time', 'return', 'eom_price_1']
        col_df.extend(item_list)
        result_df = pd.DataFrame(index=np.arange(0, 500*25), columns=col_df.extend(item_list))

        num = 0
        for l_time in length_time:
            num_start_ltime = num
            print l_time
            for date in date_list:
                num_start_date = num
                date_dt = dt.datetime.strptime(date, '%Y-%m-%d')
                new_date = dt.date(date_dt.year + l_time, date_dt.month, date_dt.day).strftime('%Y-%m-%d')
                # Check if new date is in the list
                if new_date not in date_list:
                    continue

                od = df_index.loc[(df_index['date'] == date) & (df_index[price_name] != 0)]
                nd = df_index.loc[(df_index['date'] == new_date) & (df_index[price_name] != 0)]

                companies = list(set(od['symbol_id']).intersection(set(nd['symbol_id'])))

                od = od.loc[od['symbol_id'].isin(companies)]
                nd = nd.loc[nd['symbol_id'].isin(companies)]
                od.index = od['symbol_id']
                nd.index = nd['symbol_id']

                res = nd[price_name].divide(od[price_name])
                num += len(res.values)

                for item in item_list:
                    #print item, num_start_date, num, len(res), len(nd), len(companies)
                    result_df.loc[num_start_date:(num-1), item] = od[item].values
                result_df.loc[num_start_date:(num-1), 'return'] = res.values
                result_df.loc[num_start_date:(num-1), 'start_date'] = date
                result_df.loc[num_start_date:(num-1), 'eom_price_1'] = od[price_name].values
                result_df.loc[num_start_date:(num-1), 'symbol_id'] = od['symbol_id'].values
            result_df.loc[num_start_ltime:(num-1), 'length_time'] = l_time

        # Make plots
        limits = {'total_sales_1': [0, 1e12],
                  'ca_cl_1': [0, 10],
                  'earning_stability_1': [0, 20],
                  'dividend_stability_1': [0, 20],
                  'earning_growth_1': [-1, 1],
                  'pe_1': [0, 20],
                  'pe_2': [0, 50],
                  'pe_3': [0, 50],
                  'pe_4': [0, 1.1],
                  'pb_1': [0, 10],
                  'pb_2': [0, 10],
                  'pepb_1': [0, 100],
                  'ncavps_1': [-100, 50],
                  'nnwcps_1': [-100, 50],
                  'debt_to_equity_1': [-2, 10]}
        if self.plot:
            print 'PLOTTING'
            for item in item_list:
                pres_name = ''.join(['Backtesting_', item, '.pptx'])
                if os.path.isfile(pres_name):
                    continue
                pres = Presenter()
                pres.start_presentation(title=pres_name[:-5])
                pres.save_presentation(pres_name)
                print item
                for l_time in length_time:
                    print l_time
                    for date in date_list:
                        subselec = result_df.loc[(result_df['start_date'] == date) & (result_df['length_time'] == l_time) &
                                                 (result_df[item] >= limits[item][0]) &
                                                 (result_df[item] <= limits[item][1])]
                        if subselec.empty:
                            continue
                        self._plot(subselec['return'].values*100-100, subselec[item], y_label=item,
                                   plot_title=''.join([str(l_time), ' years']),
                                   title=''.join([item, ' ', date]), ylim=limits[item], xlim=[-100, 500],
                                   pres_name=pres_name)

        print 'Strategy', self.context['perform_strategy']
        for date in date_list:
            for l_time in length_time:
                gen_return = result_df.loc[(result_df['start_date'] == date) &
                                           (result_df['length_time'] == l_time), 'return']
                if gen_return.empty:
                    continue

                print date, l_time
                print 'Average return:', np.average(gen_return.values[~np.isnan(gen_return.values)])

                if self.context['perform_strategy'] == 'A':
                    strat_selec = result_df.loc[(result_df['start_date'] == date) &
                                                (result_df['length_time'] == l_time) &
                                                (result_df['ncavps_1'] > result_df['eom_price_1']), 'return']

                if self.context['perform_strategy'] == 'B':
                    strat_selec = result_df.loc[(result_df['start_date'] == date) &
                                                 (result_df['length_time'] == l_time) &
                                                 (result_df['debt_to_equity_1'] <= 0.5) &
                                                 (result_df['debt_to_equity_1'] > 0) &
                                                 (result_df['pe_2'] <= 10), 'return']

                if self.context['perform_strategy'] == 'E':
                    strat_selec = result_df.loc[(result_df['start_date'] == date) &
                                                (result_df['length_time'] == l_time) &
                                                (result_df['nnwcps_1'] > result_df['eom_price_1']), 'return']

                if self.context['perform_strategy'] == 'G':
                    strat_selec = result_df.loc[(result_df['start_date'] == date) &
                                                 (result_df['length_time'] == l_time) &
                                                 (result_df['total_sales_1'] >= 2e9) &
                                                 (result_df['debt_to_equity_1'] <= 1) &
                                                 (result_df['dividend_stability_1'] >= 10) &
                                                 (result_df['pe_2'] <= 20) & (result_df['pe_3'] <= 25), 'return']

                print 'Strategy', self.context['perform_strategy'], 'return:', \
                    np.average((strat_selec.values)[~np.isnan(strat_selec.values)])
                print 'Number of initial companies:', len(gen_return)
                print 'Number of companies passing:', len(strat_selec)


    def _plot(self, x, y, labels=None, x_label='Return [%]',
         y_label='-', title='Backtesting results',
         plot_title='', xlim=None, ylim=None, pres_name=None):

        if pres_name is None:
            pres_name = self.presname
        pres = Presenter(pres_name)
        fig = plt.figure()

        plt.scatter(x, y)
        if xlim is not None:
            plt.xlim(xlim)
        if ylim is not None:
            plt.ylim(ylim)
        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plot_title)
        plt.grid()
        img_path = 'temp.png'
        plt.savefig(img_path)
        plt.close(fig)

        pres.add_picture_slide(img_path, title=title)
        pres.save_presentation(pres_name)

        #os.remove(img_path)