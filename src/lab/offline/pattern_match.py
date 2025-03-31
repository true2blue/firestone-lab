import akshare as ak
import talib
import pandas as pd

stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()

if stock_zh_a_spot_em_df.empty:
    print("No data available for the given date range.")
else:
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['名称'].str.startswith(('ST', '*'))]
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.dropna(subset=['最新价'])
    stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[(stock_zh_a_spot_em_df['最新价'] > 5)
                                                    & (stock_zh_a_spot_em_df['最新价'] < 30) 
                                                    & (3000 / stock_zh_a_spot_em_df['最新价'] > 100)]
    data_all_df = pd.DataFrame()
    for index, row in stock_zh_a_spot_em_df.iterrows():
        symbol = row['代码']
        data_df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date="20250101", end_date='20250328', adjust="qfq")

        data_df['CDLMORNINGDOJISTAR'] = talib.CDLMORNINGSTAR(data_df['开盘'].values, 
            data_df['最高'].values, 
            data_df['最低'].values, 
            data_df['收盘'].values)

        if data_df.iloc[-1]['CDLMORNINGDOJISTAR'] == 100:
            data_all_df = pd.concat([data_all_df, data_df.iloc[[-1]]], ignore_index=True)
    data_all_df.to_csv('./output/data_all_df.csv', index=False)
    # print(codes)