import unittest
import pandas as pd
from src.app import App
from src.strategies.Ydls import Ydls

class TestApp(unittest.TestCase):

    def setUp(self):
        self.data = pd.read_csv('data/processed/300534-2025-03-20.csv', dtype={'代码': str})

    def test_run_no_trade(self):
        self.ydls = Ydls('config-test-no-trade.ini')
        self.app = App(self.ydls)
        res_list = []
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res = self.app.run(row_df)
            if res['state'] != 'nodata':
                print(res)
                res_list.append(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]['state'], 'success')
        self.assertEqual(res_list[0]['message'], 'data match, no trade')

    def test_run_trade(self):
        self.ydls = Ydls('config-test-trade.ini')
        self.app = App(self.ydls)
        res_list = []
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res = self.app.run(row_df)
            if res['state'] != 'nodata':
                print(res)
                res_list.append(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(len(self.app.get_buy_list()), 1)
        self.assertEqual(self.app.get_buy_list()[0], '300534')
        self.assertEqual(res_list[0]['state'], 'success')
        self.assertEqual(res_list[0]['message'], 'trade success')

if __name__ == '__main__':
    unittest.main()