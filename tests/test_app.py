import unittest
import pandas as pd
from datetime import datetime, timedelta
from src import app
import random

class TestApp(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up mock data for testing."""
        intervals = [1, 3, 5, 10, 20, 30, 60]
        app.setup_original_df(intervals)
        cls.sample_datas = []
        for idx in range(7):
            now = datetime.now() + timedelta(seconds=intervals[idx])
            sample_data = pd.DataFrame({
                'datetime': [now, now],
                '成交额': [random.randint(50000, 200000) for _ in range(2)],
                '涨跌幅': [round(random.uniform(1.0, 5.0), 2) for _ in range(2)],
                '振幅': [round(random.uniform(0.5, 3.0), 2) for _ in range(2)],
                '最新价': [round(random.uniform(10.0, 20.0), 2) for _ in range(2)],
                '最高': [round(random.uniform(10.5, 20.5), 2) for _ in range(2)],
                '代码': ['000001', '000002'],
                '名称': ['xx', 'bb']
            })
            sample_data.index = ['000001', '000002']  # Set stock codes as index
            cls.sample_datas.append(sample_data)


    def test_print_data(self):
        print(self.sample_datas)
    
    # def test_sampling(self):
    #     """Test the sampling function stores data correctly."""
    #     app.sampling(self.sample_data_1)
    #     print(app.orginal_df)
    #     self.assertIsNone(app.orginal_df['1']['data'])
    #     self.assertIsInstance(app.orginal_df['1']['last_sample_time'], datetime)

    # def test_get_sampling_data(self):
    #     """Test get_sampling_data returns correct data."""
    #     app.orginal_df['15']['data'] = self.sample_data
    #     result = app.get_sampling_data('15')
    #     self.assertIsInstance(result, pd.DataFrame)
    #     self.assertEqual(len(result), len(self.sample_data))

    # def test_get_average_amount(self):
    #     """Test get_average_amount calculation."""
    #     # Mock data for two intervals
    #     dataA = self.sample_data.copy()
    #     dataB = self.sample_data.copy()
    #     dataB['datetime'] = dataB['datetime'] + timedelta(seconds=15)

    #     # Store mock data in orginal_df
    #     app.orginal_df['15']['data'] = dataA
    #     app.orginal_df['30']['data'] = dataB

    #     # Test calculation
    #     result = app.get_average_amount('15', '30', 60)
    #     self.assertIsInstance(result, pd.Series)
    #     self.assertEqual(len(result), len(self.sample_data))

    # def test_get_average_amount_missing_data(self):
    #     """Test get_average_amount handles missing data."""
    #     app.orginal_df['15']['data'] = None
    #     app.orginal_df['30']['data'] = None
    #     result = app.get_average_amount('15', '30', 60)
    #     self.assertIsNone(result)

if __name__ == '__main__':
    unittest.main()