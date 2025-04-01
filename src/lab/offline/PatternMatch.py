import akshare as ak
import talib
from talib import abstract
import pandas as pd
import os
from datetime import datetime

enable_concept = False
stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
start_date = "20250101"

def read_target_codes():
    if os.path.exists('./output/codes.csv'):
        return pd.read_csv('./output/codes.csv')
    return None

if stock_zh_a_spot_em_df.empty:
    print("No data available for the given date range.")
else:
    target_codes = read_target_codes()
    if enable_concept and target_codes is not None:
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'].isin(target_codes['代码'])]
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['名称'].str.startswith(('ST', '*'))]
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.dropna(subset=['最新价'])
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[(stock_zh_a_spot_em_df['最新价'] > 5)
                                                    & (stock_zh_a_spot_em_df['最新价'] < 30) 
                                                    & (3000 / stock_zh_a_spot_em_df['最新价'] > 100)]
    pattern_list = {
        'CDLMORNINGSTAR' : pd.DataFrame(),
        'CDLENGULFING' : pd.DataFrame()
    }
    for index, row in stock_zh_a_spot_em_df.iterrows():
        symbol = row['代码']
        current_date = datetime.now().strftime('%Y%m%d')
        data_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start_date, end_date=current_date, adjust="qfq")
        data_df["RSI"] = talib.RSI(data_df["收盘"], timeperiod=14)
        data_df["volume_roc"] = talib.ROC(data_df['成交量'], timeperiod=1)

        for pattern in pattern_list.keys():
            func = abstract.Function(pattern)
            data_df[pattern] = func(data_df['开盘'].values, 
            data_df['最高'].values, 
            data_df['最低'].values, 
            data_df['收盘'].values)
            if data_df.iloc[-1][pattern] == 100 and data_df.iloc[-1]["volume_roc"] > 50:
                pattern_list[pattern] = pd.concat([pattern_list[pattern], data_df.iloc[[-1]]], ignore_index=True)
    
    data_all_df = pd.concat(pattern_list.values(), ignore_index=True)
    data_all_df.to_csv('./output/pm.csv', index=False)