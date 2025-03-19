import akshare as ak
import time
from datetime import datetime

class App(object):
    
    def __init__(self):
        self.orginal_df = []
        self.window = 15
        self.period_percent_min = 1.47
        self.percent_min = 2.0
        self.percent_max = 5.0
        self.amount_min = 1000 * 10000
        self.high_low_percent_min = 4.0
        self.high_low_percent_previous_max = 2.5

    def job(self, stock_zh_a_spot_em_df):
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['名称'].str.startswith(('ST', '*'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.dropna(subset=['最新价'])
        # stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.sort_values(by='涨速', ascending=False).head(2)
        stock_zh_a_spot_em_df['datetime'] = datetime.now().strftime('%H:%M:%S')
        stock_zh_a_spot_em_df.set_index(['代码'], inplace=True)
        # orginal_df = pd.concat([orginal_df, stock_zh_a_spot_em_df])
        self.orginal_df.append(stock_zh_a_spot_em_df)
        if len(self.orginal_df) > self.window:
            self.orginal_df = self.orginal_df[1:]
        # if len(orginal_df.index.get_level_values('datetime').unique()) > 20:
        #     oldest_datetime = orginal_df.index.get_level_values('datetime').unique()[0]
        #     orginal_df = orginal_df[orginal_df.index.get_level_values('datetime') != oldest_datetime]
        if len(self.orginal_df) == self.window:
            stock_zh_a_spot_em_df['涨跌幅(window)'] = (self.orginal_df[-1]['涨跌幅'] - self.orginal_df[-self.window]['涨跌幅'])
            stock_zh_a_spot_em_df['成交额(window)'] = (self.orginal_df[-1]['成交额'] - self.orginal_df[-self.window]['成交额'])
            stock_zh_a_spot_em_df['前期振幅'] = self.orginal_df[-self.window]['振幅']
            # print(stock_zh_a_spot_em_df[['时间', '涨跌幅(window)']])
            stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[
                (stock_zh_a_spot_em_df['涨跌幅(window)'] >= self.period_percent_min)  
                & (stock_zh_a_spot_em_df['涨跌幅'] < self.percent_max) 
                & (stock_zh_a_spot_em_df['涨跌幅'] > self.percent_min)
                & (stock_zh_a_spot_em_df['成交额(window)'] >= self.amount_min) 
                & (stock_zh_a_spot_em_df['最高'] == stock_zh_a_spot_em_df['最新价']) 
                & (stock_zh_a_spot_em_df['前期振幅'] < self.high_low_percent_previous_max)  
                & (stock_zh_a_spot_em_df['振幅'] > self.high_low_percent_min)
            ]
            # print(stock_zh_a_spot_em_df['涨跌幅(window)'])
            if not stock_zh_a_spot_em_df.empty:
                return stock_zh_a_spot_em_df
        return None
    
    
if __name__ == '__main__':
    app = App()
    while True:
        # if datetime.now().strftime('%H:%M:%S') >= '10:00:00':
        try:
            stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
            res_df = app.job(stock_zh_a_spot_em_df)
            if res_df is not None:
                print(res_df)
                break
        except Exception as e:
            print(e)
        time.sleep(3)
    
