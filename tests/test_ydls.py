import unittest
import pandas as pd
from src.lab.strategies.Ydls import Ydls

class TestApp(unittest.TestCase):
    
    def setUp(self):
        self.ydls = Ydls(config_file='config-test-no-trade.ini')
        self.data = pd.read_csv('data/processed/600239-2025-03-28.csv', dtype={'代码': str})


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
        
    def is_match_time(self, row, time):
        return row['时间'] == time
    
    # def test_column_value_exists(self):
    #     df1 = pd.DataFrame({'A': [7]})
    #     df2 = pd.DataFrame({'B': [3, 4, 5, 6]})
    #     exists = df1[df1['A'].isin(df2['B'])]
    #     print(exists)

    def test_job(self):
        res_df = None
        status = False
        expected_time = None
        actual_time = None
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res_df, status = self.ydls.job(row_df)
            if self.is_match_time(row, '14:31:18'):
                print('Expected')
                print(res_df)
                expected_time = res_df.iloc[0]['时间']
            if status:
                print('Actual')
                print(res_df)
                actual_time = res_df.iloc[0]['时间']
                break
        self.assertEqual(expected_time, actual_time)           
        self.assertTrue(status)

if __name__ == '__main__':
    unittest.main()