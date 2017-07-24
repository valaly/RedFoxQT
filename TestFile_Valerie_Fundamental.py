# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 18:09:05 2017

@author: Valerie
"""

#from downloader import WebsiteData as ClassWd
import DataFrameManipulation as m_Dfm
import numpy as ClassNp
import pandas as ClassPd

# Read income statement data
vs_IS = "C:/Users/Valerie/OneDrive/RedFox/Software/IncomeStatementTerms"
l_IS = ['group', 'category', 'item', 'name']
df_IS = m_Dfm.f_ReadCsv(vs_IS, l_Header=l_IS, vs_Delim=";")
df_IS['group'] = df_IS['group'].str.strip()
df_IS['category'] = df_IS['category'].str.strip()
df_IS['item'] = df_IS['item'].str.strip()
df_IS['name'] = df_IS['name'].str.strip()




l_RslTicker = ["FLWS", "SRCE", "TWOU", "DDD", "EGHT", "AVHI", "ATEN", "AAC", "AAON", "AIR", "AAN", "ABAX", "ANF"]
vs_Path = "C:/Users/Valerie/OneDrive/RedFox/Software/MorningStar_Russel2000/"

l_ReportType = ["is", "cf", "bs"]  #is = Income Statement, cf = Cash Flow, bs = Balance Sheet
l_Period = [12, 3]  #12 for annual, 3 for quarterly
vs_Order = "asc" # or desc
vi_ColumnYear = 10   # or 5 (years)
vi_Number = 2       # units of the response data: 1 = None, 2 = Thousands, 3 = Milions, 4 = Bilions

#dwn = ClassWd()

l_Items = []
vs_ReportType = "is"
for vi_Period in l_Period:
    for vs_Ticker in l_RslTicker:
        vs_Name = '_'.join([vs_ReportType, vs_Ticker, str(vi_Period), str(vi_ColumnYear), str(vi_Number)])
#==============================================================================            
#               RETRIEVING DATA FROM MORNINGSTAR            
#==============================================================================
#             print vs_Name
#             
#             vs_API = ''.join(["http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=", vs_Ticker,
#                 "&reportType=", vs_ReportType, "&period=", str(vi_Period), "&dataType=A&order=", vs_Order, 
#                 "&columnYear=", str(vi_ColumnYear), "&number=", str(vi_Number)])
#             
#             dwn.get_csv_file(location=vs_Path, name=vs_Name, site_csvfile=vs_API)
#==============================================================================
        df_Tmp = m_Dfm.f_ReadCsv(vs_Name, vs_Path)
        l_Header = ['Item_name']
        l_Header.extend(df_Tmp.index[0][1:])
        
        df_Tmp2 = m_Dfm.f_ReadCsv(vs_Name, vs_Path=vs_Path, l_Header=l_Header)
        
        # Fix the ticker dataframe
        df_Tmp2 = df_Tmp2.drop([0, 1])
        df_Tmp2.index = range(0, len(df_Tmp2['Item_name']))
        df_Tmp2.loc[:, 'group'] = 'income_statement'
        df_Tmp2.loc[:, 'category'] = ''
        df_Tmp2.loc[:, 'item'] = ''
        
        vi_MaxRows = max(df_IS.loc[:, 'name'].map(lambda x: x.count("@")).values)
                   
        vs_Header = '' 
        for vi_Ind, vs_Find in enumerate(df_Tmp2[l_Header[0]]):    
            vs_Category = df_IS.loc[df_IS['name'] == vs_Find.lower(), 'category'].values
            vs_Item = df_IS.loc[df_IS['name'] == vs_Find.lower(), 'item'].values
                
            if ClassNp.sum(df_Tmp2.loc[vi_Ind, l_Header[1:]].isnull()) == len(l_Header[1:]):
                vs_Header = vs_Find
                
            if len(vs_Item) == 0:
                vs_NewFind = ''.join([vs_Header, "@", vs_Find])
                vs_Category = df_IS.loc[df_IS['name'] == vs_NewFind.lower(), 'category'].values
                vs_Item = df_IS.loc[df_IS['name'] == vs_NewFind.lower(), 'item'].values
        
            if len(vs_Item) == 0 and vs_Header <> vs_Find:    
                print "[", vs_Ticker, "] Could not find item for: ", vs_Find
            
            if len(vs_Category) > 1:
                print vs_Category, vs_Item, vs_Find, vs_NewFind
                raise ValueError("Multiple options for category!!")
            if len(vs_Category) == 1 and not ClassPd.isnull(vs_Category):
                  df_Tmp2.loc[vi_Ind, 'category'] = vs_Category[0]
            if len(vs_Item) == 1 and not ClassPd.isnull(vs_Item):
                df_Tmp2.loc[vi_Ind, 'item'] = vs_Item[0]
        
        df_Tmp2 = df_Tmp2.dropna(axis=0, subset=l_Header[1:], how='all')
        df_Tmp2.index = range(0, len(df_Tmp2['Item_name']))
        
# Ook ergens nog getallen checken? Of gewoon laten zo? Is sowieso moeilijk het nog mooi weer te geven