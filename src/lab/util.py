class Util(object):

    def calc_high_limit(price, pre_close):
        high_limit = round(pre_close * 1.1, 2)
        two_pecent_a_limit = round(price * 1.015, 2)
        two_pecent_b_limit = round(price + 10 * 0.01, 2)
        temp = two_pecent_a_limit if two_pecent_a_limit > two_pecent_b_limit else two_pecent_b_limit
        return temp if temp < high_limit else high_limit

    def calc_buy_voulme(price, amount):
        return (amount // price) // 100 * 100
