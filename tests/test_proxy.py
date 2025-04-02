import unittest
from src.lab.ProxyManager import ProxyManager
import akshare as ak

class TestProxy(unittest.TestCase):
    
    def setUp(self):
        self.pm = ProxyManager()
        
        
    def test_proxy(self):
        proxy = self.pm.get_tunnel()
        if proxy is not None:
            stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em(proxy=proxy)
            print(stock_zh_a_spot_em_df)
            length = len(stock_zh_a_spot_em_df)
            self.assertGreater(length, 1)
            
    def test_no_proxy(self):
        stock_zh_a_spot_em_df = ak.stock_zh_a_spot_em()
        print(stock_zh_a_spot_em_df)
        length = len(stock_zh_a_spot_em_df)
        self.assertGreater(length, 1)