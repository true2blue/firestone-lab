
from .trade import Trade
from .util import Util
import time
import akshare as ak
from datetime import datetime
import logging
from .strategies.Base import Base
from .strategies.Ydls import Ydls
from .strategies.YdlsConcept import YdlsConcept
import sys
import os
import configparser

# Add the parent directory of 'src' to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class App(object):
    
    _logger = logging.getLogger(__name__)

    def __init__(self, bases: list[Base], config_file='config.ini'):
        self.config = configparser.ConfigParser()
        self.config.read(f'./config/{config_file}', encoding='utf-8')
        self.bases = bases
        for base in self.bases:
            base.set_config(self.config)
        self.match_list = []
        self.order = {
            'success': [],
            'failed': []
        }
        if self.is_trade_enable():
            self.trade = Trade(self.get_user_id())

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
            
    def has_match(self, code):
        return code in self.match_list
    
    def add_match(self, code):
        if code not in self.match_list:
            self.match_list.append(code)
            
    def get_match_list(self):
        return self.match_list            
            
    def get_match_list_count(self):   
        return len(self.match_list)
            
    def add_order(self, status, code):
        if code not in self.order[status]:
            self.order[status].append(code)
        
    def get_success_order(self):
        return self.order['success']
        
    def get_success_order_count(self):
        return len(self.order['success'])
    
    def get_failed_order(self):   
        return self.order['failed']

    def need_trade(self):
        return hasattr(self, 'trade')

    def is_reach_max_buy_count(self):
        if self.need_trade():
            return self.get_success_order_count() >= self.get_max_buy_count()
        return self.get_match_list_count() >= self.get_max_buy_count()
    
    def get_complete_buy_list(self):
        return self.get_success_order() if self.need_trade() else self.get_match_list()
    
    def close(self):
        if self.need_trade():
            self.trade.close()

    def run(self, stock_zh_a_spot_em_df, timeStr = datetime.now().strftime('%H:%M:%S')):
        if self.is_reach_max_buy_count():
            return {'state': 'complete', 'message': 'reach max buy count', 'data' : self.get_complete_buy_list()}
        if self.need_trade():
            self.trade.load_config(self.get_user_id())
        result = {'state': 'nodata', 'message': 'no data match', 'data' : []}
        for base in self.bases:
            res_df, status = base.run(stock_zh_a_spot_em_df, timeStr=timeStr)
            if status:
                App._logger.info(res_df)
                rows = []
                rows_success = []
                for index, row in res_df.iterrows():
                    if self.has_match(index):
                        continue
                    self.add_match(index)
                    rows.append(row)
                    if self.need_trade():
                        price = Util.calc_high_limit(row['昨收'])
                        volumne = self.get_buy_volume(price)
                        if volumne >= 100:
                            res = self.trade.createDelegate(index, row['名称'], price, volumne, 'buy')
                            if res['state'] == 'success':
                                self.add_order('success', index)
                                rows_success.append(index)
                            else:
                                self.add_order('failed', index)
                        else:
                            App._logger.error(f'volumne is too low: {volumne} for {index}')
                            self.add_order('failed', index)
                    if self.is_reach_max_buy_count():
                        return {'state': 'complete', 'message': 'reach max buy count', 'data' : self.get_complete_buy_list()}
                if self.need_trade() and len(rows_success) > 0:
                    result['state'] = 'success'
                    result['message'] = 'trade success'
                    result['data'].extend(rows_success)
                elif len(rows) > 0:
                    result['state'] = 'success'
                    result['message'] = 'data match, no trade'
                    result['data'].extend(rows)
        return result

if __name__ == '__main__':
    app = None
    try:
        app = App([Ydls()])
        App._logger.info('Lab ready to start')
        while True:
            timeStr = datetime.now().strftime('%H:%M:%S')
            if timeStr > '15:00:00':
                break
            if (timeStr >= '09:30:00' and timeStr <= '11:30:00') or (timeStr >= '13:00:00' and timeStr <= '15:00:00'):
                try:
                    stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                    res = app.run(stock_zh_a_spot_em_df)
                    if res['state'] != 'nodata':
                        App._logger.info(res)
                    if res['state'] == 'complete':
                        break
                except Exception as e:
                    App._logger.error(e, exc_info=True)
            time.sleep(3)
        app.close()
    except Exception as e:
        App._logger.error(e, exc_info=True)
    finally:
        if app is not None:
            App._logger.info(f'trade complete, match list: {app.get_match_list()}, success order: {app.get_success_order()} failed order: {app.get_failed_order()}')
        else:
            App._logger.error('app is not initialized')