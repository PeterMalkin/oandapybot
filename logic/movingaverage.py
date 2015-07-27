from logic.candle import Candle
from logic import Indicator

# Moving averages indicators
# This implementation is more computationally efficient
# it allows to update the value of average without
# running a loop over all the elements of the average.
# It uses the sliding window of PeriodCount to have
# a fixed number of data points to average

def GetDataPointValue(datapoint):
    result = {}

    if not datapoint:
        return result

    if (isinstance(datapoint, Candle)):
        result["value"] = float(datapoint.Close)

    try:
        if (not result):
            result["value"]= datapoint["value"]
    except:
        result = {}

    return result


# Base class for real indicators (SimpleMovingAverage, ExponentialMovingAverage)
class MovingAverage(Indicator):

    def __init__(self, period_count = 1):
        self.value = 0.0
        self.period_count = period_count
        self._data = []

    def DataPointsCount(self):
        return len(self._data)

    def AmountOfDataStillMissing(self):
        return max(0, self.period_count - len(self._data))

    def SeenEnoughData(self):
        return ( len(self._data) >= self.period_count )

    def Update(self, data):
        pass

# Moving average of a price over a period of time
class SimpleMovingAverage(MovingAverage):

    def __init__(self, period_count = 1):
        super(SimpleMovingAverage,self).__init__(period_count)

    def Update(self, d):

        data = GetDataPointValue(d)

        if (not data):
            return

        if ( len(self._data) >= self.period_count ):
            # Update current moving average, avoiding the loop over all datapoints
            self.value = self.value + ( data["value"] - self._data[0]["value"] ) / len(self._data)
            # Remove outdated datapoint from the storage
            self._data.pop(0)
        else:
            # Not enough data accumulated. Compute cumulative moving average
            self.value = self.value + (data["value"] - self.value) / ( len(self._data) + 1.0 )

        # Add the data point to the storage
        self._data.append(data)

# Moving average with exponential smoothing of a price over a period of time
class ExponentialMovingAverage(MovingAverage):

    def __init__(self, period_count = 1):
        super(ExponentialMovingAverage,self).__init__(period_count)

    def Update(self, d):

        data = GetDataPointValue(d)

        if (not data):
            return

        smoothing = 2.0 / (len(self._data) + 1.0)

        if ( len(self._data) >= self.period_count ):
            # Update current exponential moving average, avoiding the loop over all datapoints
            self.value = self.value + smoothing * ( data["value"] - self.value )
            # Remove outdated datapoint from the storage
            self._data.pop(0)
        else:
            # Not enough data accumulated. Compute cumulative moving average
            self.value = self.value + (data["value"] - self.value) / ( len(self._data) + 1.0 )

        # Add the data point to the storage
        self._data.append(data)
