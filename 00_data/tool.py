# -*- coding: UTF-8 -*-    
import pandas as pd
from pandas.io.json import json_normalize
import json
import pathlib

def read_finmain():
    p = pathlib.Path('./json')
    files = list(p.glob('*.json'))

    dframes = []
    for file in files:
        with file.open() as f:
            data_str = f.read()
            data_list = json.loads(data_str)
            df = json_normalize(data_list["list"])
            df['symbol'] = file.stem.lower()
            dframes.append(df)

    r = pd.concat(dframes)
    r.reportdate = pd.to_datetime(r['reportdate'])
    r.reportdate = r.reportdate.dt.to_period("Q")
    return r

def read_fzb():
    p = pathlib.Path('./csv')
    files = list(p.glob('*_fzb.csv'))

    dframes = []
    for file in files:
        df = pd.read_csv(str(file))
        df['symbol'] = file.stem.lower()[:8]
        dframes.append(df)

    r = pd.concat(dframes)
    r['报表日期'] = pd.to_datetime(r['报表日期'], format='%Y%m%d')
    r['报表日期'] = r['报表日期'].dt.to_period("Q")
    return r

def calculate(row):
    if pd.notnull(row['股本']):
        return row['股本']
    else:
        return row['实收资本(或股本)']

#https://stackoverflow.com/questions/19818756/extract-row-with-maximum-value-in-a-group-pandas-dataframe
def get_totalshare(df = None):
    if df is None:
        df = read_fzb()

    dfnew = df[['symbol', '报表日期', '实收资本(或股本)', '股本']].groupby('symbol').first()
    dfnew['totalshare'] = dfnew.apply(calculate, axis=1)
    dfnew.drop(columns=['报表日期', '实收资本(或股本)', '股本'], inplace=True)
    return dfnew

def calculate_ttm(row):
    if pd.notnull(row['2017Q4']):
        return row['2017Q4']
    else:
        return row['2017Q3'] + row['2016Q4'] - row['2016Q3']

def calculate_ttmday(row):
    if pd.notnull(row['2017Q4']):
        return '2017Q4'
    else:
        return '2017Q3'

def get_profits(df = None):
    # https://stackoverflow.com/questions/36217969/how-to-compare-pandas-dataframe-against-none-in-python
    if df is None:
        df = read_finmain()

    dfp = df.loc[df.reportdate > pd.Period('2016Q2'), ['symbol', 'reportdate', 'netprofit']]
    dfp.sort_values(by=['reportdate'])
    dfp.reportdate = dfp.reportdate.apply(str)
    profits = dfp.pivot_table('netprofit', ['symbol'], 'reportdate')
    profits['ttm'] = profits.apply(calculate_ttm, axis=1)
    profits['ttm_day'] = profits.apply(calculate_ttmday, axis=1)
    profits.drop(columns=['2016Q3', '2016Q4', '2017Q1', '2017Q2', '2017Q3', '2017Q4'], inplace = True)
    return profits
