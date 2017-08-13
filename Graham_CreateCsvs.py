# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 18:09:05 2017

@author: Valerie
"""

import DataFrameManipulation as m_Dfm
import numpy as ClassNp
import pandas as ClassPd

vi_StartPoint = 10
vi_EndPoint = vi_StartPoint + 40

# Read income statement data
vs_Terms = "C:/Users/Valerie/OneDrive/RedFox/Software/NCAV_NNWC_Terms"

l_FinalHeaders = ['source', 'item', 'date', 'period', 'value']
l_FinalReportType = ['income_statement', 'cashflow', 'balance_sheet']

df_Rsl = m_Dfm.f_ReadCsv('Russell2000_Tickers', vs_Path="C:/Users/Valerie/OneDrive/RedFox/Software/")
l_RslTicker = df_Rsl['ticker'].values
vs_Path = "C:/Users/Valerie/OneDrive/RedFox/Software/MorningStar_Russell2000/"

l_ReportType = ["is", "bs", "cf"]  #is = Income Statement, cf = Cash Flow, bs = Balance Sheet
l_Period = [12, 3]  #12 for annual, 3 for quarterly
vs_Order = "asc" # or desc
vi_ColumnYear = 10   # or 5 (years)
vi_Number = 2       # units of the response data: 1 = None, 2 = Thousands, 3 = Milions, 4 = Bilions

vs_ReportTerms = vs_Terms
l_RT = ['group', 'item', 'name']
df_RT = m_Dfm.f_ReadCsv(vs_ReportTerms, l_Header=l_RT, vs_Delim=";")
df_RT['group'] = df_RT['group'].str.strip()
df_RT['item'] = df_RT['item'].str.strip()
df_RT['name'] = df_RT['name'].str.strip()
for vs_Ticker in l_RslTicker[vi_StartPoint:vi_EndPoint]:
    l_Data = []
    for vs_ReportType in l_ReportType[:-1]:        
        for vi_Period in l_Period:
            vs_Name = '_'.join([vs_ReportType, vs_Ticker, str(vi_Period), str(vi_ColumnYear), str(vi_Number)])

            # Read the csv to determine the header
            df_Tmp = m_Dfm.f_ReadCsv(vs_Name, vs_Path)
            l_Header = ['Item_name']
            l_Header.extend(df_Tmp.index[0][1:])
            
            # Read the csv again, with the correct header this time
            df_Tmp2 = m_Dfm.f_ReadCsv(vs_Name, vs_Path=vs_Path, l_Header=l_Header)
        
            # Fix the ticker dataframe
            df_Tmp2 = df_Tmp2.drop([0, 1])
            df_Tmp2.index = range(0, len(df_Tmp2['Item_name']))
            df_Tmp2.loc[:, 'item'] = ''
                           
            # Determine which item & category each line belongs to 
            vs_Header = '' 
            for vi_Ind, vs_Find in enumerate(df_Tmp2[l_Header[0]]):
                vs_Item = df_RT.loc[df_RT['name'] == vs_Find.lower(), 'item'].values
                    
                if ClassNp.sum(df_Tmp2.loc[vi_Ind, l_Header[1:]].isnull()) == len(l_Header[1:]):
                    vs_Header = vs_Find
                    
                if len(vs_Item) == 0:
                    vs_NewFind = ''.join([vs_Header, "@", vs_Find])
                    vs_Item = df_RT.loc[df_RT['name'] == vs_NewFind.lower(), 'item'].values
            
                # If the category and item are found, add them to the dataframe
                if len(vs_Item) == 1:
                    df_Tmp2.loc[vi_Ind, 'item'] = vs_Item[0]
                    for vs_Date in l_Header[1:]:
                        vd_Value = df_Tmp2.loc[vi_Ind, vs_Date]
                        vs_Period = 'quarterly' if vi_Period == 3 else 'annually'
                        l_Data.append(dict(zip(l_FinalHeaders, [vs_ReportType, vs_Item[0], vs_Date, vs_Period, vd_Value]))) 


            # Check if all the necessary values have been found!
            for vs_ItemName in df_RT['item'].loc[df_RT['group']==vs_ReportType].values:
                if vs_ItemName <> "total inventories" and vs_ItemName not in df_Tmp2['item'].values:
                    print "[", vs_Ticker, vi_Period, "] Could not find item: ", vs_ItemName

            
        # Fix the index
        df_Tmp2 = df_Tmp2.dropna(axis=0, subset=l_Header[1:], how='all')
        df_Tmp2.index = range(0, len(df_Tmp2['Item_name']))

    df_Final = ClassPd.DataFrame(l_Data)
    vs_FinalName = '_'.join(['graham', vs_Ticker])
    vs_FinalPath = "C:/Users/Valerie/OneDrive/RedFox/Software/SM_Database/Graham_Russell2000/"
    m_Dfm.f_SaveDFtoCsv(df_Final, vs_FinalName, vs_FinalPath)