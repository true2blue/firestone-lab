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
        self.buy_list = []

    def run(self, stock_zh_a_spot_em_df):
        if self.base.is_trade_enable():
            trade = Trade(self.base.get_user_id())
            if self.base.is_trade_enable() and len(self.buy_list) >= self.base.get_max_buy_count():
                return {'state': 'complete', 'message': 'reach max buy count', 'data' : self.buy_list}
            if self.base.is_trade_enable():
                trade.load_config(self.base.get_user_id())
            res_df = self.base.job(stock_zh_a_spot_em_df)
            if res_df is not None:
                App._logger.info(res_df)
                if self.base.is_trade_enable():
                    for index, row in res_df.iterrows():
                        if index in self.buy_list:
                            continue
                        price = Util.calc_high_limit(row['昨收'])
                        volumne = self.base.get_buy_volume(price)
                        res = trade.createDelegate(index, row['名称'], price, volumne, 'buy')
                        if res['state'] == 'success':
                            self.buy_list.append(index)
                        if len(self.buy_list) >= self.base.get_max_buy_count():
                            return {'state': 'complete', 'message': 'reach max buy count', 'data': res_df}
                    return {'state': 'success', 'message': 'trade success', 'data': res_df}
                else:
                    return {'state': 'success', 'message': 'data match, no trade', 'data': res_df}
            return {'state': 'nodata', 'message': 'no data match'}

if __name__ == '__main__':

    ydls = Ydls()
    app = App(ydls)
    while True:
        timeStr = datetime.now().strftime('%H:%M:%S')
        if (timeStr >= '09:45:00' and timeStr <= '11:30:00') or (timeStr >= '13:00:00' and timeStr <= '15:00:00'):
            try:
                stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                app.run(stock_zh_a_spot_em_df)
            except Exception as e:
                App._logger.error(e, exc_info=True)
        time.sleep(3)