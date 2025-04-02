import logging
from datetime import datetime
from .Base import Base

class Ydls(Base):
    
    _logger = logging.getLogger(__name__)
    
    def __init__(self, config_file='config.ini'):
        super().__init__(config_file)
        self.orginal_df = []
        self.window = int(self.config['params']['window'])
        self.period_percent_min = float(self.config['params']['period_percent_min'])
        self.percent_min = float(self.config['params']['percent_min'])
        self.percent_max = float(self.config['params']['percent_max'])
        self.amount_min = float(self.config['params']['amount_min'])
        self.min_price = float(self.config['params']['min_price'])
        self.max_price = float(self.config['params']['max_price'])
        self.high_low_percent_min = float(self.config['params']['high_low_percent_min'])
        self.high_low_percent_previous_max = float(self.config['params']['high_low_percent_previous_max'])
        self.ratio_high_low_percent = float(self.config['params']['ratio_high_low_percent'])
        self.buy_amount = float(self.config['trade']['buy_amount'])
        
    def job(self, stock_zh_a_spot_em_df):
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['名称'].str.startswith(('ST', '*'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[~stock_zh_a_spot_em_df['代码'].str.startswith(('688', '8', '4', '9', '7'))]
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df.dropna(subset=['最新价'])
        stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[(stock_zh_a_spot_em_df['最新价'] > self.min_price)
                                                      & (stock_zh_a_spot_em_df['最新价'] < self.max_price) 
                                                      & (self.buy_amount / stock_zh_a_spot_em_df['最新价'] > 100)]
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
            match_df = stock_zh_a_spot_em_df[
                (stock_zh_a_spot_em_df['涨跌幅(window)'] >= self.period_percent_min) 
                & (stock_zh_a_spot_em_df['涨跌幅'] <= self.percent_max) 
                & (stock_zh_a_spot_em_df['涨跌幅'] >= self.percent_min)
                & (stock_zh_a_spot_em_df['成交额(window)'] >= self.amount_min) 
                & (stock_zh_a_spot_em_df['最高'] == stock_zh_a_spot_em_df['最新价']) 
                & (stock_zh_a_spot_em_df['前期振幅'] <= self.high_low_percent_previous_max)  
                & (stock_zh_a_spot_em_df['振幅'] >= self.high_low_percent_min)
                & (stock_zh_a_spot_em_df['振幅'] >= stock_zh_a_spot_em_df['前期振幅'] * self.ratio_high_low_percent)
            ]
            # print(stock_zh_a_spot_em_df['涨跌幅(window)'])
            if not match_df.empty:
                return match_df, True
        return stock_zh_a_spot_em_df, False