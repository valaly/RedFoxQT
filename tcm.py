from dbaccess import DatabaseManipulationTCM
from presenter import Presenter
import numpy as np
import matplotlib.pyplot as plt
import os


class TransactionCostModel(object):
    def __init__(self, broker_id=None, sec_type=None, exchange_id=None, country=None,
                 sec_price=None, no_sec=None, plot=False, location=None):
        # #### MAIN INPUT ####
        self.name = 'Transaction Cost Model'
        self.dbTCM = DatabaseManipulationTCM()
        self.broker_id = broker_id
        self.sec_type = sec_type
        self.exchange_id = exchange_id
        self.country = country
        # Ensure that sec_price is a numpy array, and create one if not provided
        if not isinstance(sec_price, list) and sec_price is not None:
            sec_price = [sec_price]
        self.sec_price = np.arange(10, 500, 10) if sec_price is None else np.array(sec_price)
        # Ensure that no_sec is a numpy array, and create one if not provided
        if not isinstance(no_sec, list) and no_sec is not None:
            no_sec = [no_sec]
        self.no_sec = np.arange(10, 500, 10) if no_sec is None else np.array(no_sec)
        # Assign location, if not provided, it will be main file of project
        if location is None:
            self.location = ''
        else:
            self.location = ''.join([location, '/'])

        # #### PRESENTATION ####
        self.plot = plot
        self.presname = ''

        if self.plot:
            pres = Presenter()
            pres.start_presentation(title='Transaction Costs')
            text = ''.join(['broker id: ', str(self.broker_id), '\n security type: ', self.sec_type,
                            '\n exchange id: ', self.exchange_id, '\n country: ', self.country])
            pres.add_text_slide(text, title='Input')
            self.presname = ''.join([self.location, 'Transaction_Costs_', str(broker_id), '_',
                                     self.sec_type, '_', self.exchange_id, '_', self.country, '.pptx'])
            pres.save_presentation(self.presname)

    def comp_transaction_costs(self):
        slippage = self.comp_slippage()
        commissions = self.comp_commissions_fees()

        total = slippage + commissions

        return total

    def comp_slippage(self):
        # Assumption: slippage is 2 pip
        slip = 0.0002

        # If no_sec and sec_price are vectors, the calculation of transaction cost will be slightly different
        if len(self.sec_price) > 1 and len(self.no_sec) > 1:
            no_samp = 5
            # Sample 5 values of no_sec & sec_price
            ns_samp = self._cm_sample_arr(self.no_sec, no_samp)
            sp_samp = self._cm_sample_arr(self.sec_price, no_samp)

            # Get list of lists ns
            costs_ns = []
            for ind in range(0, no_samp):
                costs_ns.append(ns_samp[ind] * self.sec_price * slip)

            # Get list of lists sp
            costs_sp = []
            for ind in range(0, no_samp):
                costs_sp.append(self.no_sec * sp_samp[ind] * slip)

            costs = [costs_ns, costs_sp]
        else:
            costs = self.no_sec * self.sec_price * slip

        return costs

    def comp_commissions_fees(self):
        # Load data
        self.dbTCM.load('commissions_fees')
        df = self.dbTCM.data['commissions_fees']['content']

        # Find the correct lines to use
        df_line = df.loc[(df.broker_id == self.broker_id)
                         & (df.country == self.country)
                         & (df.sec_type == self.sec_type)
                         & ((df.exchange_id == 'ALL') | (df.exchange_id == self.exchange_id))]

        # If no_sec and sec_price are vectors, the calculation of transaction cost will be slightly different
        if len(self.sec_price) > 1 and len(self.no_sec) > 1:
            no_samp = 5
            # Sample 5 values of no_sec & sec_price
            ns_samp = self._cm_sample_arr(self.no_sec, no_samp)
            sp_samp = self._cm_sample_arr(self.sec_price, no_samp)

            # Get list of lists ns
            costs_ns = []
            for ind in range(0, no_samp):
                costs_ns.append(self._cm_get_costs(df_line, ns=np.array([ns_samp[ind]]), sp=self.sec_price))

            # Get list of lists sp
            costs_sp = []
            for ind in range(0, no_samp):
                costs_sp.append(self._cm_get_costs(df_line, ns=self.no_sec, sp=np.array([sp_samp[ind]])))

            costs = [costs_ns, costs_sp]

            if self.plot:
                self._cm_plot(self.no_sec, costs_sp, x_label='Number of Securities', title='Commissions and fees',
                              labels=['sec_price = ' + str(x) for x in sp_samp])
                self._cm_plot(self.sec_price, costs_ns, x_label='Security Price [monetary unit]', title='Commissions and fees',
                              labels=['no_sec = ' + str(x) for x in ns_samp])

        else:
            costs = self._cm_get_costs(df_line, ns=self.no_sec, sp=self.sec_price)

            if (len(self.sec_price) > 1) & self.plot:
                self._cm_plot(self.sec_price, costs, x_label='Security Price [monetary unit]',
                              plot_title=''.join(['no_sec = ', str(self.no_sec)]), title='Commissions and fees')
            elif (len(self.no_sec) > 1) & self.plot:
                self._cm_plot(self.no_sec, costs, x_label='Number of Securities',
                              plot_title = ''.join(['sec_price = ', str(self.sec_price)]), title='Commissions and fees')

        return costs

    def _cm_get_costs(self, df_lines, ns=None, sp=None):
        norm_cost = max_cost = min_cost = np.zeros(max(len(ns), len(sp)))

        for d in df_lines.id:
            ns_d = ns - df_lines.min_volume[d]
            ns_d[ns_d <= 0] = 0
            ns_d[ns_d > df_lines.max_volume[d]] = df_lines.max_volume[d]

            norm_cost += df_lines.const[d] + \
                         df_lines.rate[d] * (ns_d * (1 - df_lines.no_sec[d]) + df_lines.no_sec[d]) * \
                         (sp * (1 - df_lines.sec_price[d]) + df_lines.sec_price[d])

            min_cost = df_lines.min_const[d] + \
                       df_lines.min_rate[d] * (ns * (1 - df_lines.min_no_sec[d]) + df_lines.min_no_sec[d]) * \
                       (sp * (1 - df_lines.min_sec_price[d]) + df_lines.min_sec_price[d])

            max_cost = df_lines.max_const[d] + \
                       df_lines.max_rate[d] * (ns * (1 - df_lines.max_no_sec[d]) + df_lines.max_no_sec[d]) * \
                       (sp * (1 - df_lines.max_sec_price[d]) + df_lines.max_sec_price[d])

        real_max = np.maximum(min_cost, max_cost)
        costs = np.minimum(np.maximum(min_cost, norm_cost), real_max)

        return costs

    def _cm_get_ns_sp(self, df_value, self_value):
        if df_value == 0:
            return self_value
        elif isinstance(self_value, np.ndarray) | isinstance(self_value, list):
            return df_value * np.ones(len(self_value))
        else:
            return df_value

    def _cm_sample_arr(self, array, no_samp):
        return [array[int(len(array) / 4 * x)] for x in range(0, no_samp)]

    def _cm_plot(self, x, y, labels=None, x_label='Transaction Value [monetary unit]',
                 y_label='Transaction Costs [monetary unit]', title='Transaction costs',
                 plot_title=''):

        pres = Presenter(self.presname)
        fig = plt.figure()

        if isinstance(y[0], np.ndarray) | isinstance(y[0], list):
            for i in range(0, len(y)):
                plt.plot(x, y[i], label=labels[i])
            plt.legend(loc='upper left')
        else:
            plt.plot(x, y, 'b', label=labels)
            if labels is not None:
                plt.legend(loc='upper left')

        plt.xlabel(x_label)
        plt.ylabel(y_label)
        plt.title(plot_title)
        img_path = 'temp.png'
        plt.savefig(img_path)
        plt.close(fig)

        pres.add_picture_slide(img_path, title=title)
        pres.save_presentation(self.presname)

        os.remove(img_path)
