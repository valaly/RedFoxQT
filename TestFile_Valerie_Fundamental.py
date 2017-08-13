# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 18:09:05 2017

@author: Valerie
"""

import DataFrameManipulation as m_Dfm
import numpy as ClassNp
import pandas as ClassPd
from datetime import datetime as Dt
from datetime import timedelta as timedelta

vi_StartPoint = 0
vi_EndPoint = vi_StartPoint + 50

l_Terms = ['total current assets', 'total liabilities', 'shares outstanding (basic average)', 'eps (basic)']

l_FinalHeaders = ['source', 'item', 'date', 'period', 'value']

df_Rsl = m_Dfm.f_ReadCsv('Russell2000_Tickers', vs_Path="C:/Users/Valerie/OneDrive/RedFox/Software/")
l_RslTicker = df_Rsl['ticker'].values

vs_Path = "C:/Users/Valerie/OneDrive/RedFox/Software/SM_Database/Graham_Russell2000/"

vs_MaxDate =  "2017-08"
vi_Incomplete = 0                
for vi_Ticker, vs_Ticker in enumerate(l_RslTicker[vi_StartPoint:vi_EndPoint]):
    # Read the csv
    df_Tmp = m_Dfm.f_ReadCsv(vs_Ticker, vs_Path, vs_Prefix="graham_")
    
    # Determine the date closest to now
    dt_MaxDate = Dt.strptime(vs_MaxDate, "%Y-%m")
    dt_MinDate = dt_MaxDate - timedelta(days=3*25)
    vs_MinDate = Dt.strftime(dt_MinDate, "%Y-%m")
    df_Tmp2 = df_Tmp.loc[df_Tmp['date']>= vs_MinDate]
    
    # Check if all necessary values are present. If not, list as incomplete (999)
    for vs_Term in l_Terms:
        if vs_Term not in df_Tmp2['item'].values:
            print "[", vi_Ticker, vs_Ticker, "] Item ", vs_Term, " could not be found! Incomplete! Sad."
            vi_Incomplete += 1
            break