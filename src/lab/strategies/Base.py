import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime

class Base(object):

    _logger = logging.getLogger(__name__)
    _handler = TimedRotatingFileHandler(f'logs/firestone-lab-{__name__}.log', when='D', interval=1, backupCount=10 ,encoding='UTF-8')

    def __init__(self, config=None):
        self.set_config(config)

    def set_config(self, config):
        self.config = config
        if self.config is not None:
            if self.is_debug():
                self.setup_logging(logging.DEBUG)
            else:
                self.setup_logging(logging.INFO)

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
        if self.config is None:
            raise ValueError("Configuration is not set. Please provide a valid configuration.")
        if self.is_in_time_range(timeStr):
            return self.job(stock_zh_a_spot_em_df)
        return None, False

    def job(self, stock_zh_a_spot_em_df):
        return stock_zh_a_spot_em_df, False
    
    def is_debug(self):
        return self.config.getboolean('trade', 'debug')
    

    def debug(self, message):
        if self.is_debug():
            self._logger.debug(message)