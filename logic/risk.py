from exchange.oanda import Oanda
from math import floor

class RiskManager(object):
    def __init__(self, oanda, account_percent_at_risk = 2):
        self._oanda = oanda
        self._risk = account_percent_at_risk / 100.0

    def GetShortPositionSize(self):
        # This is just hardcoded percentage, experts suggest no more then 0.02
        return max(0,int(floor(self._oanda.AvailableUnits() * self._risk)))

    def GetLongPositionSize(self):
        # This is just hardcoded percentage, experts suggest no more then 0.02
        return max(0,int(floor(self._oanda.AvailableUnits() * self._risk)))
