import akshare as ak
import talib

data_df = ak.stock_zh_a_hist(symbol='603238', period="daily", start_date="20150101", end_date='20250328', adjust="qfq")

data_df['CDLMORNINGDOJISTAR'] = talib.CDLMORNINGDOJISTAR(data_df['开盘'].values, 
    data_df['最高'].values, 
    data_df['最低'].values, 
    data_df['收盘'].values)

temp_df = data_df[data_df['CDLMORNINGDOJISTAR'] == 100]
print(temp_df)
temp_df.to_csv('./output/temp.csv', index=False)
    # print(codes)