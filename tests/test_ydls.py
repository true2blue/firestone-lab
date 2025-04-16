import unittest
import pandas as pd
from src.lab.strategies.Ydls import Ydls
from src.lab.strategies.YdlsConcept import YdlsConcept
import configparser

class TestApp(unittest.TestCase):
    
    def setUp(self):
        self.config = configparser.ConfigParser()
        self.config.read('./config/config-test-no-trade.ini', encoding='utf-8')
        self.ydls = Ydls(config=self.config)
        self.ydlsConcept = YdlsConcept(config=self.config)
        self.data = pd.read_csv('data/processed/601007-2025-04-16.csv', dtype={'代码': str})

    def test_is_in_time_range(self):
        self.assertTrue(self.ydls.is_in_time_range(timeStr='09:46:00'))
        self.assertTrue(self.ydls.is_in_time_range(timeStr='11:30:00'))
        self.assertFalse(self.ydls.is_in_time_range(timeStr='15:10:00'))
        
    def is_match_time(self, row, time):
        return row['时间'] == time
    
    def test_job(self):
        res_df = None
        status = False
        expected_time = None
        actual_time = None
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res_df, status = self.ydls.job(row_df)
            if self.is_match_time(row, '10:43:09'):
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

    # def test_job_concept(self):
    #     res_df = None
    #     status = False
    #     expected_time = None
    #     actual_time = None
    #     for index, row in self.data.iterrows():
    #         row_df = pd.DataFrame([row])
    #         res_df, status = self.ydls.job(row_df)
    #         if self.is_match_time(row, '09:46:33'):
    #             print('Expected')
    #             print(res_df)
    #             expected_time = res_df.iloc[0]['时间']
    #         if status:
    #             print('Actual')
    #             print(res_df)
    #             actual_time = res_df.iloc[0]['时间']
    #             break
    #     self.assertEqual(expected_time, actual_time)           
    #     self.assertTrue(status)

if __name__ == '__main__':
    unittest.main()