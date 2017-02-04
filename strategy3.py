import numpy as np
import pandas as pd
import datetime as dt
import df_manipulation as dfm
from performance_measures import PerformanceMeasures


class RotationalETF(object):

    def __init__(self, data, context, backtest=False):
        self.data = data
        self.context = context

        if 'start_day' not in self.context:
            self.context['start_day'] = 1

        self.backtest = backtest

        # Data that needs to be used from here on out has this format:
        # Dataframe with 'price_date' and then 'price_1', 'price_2', 'price_3' etc

    def calc_results(self):
        # Check for drawdown
        drawdown = False
        if sum(self.context['positions']) != 0:
            positions = self.context['positions'].copy()
            price_names = np.array(['price_' + str(i) for i in xrange(1, len(positions) + 1)])
            dd_data = dfm.cut_dates(self.data, self.context['last_order'], 'default')
            pm = PerformanceMeasures()
            max_dr, pv = pm.calc_drawdowns(dd_data['price_date'].values, dd_data[price_names[positions != 0]].values)
            if dd_data[price_names[positions != 0]].iloc[-1, 0] / pv['Peak'].iloc[-1] < (1 - self.context['max_drawdown']):
                drawdown = True

        # Weekly check
        if self.context['check'] is 'weekly':
            order = -self.context['positions'] if drawdown is True else np.zeros(len(self.context['positions']))
            return order, None

        # Monthly check
        if self.context['check'] is 'monthly':
            scp = True if drawdown is True else False
            return self._determine_order(self.context['positions'], self.data, sell_current_position=scp)

    def _determine_order(self, positions, data, sell_current_position=False):
        # indic[0]  1-month price performance
        # indic[1]  3-month price performance
        # indic[2]  6-month price performance
        # indic[3]  6-month volatility
        # indic[4]  annualized volatility
        # indic[5]  volatility-compensated 1-month price performance
        # indic[6]  total score of ETF
        pm = PerformanceMeasures()

        indic = np.zeros(shape=(7, data.shape[1] - 1))

        for ind in range(1, data.shape[1]):
            return_pm, months = pm.calc_return_per_time_unit(data['price_date'].values,
                                                             data[''.join(['price_', str(ind)])].values,
                                                             time='monthly',
                                                             st_day=self.context['start_day'])

            indic[0, ind - 1] = np.log(return_pm[-1] + 1)
            indic[1, ind - 1] = sum(np.log(return_pm[-3:] + 1))
            indic[2, ind - 1] = sum(np.log(return_pm[-6:] + 1))
            indic[3, ind - 1] = np.std(np.log(return_pm[-6:] + 1))
            indic[4, ind - 1] = self._calc_annual_volatility(return_pm)[0]

        total_volatility = np.mean(indic[4, :])
        indic[5, :] = indic[0, :] * total_volatility / indic[4, :]
        indic[6, :] = sum((indic[[5, 1, 2, 3], :].T * self.context['weights']).T)

        # If the current position needs to be sold, give it a very large score
        indic[6, positions != 0] = -999 if sell_current_position is True else indic[6, positions != 0]

        rank = indic[6, :].argsort()

        # Determining the order to place
        # Find non-zero element, if there is one. If the index matches one in the last x in rank, leave it be.
        order = np.zeros(data.shape[1] - 1)

        if sum(positions) != 0:
            # If the current position is being held by an ETF in top x
            ind_range = np.arange(len(rank), 0, -1)

            rank_cur_pos = ind_range[positions[rank] != 0]
            if rank_cur_pos > self.context['top_out']:
                # Sell position
                order = -positions

                free_price = positions[positions != 0] * \
                             data[''.join(['price_', str(np.argmax(positions) + 1)])].values[-1]
                # Buy top first
                order[rank[-1]] = np.floor(free_price /
                                           data[''.join(['price_', str(rank[-1] + 1)])].values[-1])
        else:
            rank = indic[6, :].argsort()
            # Determine number of shares to buy based on close price
            order[rank[-1]] = np.floor(self.context['max_notional'] /
                                       data[''.join(['price_', str(rank[-1] + 1)])].values[-1])

        return order, indic

    @staticmethod
    def _calc_annual_volatility(return_pm):
        # First remove the NaN values
        return_pm = return_pm[~np.isnan(return_pm)]

        scl_ann_vol = np.std(np.log(return_pm + 1)) * np.sqrt(12)

        # Wil het nog vergelijken met het gemiddelde nemen van een annual volatility
        no_full_years = len(return_pm) / 12
        sum_ann_vol = 0
        for y in range(0, no_full_years):
            if y == 0:
                sum_ann_vol += np.std(np.log(return_pm[-12:])) * np.sqrt(12)
            else:
                sum_ann_vol += np.std(np.log(return_pm[-(y + 1) * 12: -y * 12])) * np.sqrt(12)
        avg_ann_vol = sum_ann_vol / no_full_years

        return scl_ann_vol, avg_ann_vol

    @staticmethod
    def _simple_return(ret_val, data, positions, price_names):
        # Determine the buy price, sell_price, and hence the simulated return
        if ret_val[-1] == ret_val[0]:
            buy_price = data.loc[data.index[0], price_names[positions != 0]].values[0]
        else:
            buy_price = data.loc[
                (np.insert(ret_val[:-1], 0, ret_val[0]) - ret_val) != 0,
                price_names[positions != 0]].values[-1, 0]
        sell_price = data.loc[:, price_names[positions != 0]].iloc[-1].values[0]

        new_return = (sell_price - buy_price) * positions[positions != 0]

        # Add new return to ret_val
        ret_val = np.append(ret_val, ret_val[-1] *
                            np.ones((len(data) - len(ret_val))))

        ret_val[-1] += new_return

        return ret_val