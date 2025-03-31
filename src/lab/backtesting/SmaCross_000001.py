from backtesting import Backtest, Strategy
from backtesting.lib import crossover
import akshare as ak

from backtesting.test import SMA


class SmaCross(Strategy):
    n1 = 10
    n2 = 20

    def init(self):
        close = self.data.Close
        self.sma1 = self.I(SMA, close, self.n1)
        self.sma2 = self.I(SMA, close, self.n2)

    def next(self):
        if crossover(self.sma1, self.sma2):
            self.position.close()
            self.buy()
        elif crossover(self.sma2, self.sma1):
            self.position.close()
            self.sell()


data = ak.stock_zh_a_hist(symbol='000001', period='daily', start_date='20200101', end_date='20250330', adjust='qfq')
data.rename(columns={'开盘': 'Open', '最高' : 'High', '最低' : 'Low', '收盘' : 'Close'}, inplace=True)

print(data)
bt = Backtest(data, SmaCross,
              cash=10000, commission=.002,
              exclusive_orders=True)

output = bt.run()
# bt.plot()
# print(output)
output['_trades'].to_csv('./output/trades_output.csv', index=False)
