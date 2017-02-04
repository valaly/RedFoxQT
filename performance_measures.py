import df_manipulation as dfm
import pandas as pd
import numpy as np
import datetime as dt


class PerformanceMeasures(object):
    def __init__(self, date=None, returns=None, st_day=1):
        self.date = date
        self.returns = returns
        self.st_day = st_day

        if self.date is not None and self.returns is not None:
            self.returns_pm, self.months = self.calc_return_per_time_unit(self.date, self.returns,
                                                                          time='monthly', st_day=self.st_day)
            self.returns_py, self.years = self.calc_return_per_time_unit(self.date, self.returns,
                                                                         time='yearly', st_day=self.st_day)

    @staticmethod
    def calc_return_per_time_unit(date, returns, time='yearly', st_day=1):
        # Returns are calculated by last date of the month/year (e.g., 31/12 - 31/01)
        date_pd = pd.to_datetime(date).date
        tu = dfm.get_date_range(date[0], date[-1], time, st_day)
        first_val = returns[0]
        return_pt = np.zeros(len(tu))

        for ind, day in enumerate(tu):
            i = dfm.find_nearest_date(date_pd, day, time)[0]
            return_pt[ind] = (returns[i] / first_val) - 1
            first_val = returns[i]

        return return_pt, tu

    def calc_cagr(self, date=None, returns=None):
        # Set initial values
        if date is None:
            date = self.date
        if returns is None:
            returns = self.returns

        years = (dt.datetime.strptime(date[-1], '%Y-%m-%d') - dt.datetime.strptime(date[0], '%Y-%m-%d')).days / 365.25
        cagr = np.power(1 + (returns[-1] - returns[0]), (1 / years)) - 1

        return cagr

    def calc_annual_volatility(self, date=None, returns=None, st_day=None):
        # Set initial values
        if date is None:
            date = self.date
        if returns is None:
            returns = self.returns
        if not st_day:
            st_day = self.st_day
        return_pm = self.calc_return_per_time_unit(date, returns, time='monthly', st_day=st_day)[0] \
            if self.returns_pm is None else self.returns_pm

        # Vector values - daily
        vol = pd.rolling_std(pd.Series(np.log(returns)), 21, 0).values
        vol[0] = 0
        vec_ann_vol = vol * np.sqrt(252)

        # Scalar values
        scl_ann_vol = np.std(np.log(return_pm + 1)) * np.sqrt(12)

        return scl_ann_vol, vec_ann_vol

    def calc_best_worst_month(self, date=None, returns=None, st_day=None):
        # Set initial values
        if self.returns_pm is None:
            if date is None:
                date = self.date
            if returns is None:
                returns = self.returns
            if not st_day:
                st_day = self.st_day
            return_pm = self.calc_return_per_time_unit(date, returns, time='monthly', st_day=st_day)[0]
        else:
            return_pm = self.returns_pm

        return np.max(return_pm), np.min(return_pm)

    def calc_sharpe_ratio(self, risk_free_rate, date=None, returns=None, st_day=None):
                # Set initial values
        if self.returns_pm is None:
            if date is None:
                date = self.date
            if returns is None:
                returns = self.returns
            if not st_day:
                st_day = self.st_day
            return_pm = self.calc_return_per_time_unit(date, returns, time='monthly', st_day=st_day)[0]
        else:
            return_pm = self.returns_pm
        excess_returns = return_pm - risk_free_rate

        sharpe_monthly = np.mean(excess_returns) / np.std(excess_returns)

        return sharpe_monthly

    def calc_drawdowns(self, date=None, returns=None):
        # Set initial values
        if date is None:
            date = self.date
        if returns is None:
            returns = self.returns

        peak_valley = pd.DataFrame(index=np.arange(0, len(returns)),
                                   columns=['Peak', 'Peak_date', 'Subsequent_valley', 'Valley_date', 'Drawdown'])

        peak_valley['Peak'][0] = 0
        count = 1
        ind_st = 0
        for ind, (r, d) in enumerate(zip(returns, date)):
            # If the loop has reached the last entry in returns, determine the lowest point since
            # the last peak
            if ind == (len(returns) - 1):
                ind_d = np.where(returns[ind_st:(ind + 1)] == np.min(returns[ind_st:(ind + 1)]))[0][-1]
                peak_valley['Subsequent_valley'][count - 1] = returns[ind_st:(ind + 1)][ind_d]
                peak_valley['Valley_date'][count - 1] = date[ind_st:(ind + 1)][ind_d]
                continue

            # If the returns are larger than the previous peaks and the next return, add point as peak
            if (r >= peak_valley['Peak'][count - 1]) & (returns[ind + 1] < r):
                peak_valley['Peak'][count] = r
                peak_valley['Peak_date'][count] = d
                # If this is already the second peak, determine the drawdown
                if count > 1:
                    ind_d = np.where(returns[ind_st:(ind + 1)] == np.min(returns[ind_st:(ind + 1)]))[0][-1]
                    peak_valley['Subsequent_valley'][count - 1] = returns[ind_st:(ind + 1)][ind_d]
                    peak_valley['Valley_date'][count - 1] = date[ind_st:(ind + 1)][ind_d]
                ind_st = ind
                count += 1

        peak_valley['Drawdown'] = peak_valley['Peak'] - peak_valley['Subsequent_valley']

        peak_valley.dropna(axis=0, how='any', inplace=True)
        peak_valley.index = range(0, len(peak_valley))

        # Maximum drawdown
        if peak_valley.empty:
            peak_valley['Peak'] = returns[-1]
            peak_valley['Peak_date'] = date[-1]
            max_drawdown = 0
        else:
            max_drawdown = peak_valley.iloc[peak_valley['Drawdown'].argmax(), :]

        return max_drawdown, peak_valley
