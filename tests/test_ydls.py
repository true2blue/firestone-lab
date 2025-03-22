import unittest
import pandas as pd
from src.strategies.Ydls import Ydls

class TestApp(unittest.TestCase):
    
    def setUp(self):
        self.ydls = Ydls(config_file='config-test-no-trade.ini')
        self.data = pd.read_csv('data/processed/300534-2025-03-20.csv', dtype={'代码': str})


    def test_is_trade_enable(self):
        self.assertFalse(self.ydls.is_trade_enable())

    def test_get_user_id(self):
        self.assertEqual(self.ydls.get_user_id(), '5d905db9fc84d3224b0eb59c')

    def test_get_max_buy_count(self):
        self.assertEqual(self.ydls.get_max_buy_count(), 3)

    def test_get_buy_volume(self):
        self.assertEqual(self.ydls.get_buy_volume(10.13), 200)
        
    def test_is_in_time_range(self):
        self.assertTrue(self.ydls.is_in_time_range(timeStr='09:46:00'))
        self.assertTrue(self.ydls.is_in_time_range(timeStr='11:30:00'))
        self.assertFalse(self.ydls.is_in_time_range(timeStr='15:10:00'))

    def test_job(self):
        res_df = None
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res_df = self.ydls.job(row_df)
            if res_df is not None:
                print(res_df)                
                break
        self.assertIsNotNone(res_df)

if __name__ == '__main__':
    unittest.main()