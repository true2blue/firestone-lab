import logging
from .Ydls import Ydls
import pandas as pd
import os

class YdlsConcept(Ydls):
    
    _logger = logging.getLogger(__name__)
    
    def __init__(self, config=None):
        super().__init__(config)
        self.target_codes = self.read_target_codes()

    def set_config(self, config):
        super().set_config(config)
        if self.config is not None:
            self.window = int(self.config['params_concept']['window'])
            self.period_percent_min = float(self.config['params_concept']['period_percent_min'])
            self.open_percent_min = float(self.config['params_concept']['open_percent_min'])
            self.open_percent_max = float(self.config['params_concept']['open_percent_max'])
            self.percent_min = float(self.config['params_concept']['percent_min'])
            self.percent_max = float(self.config['params_concept']['percent_max'])
            self.amount_min = float(self.config['params_concept']['amount_min'])
            self.high_low_percent_min = float(self.config['params_concept']['high_low_percent_min'])
            self.high_low_percent_previous_max = float(self.config['params_concept']['high_low_percent_previous_max'])
            self.ratio_high_low_percent = float(self.config['params_concept']['ratio_high_low_percent'])
            self.buy_amount = float(self.config['trade']['buy_amount'])

    def read_target_codes(self):
        if os.path.exists('./output/codes.csv'):
            return pd.read_csv('./output/codes.csv', dtype={'代码': str})
        return None
        
    def job(self, stock_zh_a_spot_em_df):
        pre_df, status = super().job(stock_zh_a_spot_em_df)
        if status and self.target_codes is not None:
            stock_zh_a_spot_em_df['开盘涨幅'] = (stock_zh_a_spot_em_df['今开'] - stock_zh_a_spot_em_df['昨收']) / stock_zh_a_spot_em_df['昨收'] * 100
            stock_zh_a_spot_em_df = stock_zh_a_spot_em_df[
                (stock_zh_a_spot_em_df['开盘涨幅'] >= self.open_percent_min) 
                & (stock_zh_a_spot_em_df['开盘涨幅'] <= self.open_percent_max)
            ]
            match_df = stock_zh_a_spot_em_df[stock_zh_a_spot_em_df['代码'].isin(self.target_codes['代码'])]
            if not match_df.empty:
                return match_df, True
        return pre_df, False