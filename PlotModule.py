#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 17:16:23 2017

@author: Emiel & Valerie

Documentation text to follow
"""

import pandas as ClassPd
import numpy as ClassNp
import matplotlib.pyplot as Plt
from matplotlib.widgets import Cursor
from matplotlib.widgets import MultiCursor

class ClassPlot:
    
    def __init__(self):
        self.log = {}
        self.fig = Plt.figure()
        self.subplot = []
        self.l_Color = ['b', 'g', 'r', 'c', 'm', 'y', 'k']
        self.vi_Color = 0
        

    def f_Plot(self, *args, **kwargs):
        """
            Description:        creates a plot
            Input:
                ~data~
                X_column        in case of dataframe data, if an X-column is provided, use this to mention the name
                Y_columns       in case of dataframe data, use this to mention the names of the Y-columns
                cursor          if this is true, a cursor will be added to the plot
                second_Y_ax     data to place on the second y-axis (only the data for Y! not for X!)
                X_label         string to place on the x-axis
                Y_label         string to place on the y-axis
                Y_label2        string to place on the second y-axis
                legend          list of strings for legend
            Output:
                fig             link to the figure that has been plotted 
                log             few logged things
        """
        # Note: args is data that needs to be plotted, while kwargs are parameters

        # Adjust the input data to make it more workable
        na_X, l_InData, vs_ArgType, dic_Kwargs = self._f_FixInput(args, kwargs)
        dic_Kwargs['location'] = 111
        
        # Plot the data     
        mainFig = self.fig.add_subplot(dic_Kwargs['location'])
        self._f_BasicPlot(mainFig, na_X, l_InData, dic_Kwargs['legend'])
        
        # Add the additional requests that work the same for normal and subplots
        self._f_GeneralKwargs(na_X, l_InData, dic_Kwargs)
    
        # Add the additional requests that are different for normal plots
        if 'cursor' in dic_Kwargs and dic_Kwargs['cursor'] is True: 
            ax = Plt.gca()
            cursor = Cursor(ax, useblit=True, color='red', linewidth=2)
            self.log['cursor'] = cursor
        
        Plt.show()
        
        return self.fig, self.log
    
    
    def f_SubPlot(self, location, *args, **kwargs):
        """
            Description:        creates a subplot
            Input:
                location        integer with 3 values (for example 212):
                                    - 1st value: total number of subplots (eventually) in Y direction
                                    - 2nd value: total number of subplots (eventually) in X direction
                                    - 3rd value: which subplot this is (1st, 2nd, etc..)
                other inputs    see description of f_Plot
            Output:
                fig             link to the figure that has been plotted
                subplot         link to the subplot that has been plotted
        """
        
        # Adjust the input data to make it more workable
        na_X, l_InData, vs_ArgType, dic_Kwargs = self._f_FixInput(args, kwargs)
        dic_Kwargs['location'] = location
        
        # Create a subplot
        self.subplot.append(self.fig.add_subplot(location))
        
        # Plot the data
        self._f_BasicPlot(self.subplot[-1], na_X, l_InData, dic_Kwargs['legend'])
        
        # Add the additional requests that work the same for normal and subplots
        self._f_GeneralKwargs(na_X, l_InData, dic_Kwargs)
        
        # Add the additional requests that are different for subplots
        if 'cursor' in kwargs and kwargs['cursor'] is True: 
            cursor = MultiCursor(self.fig.canvas, self.subplot, color='red', linewidth=1)
            self.log['cursor'] = cursor
        
        Plt.show()       
    
        return self.fig, self.subplot
    
    
    def _f_GeneralKwargs(self, na_X, l_InData, dic_Kwargs):
        """
            Description:        adds additional requests (such as labels)
            Input:
                na_X            data to be plotted on the X-axis
                l_InData        data to be plotted on the Y-axis
                dic_Kwargs      additional information required
            Output:             none
        """
        
        if 'X_label' in dic_Kwargs:
            Plt.xlabel(dic_Kwargs['X_label'])
            
        if 'Y_label' in dic_Kwargs:
            Plt.ylabel(dic_Kwargs['Y_label'])
        
        # Add data to a second axis
        if 'second_Y_ax' in dic_Kwargs and len(dic_Kwargs['second_Y_ax']) is not 0:
            if 'legend' in dic_Kwargs:
                Plt.legend(title="Legend")
            
            ax1 = self.fig.add_subplot(dic_Kwargs['location'])
            ax2 = ax1.twinx()
            self._f_BasicPlot(ax2, na_X, dic_Kwargs['second_Y_ax'], dic_Kwargs['second_legend'])
            
            if 'Y_label2' in dic_Kwargs:
                Plt.ylabel(dic_Kwargs['Y_label2'])
        
        if 'legend' in dic_Kwargs:
            Plt.legend(title="Legend")
            

    def _f_BasicPlot(self, fig, na_X, l_InData, labels):
        """
            Description:        makes a basic plot
            Input:
                fig             figure to add the plot to
                na_X            data for the X-axis
                l_InData        data for the Y-axis
                labels          label to associate with each plotted line
            Output:             none
        """
        
        for lab, na_Data in zip(labels, l_InData):
            if na_X is not "":
                fig.plot(na_X, na_Data, label=lab, color=self.l_Color[self.vi_Color])    
            else:
                fig.plot(na_Data, label=lab, color=self.l_Color[self.vi_Color])
            # Remember to use the next available color for the next plot on this figure
            self.vi_Color += 1
            if self.vi_Color >= len(self.l_Color):
                self.vi_Color = 0
    
#==============================================================================
# STATIC METHODS
#==============================================================================
    @staticmethod
    def _f_FixInput(args, kwargs):
        """
            Description:        makes the input data more workable
            Input:
                args            the "args" provided to the plot and subplot functions
                kwargs          the "kwargs" provided to the plot and subplot functions
            Output:
                na_X            numpy array of the data of the X-axis
                l_InData        list of numpy arrays of the data to plot (on the Y-axis)
                vs_ArgType      information on the original type of data provided:
                                     - df: dataframe
                                     - ps: pandas series
                                     - np: numpy array
                dic_Kwargs      improved kwargs data
        """
        
        # Initialize variables
        vs_ArgType = ""
        na_X = "" 
        dic_Kwargs = dict(kwargs)
        
        # Check if the type in args is consistent
        for arg in args:
            if vs_ArgType is "" and isinstance(arg, ClassPd.DataFrame):
                vs_ArgType = "df" 
            elif vs_ArgType is "" and isinstance(arg, ClassPd.Series):
                vs_ArgType = "ps" 
            elif vs_ArgType is "" and isinstance(arg, ClassNp.ndarray):
                vs_ArgType = "np"
            elif ((vs_ArgType is "df" and not isinstance(arg, ClassPd.DataFrame)) 
                or (vs_ArgType is "ps" and not isinstance(arg, ClassPd.Series))
                or (vs_ArgType is "np" and not isinstance(arg, ClassNp.ndarray))):
                raise TypeError("It is not possible to provide two types of input data (for example df and array). If this is required, contact class owner")
        
        # If the input data to plot is dataframe, this needs to be indicated in a kwarg 
        if vs_ArgType is "df" and "Y_columns" not in kwargs:
            raise ValueError("There should be a variable 'Y_columns' which indicated which columns of the dataframes should be plotted! And if so desired a 'X_column'.")
        
        l_InData = []
        # If the input data to plot is dataframe, the columns required should be present in each of the dataframes - and converted to pandas series
        if vs_ArgType is "df":
            if "X_column" in kwargs:
                na_X = args[0][kwargs['X_column']]
            for df_Tmp in args:
                for col in kwargs['Y_columns']:
                    l_InData.append(df_Tmp[col])
        else:
            # If the input data is a numpy array or a pandas series, the data can be plotted just like this
            if isinstance(args, ClassNp.ndarray) or isinstance(args, ClassPd.Series):
                l_InData = [args]
            elif len(args) > 1:
                na_X = args[0]
                l_InData = args[1:]
            else:
                l_InData = args    
                
        # Adjust the data for the second axis
        if ('second_Y_ax' in kwargs
            and (isinstance(kwargs['second_Y_ax'], ClassNp.ndarray)
            or isinstance(kwargs['second_Y_ax'], ClassPd.Series))):
            dic_Kwargs['second_Y_ax'] = [kwargs['second_Y_ax']]
        elif (vs_ArgType is 'df' and 'second_Y_ax' in kwargs
            and isinstance(kwargs['second_Y_ax'], ClassPd.DataFrame)):
            dic_Kwargs['second_Y_ax'] = []
            for col in kwargs['Y_columns']:
                dic_Kwargs['second_Y_ax'].append(kwargs['second_Y_ax'][col])
        elif (vs_ArgType is 'df' and 'second_Y_ax' in kwargs
            and isinstance(kwargs['second_Y_ax'], list)
            and isinstance(kwargs['second_Y_ax'][0], ClassPd.DataFrame)):
            dic_Kwargs['second_Y_ax'] = []
            for df_Tmp in kwargs['second_Y_ax']:
                    for col in kwargs['Y_columns']:
                        dic_Kwargs['second_Y_ax'].append(df_Tmp[col])
        
        # Adjust the information for the legend
        l_TmpLegend = []
        if vs_ArgType is 'df' and 'legend' in kwargs and isinstance(kwargs['legend'], str):
            for col in kwargs['Y_columns']:
                l_TmpLegend.append('_'.join([kwargs['legend'], col]))
        elif vs_ArgType is 'df' and 'legend' in kwargs and isinstance(kwargs['legend'], list):
            for vs_Leg in kwargs['legend']:
                for col in kwargs['Y_columns']:
                    l_TmpLegend.append('_'.join([vs_Leg, col]))
        elif 'legend' in kwargs and isinstance(kwargs['legend'], list):
            l_TmpLegend = kwargs['legend']
        elif 'legend' in kwargs and isinstance(kwargs['legend'], str):
            l_TmpLegend = [kwargs['legend']]
        
        dic_Kwargs['legend'] = []
        for vi_Ind, na_Data in enumerate(l_InData):
            if len(l_TmpLegend) > vi_Ind:
                dic_Kwargs['legend'].append(l_TmpLegend[vi_Ind])
            else:
                dic_Kwargs['legend'].append("")
        if 'second_Y_ax' in kwargs:
            dic_Kwargs['second_legend'] = []
            for vi_Ind2, na_Data in enumerate(dic_Kwargs['second_Y_ax']):
                if len(l_TmpLegend) > vi_Ind + vi_Ind2 + 1:
                    dic_Kwargs['second_legend'].append(l_TmpLegend[vi_Ind + vi_Ind2 + 1])
                else:
                    dic_Kwargs['second_legend'].append("")
    
    
        return na_X, l_InData, vs_ArgType, dic_Kwargs
        
        
        
        
        
        
        










    
    #==============================================================================
    # import matplotlib.pyplot as plt
    # import matplotlib.finance as fnc
    # import matplotlib.ticker as ticker
    # 
    # def plotStock(self, whichPrice):
    #     
    #     # choose between open/cloe/high/low and plot datetime object and values. DIT KAN CHIQUER
    #     if whichPrice == 'CandleStick':
    #         plot, ax = plt.subplots()
    #         fnc.candlestick2_ochl(ax,self.StockData['open_price'] ,self.StockData['high_price'] ,self.StockData['low_price'] ,self.StockData['close_price'] , width=0.5, colorup='k', colordown='r', alpha=0.75)
    #         
    #         ax.xaxis.set_major_locator(ticker.MaxNLocator(15))
    #         
    #         def mydate(x,pos):
    #             try:
    #                 return self.StockData['DateTime'][int(x)]
    #             except IndexError:
    #                 return ''
    #         
    #         ax.xaxis.set_major_formatter(ticker.FuncFormatter(mydate))
    #         
    #         plot.autofmt_xdate()
    #         plot.tight_layout()
    #         
    # 
    # def PlotIndicator(self,dic_Indicator,**kwargs):
    #     # initiate
    #     argumentName=[]
    #     argumentValue=[]
    # 
    #     # Read **kwargs
    #     # loop through **kwargs
    #     for key, value in kwargs.iteritems():
    #         argumentName.append(key)
    #         argumentValue.append(value)
    #     
    #     ### len(self.result) of len(self.result[0])
    #     ### iets verzinnen dat ook 2 of 3 lijnen in 1 keer geplot kunnen worden omdat BBANDS meer dan 1 resultaat
    #         
    #     # plot
    #     plot = plt.plot(dic_Indicator['dt_object'],dic_Indicator['Result'])
    #     
    #     # set label
    #     if 'label' in argumentName:
    #         print str(argumentName.index('label'))
    #         plt.setp(plot,label=argumentValue[argumentName.index('label')])
    #     else:
    #         plt.setp(plot, label=dic_Indicator['StockName'] + ' ' + dic_Indicator['IndicatorName'] + ' ' + dic_Indicator['IndicatorOrder'] + ' ' + str(dic_Indicator['TimeValue']))
    #     
    #     plt.legend(loc="upper left", bbox_to_anchor=[0, 1], ncol=2, shadow=True, title="Legend", fancybox=True)
    # 
    # def plotTY(self,dic_DataIn):
    #     # plotting
    #     plt.plot(dic_DataIn['t'] ,dic_DataIn['y'], 'o', label=self.name + ' ' + dic_DataIn['BuySellCriteria'])
    #     plt.grid(True)
    #     plt.ylabel('Price')
    #     plt.xlabel('Time')
    #     plt.legend()
    # 
    # def PlotBuySell(self,dic_DataIn):
    #     for i in range(len(dic_DataIn['t'])):
    #         plt.axvline(dic_DataIn['t'][i], ymin=0, ymax = 1, linewidth=2, linestyle='dashed',color='k', label=dic_DataIn['Action'])
    #         if i == 0:
    #             plt.legend()# only one time creating legend item
    # 
    #==============================================================================