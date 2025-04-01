import logging
import configparser
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
from ..util import Util
import pandas as pd
import os

class Base(object):

    _logger = logging.getLogger(__name__)
    _handler = TimedRotatingFileHandler('logs/firestone-lab.log', when='D', interval=1, backupCount=10 ,encoding='UTF-8')

    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(f'./config/{config_file}', encoding='utf-8')
        self.setup_logging(logging.INFO)
        self.target_codes = self.read_target_codes()

    def read_target_codes(self):
        if self.is_codes_filter_enable() and os.path.exists('./output/codes.csv'):
            return pd.read_csv('./output/codes.csv', dtype={'代码': str})
        return None

    def setup_logging(self, loglevel):
        logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
        logging.basicConfig(level=loglevel, format=logformat, datefmt="%Y-%m-%d %H:%M:%S", handlers=[Base._handler])
        
    def is_in_time_range(self, timeStr): 
        for time_period in self.config['params']['time_period'].split(','):
            time_period_array = time_period.split('-')
            if timeStr >= time_period_array[0] and timeStr <= time_period_array[1]:
                return True
        return False
    
    def run(self, stock_zh_a_spot_em_df, timeStr = datetime.now().strftime('%H:%M:%S')):
        if self.is_in_time_range(timeStr):
            return self.job(stock_zh_a_spot_em_df)
        return None, False

    def job(self, stock_zh_a_spot_em_df):
        return stock_zh_a_spot_em_df, False
    
    def is_trade_enable(self):
        return self.config.getboolean('trade', 'enable')
    
    def is_codes_filter_enable(self):
        return self.config.getboolean('params', 'codes_filter')
    
    def get_user_id(self):
        return self.config['trade']['user_id']
    
    def get_max_buy_count(self):
        return int(self.config['trade']['max_buy_count'])
    
    def get_buy_volume(self, price):
        if 'buy_volumne' in self.config['trade']:
            return int(self.config['trade']['buy_volumne'])
        else:
            return Util.calc_buy_voulme(price, float(self.config['trade']['buy_amount']))