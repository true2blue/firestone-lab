from .strategies.Ydls import Ydls
from .trade import Trade
from .util import Util
import time
import akshare as ak
from datetime import datetime
import logging
from .strategies.Base import Base


class App(object):
    
    _logger = logging.getLogger(__name__)

    def __init__(self, base: Base):
        self.base = base
        self.match_list = []
        self.order = {
            'success' : [],
            'failed' : []
        }
        if self.base.is_trade_enable():
            self.trade = Trade(self.base.get_user_id())
            
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

    def need_trade(self):
        return hasattr(self, 'trade')

    def is_reach_max_buy_count(self):
        if self.need_trade():
            return self.get_success_order_count() >= self.base.get_max_buy_count()
        return self.get_match_list_count() >= self.base.get_max_buy_count()
    
    def get_complete_buy_list(self):
        return self.get_success_order() if self.need_trade() else self.get_match_list()
    
    def close(self):
        if self.need_trade():
            self.trade.close()

    def run(self, stock_zh_a_spot_em_df, timeStr = datetime.now().strftime('%H:%M:%S')):
        if self.is_reach_max_buy_count():
            return {'state': 'complete', 'message': 'reach max buy count', 'data' : self.get_complete_buy_list()}
        if self.need_trade():
            self.trade.load_config(self.base.get_user_id())
        res_df = self.base.run(stock_zh_a_spot_em_df, timeStr=timeStr)
        if res_df is not None:
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
                    volumne = self.base.get_buy_volume(price)
                    res = self.trade.createDelegate(index, row['名称'], price, volumne, 'buy')
                    if res['state'] == 'success':
                        self.add_order('success', index)
                        rows_success.append(index)
                    else:
                        self.add_order('failed', index)
                if self.is_reach_max_buy_count():
                    return {'state': 'complete', 'message': 'reach max buy count', 'data' : self.get_complete_buy_list()}
            result = {'state': 'success', 'message': 'data match, no trade', 'data': rows}
            if self.need_trade():
                result = {'state': 'success', 'message': 'trade success', 'data': rows_success}
            return result
        return {'state': 'nodata', 'message': 'no data match'}

if __name__ == '__main__':

    ydls = Ydls()
    app = App(ydls)
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