import unittest
from src.util import Util

class TestUtil(unittest.TestCase):

    def test_calc_high_limit(self):
        pre_close = 12.85
        expected = 14.14
        result = Util.calc_high_limit(pre_close)
        self.assertEqual(result, expected)

    def test_calc_buy_volume(self):
        price = 10.13
        amount = 3000
        expected = 200  # (1050 // 10) // 100 * 100 = 100
        result = Util.calc_buy_voulme(price, amount)
        self.assertEqual(result, expected)

if __name__ == '__main__':
    unittest.main()