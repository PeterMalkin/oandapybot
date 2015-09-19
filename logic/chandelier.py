import numpy
import talib
from logic import MarketTrend
from logic import Indicator
from logic.candle import Candle

class ChandelierExit(Indicator):
    def __init__(self):
        super(ChandelierExit,self).__init__()
        self.enter_period = 22
        self.C1 = 0.0
        self.C2 = 0.0
        self._high = []
        self._low = []
        self._close = []
        self.trend = MarketTrend.NONE

    def Update(self, datapoint):

        if not isinstance(datapoint, Candle):
            return

        # append data to storage
        self._high.append(datapoint.High)
        self._low.append(datapoint.Low)
        self._close.append(datapoint.Close)

        if (len(self._high) > self.enter_period):
            self._high.pop(0)
            self._low.pop(0)
            self._close.pop(0)

        # find H and L enter_period max and min
        Pmax = max(self._high)
        Pmin = min(self._low)

        # calculate enter_period Average True Range
        ATR = talib.ATR(numpy.array(self._high), numpy.array(self._low), numpy.array(self._close), timeperiod=self.enter_period)[-1]

        # Chandelier's Exit
        self.C1 = Pmax - 3.0 * ATR
        self.C2 = Pmin + 3.0 * ATR

        self.trend = MarketTrend.NONE

        if (self.C1 > datapoint.Close):
            self.trend = MarketTrend.EXIT_LONG

        if (self.C2 < datapoint.Close):
            self.trend = MarketTrend.EXIT_SHORT

    def AmountOfDataStillMissing(self):
        return max(0, self.enter_period - len(self._high))

    def SeenEnoughData(self):
        return (self.AmountOfDataStillMissing == 0)
