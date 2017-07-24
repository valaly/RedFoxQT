# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 18:54:04 2017

@author: Valerie
"""

import DataFrameManipulation as m_Dfm
from PlotModule import ClassPlot as ClassPt


vs_Path = "C:\Users\Valerie\OneDrive\RedFox\Software/"

vs_Name = "AAON"

df_AAON = m_Dfm.f_ReadCsv(vs_Name, vs_Path)

#vs_Path = 'C:/Users/Valerie/OneDrive/RedFox/Software/SM_Database/daily_price/'
#vs_Prefix = 'daily_price_'

#vs_Name = 'IWM'
#df_IWM = m_Dfm.f_ReadCsv(vs_Name, vs_Path, vs_Prefix)

#vs_Name = 'DBC'
#df_DBC = m_Dfm.f_ReadCsv(vs_Name, vs_Path, vs_Prefix)

#==============================================================================
# dt_ClosestDate, vi_MinIndex = m_Dfm.f_FindNearestDate(df_IWM['date_time'], '2012-01-01')
# 
#vs_StartDate, vs_EndDate = m_Dfm.f_FindCommonDates([df_DBC, df_IWM])
# 
# vi_Months = m_Dfm.f_CountTimePeriod('2012-01-01', '2012-07-08', 'monthly')
# 
# na_Dates = m_Dfm.f_ListTimePeriod(df_DBC['date_time'], 'monthly')
# 
# test1 = m_Dfm.f_CutDates(df_DBC)
# test2 = m_Dfm.f_CutDates([df_DBC])
# test3 = m_Dfm.f_CutDates([df_DBC, df_IWM])
# 
# test4 = m_Dfm.f_CutDates(df_DBC, vs_StartDate, vs_EndDate)
# test5 = m_Dfm.f_CutDates([df_DBC], vs_StartDate, vs_EndDate)
#df_DBC, df_IWM = m_Dfm.f_CutDates([df_DBC, df_IWM], vs_StartDate, vs_EndDate)
#==============================================================================
#Plt.close("all")


# Plot 1
#a = ClassPt()
#a.f_Plot(df_DBC,
#         second_Y_ax=df_IWM,
#         X_column='date_time', Y_columns=['open_price', 'close_price'],
#         cursor=True,
#         legend=['DBC', 'IWM'])

# Plot 2
#a = ClassPt()
#a.f_SubPlot(211, df_DBC['date_time'], df_DBC['open_price'], df_DBC['close_price'], cursor=True)
#a.f_SubPlot(212, df_IWM['date_time'], df_IWM['open_price'], df_IWM['close_price'], cursor=True)
#
## Plot 3
#a = ClassPt()
#a.f_Plot(df_DBC['date_time'], df_DBC['open_price'], 
#        second_Y_ax=[df_IWM['close_price']], 
#        cursor=True, 
#        X_label='Date', Y_label='Value', Y_label2='Value2',
#        legend=['DBC_open', 'IWM_close'])
#
## Plot 4
#a = ClassPt()
#a.f_SubPlot(211, df_DBC['date_time'], df_DBC['open_price'], second_Y_ax=df_IWM['close_price'], cursor=True)
#a.f_SubPlot(212, df_IWM['date_time'], df_IWM['open_price'], df_IWM['close_price'], cursor=True)

# Plot 5
#a = ClassPt()
#a.f_SubPlot(211, df_DBC['date_time'], df_DBC['open_price'], 
#        second_Y_ax=df_IWM['close_price'], 
#        legend=['DBC_open', 'IWM_close'],
#        cursor=True)
#a.f_SubPlot(212, df_IWM['date_time'], df_IWM['open_price'], df_IWM['close_price'], 
#        cursor=True)