import datetime
from logic import MarketTrend
from logic import Indicator
from logic.candle import Candle

# Sets its state to STOP if the datapoint's time is in a specified range
class TimeStop(Indicator):
    def __init__(self):
        self._state = MarketTrend.NO_STOP
        
    def GetState(self):
        return self._state
    
    # Declare a stop if it's Friday, between 8:40PM and 8:45PM
    def TickerUpdate(self, datapoint):
        if not datapoint:
            return

        try:
            if "now" not in datapoint:
                return
        except:
            return

        dt = datapoint["now"]

        if not isinstance(dt, datetime.datetime):
            return

        self._state = MarketTrend.NO_STOP

        if ( dt.weekday() != 4 ):
            return

        if ( dt.hour != 20 ):
            return

        if ( dt.minute > 45 ):
            return

        if ( dt.minute < 40 ):
            return

        self._state = MarketTrend.STOP_LONG

    def Update(self, datapoint):

        if not isinstance(datapoint, Candle):
            self.TickerUpdate(datapoint)
            return
