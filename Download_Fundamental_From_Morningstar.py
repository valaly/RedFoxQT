# -*- coding: utf-8 -*-
"""
Created on Sun Jul 23 18:09:05 2017

@author: Valerie
"""

from downloader import WebsiteData as ClassWd
import DataFrameManipulation as m_Dfm
#from time import sleep

vi_StartPoint = 100
vi_EndPoint = vi_StartPoint + 100

df_Rsl = m_Dfm.f_ReadCsv('Russell2000_Tickers', vs_Path="C:/Users/Valerie/OneDrive/RedFox/Software/")
l_RslTicker = df_Rsl['ticker'].values
vs_Path = "C:/Users/Valerie/OneDrive/RedFox/Software/MorningStar_Russell2000/"

l_ReportType = ["is", "bs", "cf"]  #is = Income Statement, cf = Cash Flow, bs = Balance Sheet
l_Period = [12, 3]  #12 for annual, 3 for quarterly
vs_Order = "asc" # or desc
vi_ColumnYear = 10   # or 5 (years)
vi_Number = 2       # units of the response data: 1 = None, 2 = Thousands, 3 = Milions, 4 = Bilions

dwn = ClassWd()
for vi_Ticker, vs_Ticker in enumerate(l_RslTicker[vi_StartPoint:vi_EndPoint]):
    for vs_ReportType in l_ReportType:        
        for vi_Period in l_Period:              
            vs_Name = '_'.join([vs_ReportType, vs_Ticker, str(vi_Period), str(vi_ColumnYear), str(vi_Number)])
            vs_API = ''.join(["http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=", vs_Ticker,
                "&reportType=", vs_ReportType, "&period=", str(vi_Period), "&dataType=A&order=", vs_Order, 
                "&columnYear=", str(vi_ColumnYear), "&number=", str(vi_Number)])
             
            dwn.get_csv_file(location=vs_Path, name=vs_Name, site_csvfile=vs_API)
            print vi_Ticker + vi_StartPoint, vs_Name