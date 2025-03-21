import requests
import logging
import json
from time import time
from datetime import datetime
from pymongo import MongoClient
import os
from bson.objectid import ObjectId

class Trade(object):
    
    _MONFO_URL = '127.0.0.1'
    
    _logger = logging.getLogger(__name__)
    
    def __init__(self, user_id):
        self.__header = {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Host': 'jy.xzsec.com',
            'Origin': 'https://jy.xzsec.com',
            'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.71 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest'
        }
        self.client = MongoClient(Trade._MONFO_URL, 27017)
        self.db = self.client[os.environ['FR_DB']]
        self.force_refresh = False
        self.last_refresh = None
        self.cols = {
            'configs' : 'configs'
        }
        self.load_config(user_id)
    
    def load_config(self, user_id):
        if self.force_refresh or self.is_expired():
            self.config = self.db[self.cols['configs']].find_one({"userId": ObjectId(user_id)})
            Trade._logger.info(f'load config = {self.config}')
            self.__header['gw_reqtimestamp'] = f'{int(time()*1000)}'
            old_cookie = None
            if 'Cookie' in self.__header:
                old_cookie = self.__header['Cookie']
            self.__header['Cookie'] = self.config['cookie']
            self.__validatekey = self.config['validatekey']
            if old_cookie != self.__header['Cookie']:
                self.last_refresh = datetime.now()
                self.force_refresh = False

    def is_expired(self):
        return self.last_refresh is None or (datetime.now() - self.last_refresh).seconds > 60 * 60 * 3
    
    def createDelegate(self, code, name, price, volume, op):
        try:
            tradeType = 'Buy' if op == 'buy' else 'Sell'
            self.__header['Referer'] = f'https://jy.xzsec.com/Trade/{tradeType}'
            market = 'HA' if (code.startswith('6') or code.startswith('5')) else 'SA'
            postData = {
                'stockCode': code,
                'price': price,
                'amount': volume,
                'tradeType': tradeType[0],
                'zqmc': name,
                'market': market
            }
            if op == 'sell':
                if (code.startswith('6') or code.startswith('5')):
                    postData['hgddm'] = self.config['hgddm']
                else:
                    postData['gddm'] = self.config['gddm']
            url = f'https://jy.xzsec.com/Trade/SubmitTradeV2?validatekey={self.__validatekey}'
            response = requests.post(url,data=postData,headers=self.__header, verify=False)
            # text = self.unzip_data(response.content)
            Trade._logger.info('real code = {}, price = {}, volume = {}, op = {}, submit order get response = {}'.format(code, price, volume, op, response.text))
            result = json.loads(response.text)
            if(result['Status'] == 0):
                op_cn = '买入' if op == 'buy' else '卖出'
                message = '订单提交: 在{},以{}{}[{}] {}股'.format(datetime.now(), price, op_cn, code, volume)
                order = {
                    'result' : {
                        'data' : {
                            'htbh' : result['Data'][0]['Wtbh']
                        }
                    }
                }
                return {'state' : 'success', 'result' : message, 'order' : order}
            else:
                self.force_refresh = True
                return {'state' : 'failed', 'result' : result}
        except Exception as e:
            Trade._logger.error('mock code = {}, price = {}, volume = {}, op = {}, faield with exception = {}'.format(code, price, volume, op, e), exc_info=True)
            self.force_refresh = True
            return {'state' : 'failed', 'result' : '创建订单失败'}