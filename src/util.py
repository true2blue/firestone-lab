class Util(object):

    def calc_high_limit(pre_close):
        return round(pre_close * 1.1, 2)
    
    def calc_buy_voulme(price, amount):
        return (amount // price) // 100 * 100
