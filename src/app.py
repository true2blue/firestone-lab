import akshare as ak
import time
from datetime import datetime
import pandas as pd

orginal_df = []

while True:
    if datetime.now().strftime('%H:%M:%S') >= '10:00:00':
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['名称'].str.startswith(('ST', '*'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.dropna(subset=['最新价'])
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.sort_values(by='涨速', ascending=False).head(2)
        stock_zh_a_spot_em_df['datetime'] = datetime.now().strftime('%H:%M:%S')
        stock_zh_a_spot_em_df.set_index(['代码'], inplace=True)
        # orginal_df = pd.concat([orginal_df, stock_zh_a_spot_em_df])
        orginal_df.append(stock_zh_a_spot_em_df)
        if len(orginal_df) > 5:
            orginal_df = orginal_df[1:]
        # if len(orginal_df.index.get_level_values('datetime').unique()) > 20:
        #     oldest_datetime = orginal_df.index.get_level_values('datetime').unique()[0]
        #     orginal_df = orginal_df[orginal_df.index.get_level_values('datetime') != oldest_datetime]
        if len(orginal_df) == 5:
            stock_zh_a_spot_em_df['涨跌幅(15s)'] = (orginal_df[-1]['涨跌幅'] - orginal_df[-5]['涨跌幅'])
            stock_zh_a_spot_em_df['成交额(15s)'] = (orginal_df[-1]['成交额'] - orginal_df[-5]['成交额'])
            stock_zh_a_spot_em_df['前期振幅'] = orginal_df[-5]['振幅']
            stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[
                (stock_zh_a_spot_em_df['涨跌幅(15s)'] >= 3.0) & (stock_zh_a_spot_em_df['涨跌幅'] < 5.0) & (stock_zh_a_spot_em_df['涨跌幅'] > 2.0) &
                (stock_zh_a_spot_em_df['成交额(15s)'] >= 1000 * 10000) & (stock_zh_a_spot_em_df['最高'] == stock_zh_a_spot_em_df['最新价']) &
                (stock_zh_a_spot_em_df['前期振幅'] < 1.0) & (stock_zh_a_spot_em_df['振幅'] > 2.5)
            ]
            if not stock_zh_a_spot_em_df.empty:
                print(stock_zh_a_spot_em_df)
        # print(datetime.now())
    time.sleep(3)