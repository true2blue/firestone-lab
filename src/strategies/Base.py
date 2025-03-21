import logging
import configparser
from logging.handlers import TimedRotatingFileHandler
from ..util import Util

class Base(object):

    _logger = logging.getLogger(__name__)
    _handler = TimedRotatingFileHandler('logs/firestone-lab.log', when='D', interval=1, backupCount=10 ,encoding='UTF-8')

    def __init__(self, config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(f'./config/{config_file}')
        self.setup_logging(logging.INFO)

    def setup_logging(self, loglevel):
        logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
        logging.basicConfig(level=loglevel, format=logformat, datefmt="%Y-%m-%d %H:%M:%S", handlers=[Base._handler])

    def job(self, stock_zh_a_spot_em_df):
        return None
    
    def is_trade_enable(self):
        return self.config.getboolean('trade', 'enable')
    
    def get_user_id(self):
        return self.config['trade']['user_id']
    
    def get_max_buy_count(self):
        return int(self.config['trade']['max_buy_count'])
    
    def get_buy_volume(self, price):
        if 'buy_volumne' in self.config['trade']:
            return int(self.config['trade']['buy_volumne'])
        else:
            return Util.calc_buy_voulme(price, float(self.config['trade']['buy_amount']))