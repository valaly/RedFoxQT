# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 18:54:04 2017

@author: Valerie
"""

import DataFrameManipulation as m_Dfm
from datetime import datetime as dt

vs_Path = 'C:/Users/Valerie/OneDrive/RedFox/Software/SM_Database/daily_price/'
vs_Prefix = 'daily_price_'

vs_Name = 'IWM'
df_IWM = m_Dfm.f_ReadCsv(vs_Name, vs_Path, vs_Prefix)

vs_Name = 'DBC'
df_DBC = m_Dfm.f_ReadCsv(vs_Name, vs_Path, vs_Prefix)

dt_ClosestDate, vi_MinIndex = m_Dfm.f_FindNearestDate(df_IWM['date_time'], '2012-01-01')

vs_StartDate, vs_EndDate = m_Dfm.f_FindCommonDates([df_DBC, df_IWM])

vi_Months = m_Dfm.f_CountTimePeriod('2012-01-01', '2012-07-08', 'monthly')

<<<<<<< HEAD
na_Dates = m_Dfm.f_ListTimePeriod(df_DBC['date_time'], 'monthly')
=======
na_Dates = m_Dfm.f_ListTimePeriod(df_DBC['date_time'], 'monthly')

test1 = m_Dfm.f_CutDates(df_DBC)
test2 = m_Dfm.f_CutDates([df_DBC])
test3 = m_Dfm.f_CutDates([df_DBC, df_IWM])

test4 = m_Dfm.f_CutDates(df_DBC, vs_StartDate, vs_EndDate)
test5 = m_Dfm.f_CutDates([df_DBC], vs_StartDate, vs_EndDate)
test6 = m_Dfm.f_CutDates([df_DBC, df_IWM], vs_StartDate, vs_EndDate)
>>>>>>> Emiel_Branch
