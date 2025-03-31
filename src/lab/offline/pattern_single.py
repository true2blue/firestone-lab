import akshare as ak
import talib

data_df = ak.stock_zh_a_hist(symbol='000001', period="daily", start_date="20250101", end_date='20250331', adjust="qfq")


max_high = data_df['最高'].max()
min_low = data_df['最低'].min()
close = data_df.iloc[-1]['收盘']
percent = (close - min_low) / (max_high - min_low) * 100
print(percent)
# print(f"Max value in 最高: {max_high}, Min value in 最低: {min_low}")

# data_df['CDLMORNINGDOJISTAR'] = talib.CDLMORNINGDOJISTAR(data_df['开盘'].values, 
#     data_df['最高'].values, 
#     data_df['最低'].values, 
#     data_df['收盘'].values)

# temp_df = data_df[data_df['CDLMORNINGDOJISTAR'] == 100]
# print(temp_df)
# temp_df.to_csv('./output/temp.csv', index=False)
    # print(codes)