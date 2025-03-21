from .strategies.Ydls import Ydls
from .trade import Trade
from .util import Util
import time
import akshare as ak
from datetime import datetime
import logging

if __name__ == '__main__':

    _logger = logging.getLogger(__name__)

    buy_list = []
    ydls = Ydls()

    def is_trade_enable():
        return ydls.config.getboolean('trade', 'enable')
    
    if is_trade_enable():
        trade = Trade(ydls.config['trade']['user_id'])
    while True:
        if ydls.config['trade']['enable'] and len(buy_list) >= int(ydls.config['trade']['max_buy_count']):
            break
        timeStr = datetime.now().strftime('%H:%M:%S')
        if (timeStr >= '09:45:00' and timeStr <= '11:30:00') or (timeStr >= '13:00:00' and timeStr <= '15:00:00'):
            try:
                if is_trade_enable():
                    trade.load_config(ydls.config['trade']['user_id'])
                stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
                res_df = ydls.job(stock_zh_a_spot_em_df)
                if res_df is not None:
                    _logger.info(res_df)
                    if is_trade_enable():
                        for index, row in res_df.iterrows():
                            if index in buy_list:
                                continue
                            price = Util.calc_high_limit(row['昨收'])
                            volumne = Util.calc_buy_voulme(price, float(ydls.config['trade']['amount']))
                            res = trade.createDelegate(index, row['名称'], price, volumne, 'buy')
                            if res['state'] == 'success':
                                buy_list.append(index)
                            if len(buy_list) >= int(ydls.config['trade']['max_buy_count']):
                                break
            except Exception as e:
                _logger.error(e, exc_info=True)
        time.sleep(3)
    
