import backtrader


class Strategy(backtrader.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.sma7 = backtrader.talib.SMA(self.data, timeperiod=7)
        self.sma21 = backtrader.talib.SMA(self.data, timeperiod=21)
    def next(self):
        if (self.sma7 > self.sma21):
            self.buy()
        if (self.sma7 < self.sma21):
            self.sell()
