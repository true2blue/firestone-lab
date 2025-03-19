import unittest
import pandas as pd
from src.app import App

class TestApp(unittest.TestCase):
    
    def setUp(self):
        self.app = App()
        self.data = pd.read_csv('data/processed/600178-2025-03-19.csv', dtype={'代码': str})

    def test_job(self):
        res_df = None
        for index, row in self.data.iterrows():
            row_df = pd.DataFrame([row])
            res_df = self.app.job(row_df)
            if res_df is not None:
                print(res_df)                
                break
        self.assertIsNotNone(res_df)

if __name__ == '__main__':
    unittest.main()