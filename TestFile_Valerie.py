# -*- coding: utf-8 -*-
"""
Created on Fri Jul 21 18:54:04 2017

@author: Valerie
"""

import DataFrameManipulation as m_Dfm

vs_Path = 'C:/Users/Valerie/OneDrive/RedFox/Software/SM_Database/daily_price/'
vs_Prefix = 'daily_price_'

vs_Name = 'IWM'

df_IWM = m_Dfm.f_ReadCsv(vs_Name, vs_Path, vs_Prefix)