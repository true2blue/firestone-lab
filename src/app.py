import akshare as ak
import time
from datetime import datetime
import pandas as pd

def setup_original_df(intervals):
    global orginal_df
    orginal_df = {str(interval): {'last_sample_time': None, 'data': None} for interval in intervals}

def sampling(df):
    now = datetime.now()
    for interval, data in orginal_df.items():
        if data['last_sample_time'] is None:
            data['last_sample_time'] = now
        elif (now - data['last_sample_time']).total_seconds() >= int(interval):
            data['last_sample_time'] = now
            data['data'] = df

def get_sampling_data(interval) -> pd.DataFrame:
    return orginal_df[interval]['data']


def get_average_amount(intervalA, intervalB, intervalC):
    dataA = get_sampling_data(intervalA)
    dataB = get_sampling_data(intervalB)
    if dataA is None or dataB is None:
        return None
    diff_amount = dataB['成交额'] - dataA['成交额']
    # Calculate time difference directly since datetime column contains datetime objects
    diff_time = (dataB['datetime'] - dataA['datetime']).dt.total_seconds()
    # Element-wise division and multiplication
    return diff_amount / diff_time * intervalC

def job(stock_zh_a_spot_em_df):
    try:
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['名称'].str.startswith(('ST', '*'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.dropna(subset=['最新价'])
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.sort_values(by='涨速', ascending=False).head(2)
        stock_zh_a_spot_em_df['datetime'] = datetime.now()
        stock_zh_a_spot_em_df.set_index(['代码'], inplace=True)
        sampling(stock_zh_a_spot_em_df)
        if datetime.now().strftime('%H:%M:%S') >= '10:00:00':
            sample_15 = get_sampling_data('15')
            if sample_15 is not None:
                stock_zh_a_spot_em_df['涨跌幅(15s)'] = (stock_zh_a_spot_em_df['涨跌幅'] - sample_15['涨跌幅'])
                stock_zh_a_spot_em_df['成交额(15s)'] = (stock_zh_a_spot_em_df['成交额'] - sample_15['成交额'])
                stock_zh_a_spot_em_df['前期振幅'] = sample_15['振幅']
                stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[
                    (stock_zh_a_spot_em_df['涨跌幅(15s)'] >= 3.0) & (stock_zh_a_spot_em_df['涨跌幅'] < 5.0) & (stock_zh_a_spot_em_df['涨跌幅'] > 2.0) &
                    (stock_zh_a_spot_em_df['成交额(15s)'] >= 1000 * 10000) & (stock_zh_a_spot_em_df['最高'] == stock_zh_a_spot_em_df['最新价']) &
                    (stock_zh_a_spot_em_df['前期振幅'] < 1.0) & (stock_zh_a_spot_em_df['振幅'] > 2.5)
                ]
                if not stock_zh_a_spot_em_df.empty:
                    return stock_zh_a_spot_em_df
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


if __name__ == "__main__":
    setup_original_df([15, 30, 60, 180, 300, 900, 1800])
    while True:
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        res_df = job(stock_zh_a_spot_em_df)
        if res_df is not None:
            print(res_df)
        time.sleep(3)