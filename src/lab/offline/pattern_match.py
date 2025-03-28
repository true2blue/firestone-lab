import akshare as ak
import talib

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
    res = talib.CDLDOJISTAR(stock_zh_a_spot_em_df['今开'].values, stock_zh_a_spot_em_df['最高'].values, stock_zh_a_spot_em_df['最低'].values, stock_zh_a_spot_em_df['最新价'].values)
    indices = [i for i, value in enumerate(res) if value == 100]
    filtered_df = stock_zh_a_spot_em_df.iloc[indices]
    print(filtered_df)