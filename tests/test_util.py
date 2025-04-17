import unittest
from src.lab.util import Util

class TestUtil(unittest.TestCase):

    def test_calc_high_limit(self):
        price = 13.4
        pre_close = 12.85
        expected = 13.60
        result = Util.calc_high_limit(price, pre_close)
        self.assertEqual(result, expected)
        price = 1
        pre_close = 1
        expected = 1.1
        result = Util.calc_high_limit(price, pre_close)
        self.assertEqual(result, expected)
        price = 0.9
        pre_close = 0.8
        expected = 0.88
        result = Util.calc_high_limit(price, pre_close)
        self.assertEqual(result, expected)

    def test_calc_buy_volume(self):
        price = 10.13
        amount = 3000
        expected = 200  # (1050 // 10) // 100 * 100 = 100
        result = Util.calc_buy_voulme(price, amount)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()