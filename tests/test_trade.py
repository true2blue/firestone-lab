import unittest
from src.lab.trade import Trade

class TestTrade(unittest.TestCase):

    def setUp(self):
        self.trade = Trade('5d905db9fc84d3224b0eb59c')

    def test_load_config(self):
        self.trade.load_config('5d905db9fc84d3224b0eb59c')
        self.assertIsNotNone(self.trade.last_refresh)

    def test_is_expired(self):
        self.trade.load_config('5d905db9fc84d3224b0eb59c')
        self.assertFalse(self.trade.is_expired())


    def test_createDelegate(self):
        self.trade.load_config('5d905db9fc84d3224b0eb59c')
        res = self.trade.createDelegate('300534', '陇神戎发', 9.0, 100, 'buy')
        print(res)
        self.assertEqual(res['state'], 'success')
    
    def tearDown(self):
        self.trade.close()
        return super().tearDown()