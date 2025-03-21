import akshare as ak
import time
import logging
from logging.handlers import TimedRotatingFileHandler
from datetime import datetime
import configparser
from .trade import Trade
from .util import Util

class App(object):
    
    _logger = logging.getLogger(__name__)
    _handler = TimedRotatingFileHandler('logs/firestone-lab.log', when='D', interval=1, backupCount=10 ,encoding='UTF-8')
    
    def __init__(self):
        self.config = configparser.ConfigParser().read('./config/config.ini')
        self.orginal_df = []
        self.window = self.config['params']['window']
        self.period_percent_min = self.config['params']['period_percent_min']
        self.percent_min = self.config['params']['percent_min']
        self.percent_max = self.config['params']['percent_max']
        self.amount_min = self.config['params']['amount_min']
        self.high_low_percent_min = self.config['params']['high_low_percent_min']
        self.high_low_percent_previous_max = self.config['params']['high_low_percent_previous_max']
        self.setup_logging(logging.INFO)
        
    def setup_logging(self, loglevel):
        logformat = "[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
        logging.basicConfig(level=loglevel, format=logformat, datefmt="%Y-%m-%d %H:%M:%S", handlers=[App._handler])

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
                & (stock_zh_a_spot_em_df['涨跌幅'] <= self.percent_max) 
                & (stock_zh_a_spot_em_df['涨跌幅'] >= self.percent_min)
                & (stock_zh_a_spot_em_df['成交额(window)'] >= self.amount_min) 
                & (stock_zh_a_spot_em_df['最高'] == stock_zh_a_spot_em_df['最新价']) 
                & (stock_zh_a_spot_em_df['前期振幅'] <= self.high_low_percent_previous_max)  
                & (stock_zh_a_spot_em_df['振幅'] >= self.high_low_percent_min)
            ]
            # print(stock_zh_a_spot_em_df['涨跌幅(window)'])
            if not stock_zh_a_spot_em_df.empty:
                return stock_zh_a_spot_em_df
        return None
    
    
if __name__ == '__main__':
    app = App()
    if app.config['trade']['enable']:
        trade = Trade()
    buy_count = 0
    while True:
        if app.config['trade']['enable'] and buy_count >= app.config['trade']['max_buy_count']:
            break
        timeStr = datetime.now().strftime('%H:%M:%S')
        if (timeStr >= '09:45:00' and timeStr <= '11:30:00') or (timeStr >= '13:00:00' and timeStr <= '15:00:00'):
            try:
                if app.config['trade']['enable']:
                    trade.load_config()
                stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                res_df = app.job(stock_zh_a_spot_em_df)
                if res_df is not None:
                    App._logger.info(res_df)
                    if app.config['trade']['enable']:
                        for index, row in res_df.iterrows():
                            price = Util.calc_high_limit(row['昨收'])
                            volumne = Util.calc_buy_voulme(price, app.config['trade']['amount'])
                            res = trade.createDelegate(index, row['名称'], price, volumne, 'buy')
                            if res['state'] == 'success':
                                buy_count += 1
                    break
            except Exception as e:
                App._logger.error(e)
        time.sleep(3)
    
