import unittest
import pandas as pd
from src.lab.app import App
from src.lab.strategies.Ydls import Ydls
from src.lab.strategies.YdlsConcept import YdlsConcept

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = App([], config_file='config-test-no-trade.ini')
        self.data = pd.read_csv('data/processed/600239-2025-03-28.csv', dtype={'代码': str})


    def test_is_trade_enable(self):
        self.assertFalse(self.app.is_trade_enable())

    def test_get_user_id(self):
        self.assertEqual(self.app.get_user_id(), '5d905db9fc84d3224b0eb59c')

    def test_get_max_buy_count(self):
        self.assertEqual(self.app.get_max_buy_count(), 3)

    def test_get_buy_volume(self):
        self.assertEqual(self.app.get_buy_volume(10.13), 200)

    def test_run_no_trade(self):
        ydls = Ydls()
        self.app = App([ydls], config_file='config-test-no-trade.ini')
        res_list = []
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res = self.app.run(row_df, timeStr='09:46:00')
            if res['state'] != 'nodata':
                print(res)
                res_list.append(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]['state'], 'success')
        self.assertEqual(res_list[0]['message'], 'data match, no trade')
        self.assertEqual(res_list[0]['data'][0].name, '600239')
        self.app.close()

    def test_run_no_trade_multiple(self):
        ydls = Ydls()
        ydls_concept = YdlsConcept()
        self.app = App([ydls_concept], config_file='config-test-no-trade.ini')
        res_list = []
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res = self.app.run(row_df, timeStr='09:46:00')
            if res['state'] != 'nodata':
                print(res)
                res_list.append(res)
        self.assertEqual(len(res_list), 0)
        self.app.close()


    def test_run_no_trade_multiple(self):
        ydls = Ydls()
        ydls_concept = YdlsConcept()
        self.app = App([ydls, ydls_concept], config_file='config-test-no-trade.ini')
        res_list = []
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res = self.app.run(row_df, timeStr='09:46:00')
            if res['state'] != 'nodata':
                print(res)
                res_list.append(res)
        self.assertEqual(len(res_list), 1)
        self.assertEqual(res_list[0]['state'], 'success')
        self.assertEqual(res_list[0]['message'], 'data match, no trade')
        self.assertEqual(res_list[0]['data'][0].name, '600239')
        self.app.close()

    # def test_run_trade(self):
    #     ydls = Ydls()
    #     self.app = App([ydls], 'config-test-trade.ini')
    #     res_list = []
    #     for index, row in self.data.iterrows():
    #         row_df = pd.DataFrame([row])
    #         res = self.app.run(row_df, timeStr='09:46:00')
    #         if res['state'] != 'nodata':
    #             print(res)
    #             res_list.append(res)
    #     self.assertEqual(len(res_list), 1)
    #     self.assertEqual(len(self.app.get_success_order()), 1)
    #     self.assertEqual(self.app.get_success_order()[0], '300534')
    #     self.assertEqual(res_list[0]['state'], 'success')
    #     self.assertEqual(res_list[0]['message'], 'trade success')
    #     self.assertEqual(res_list[0]['data'][0], '300534')
    #     self.app.close()
        
if __name__ == '__main__':
    unittest.main()