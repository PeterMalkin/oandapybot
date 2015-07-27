from exchange.oanda import Oanda
from math import floor

class RiskManager(object):
    def __init__(self, oanda):
        self._oanda = oanda

    def GetShortPositionSize(self):
        # This is just hardcoded percentage, experts suggest no more then 0.02
        return max(0,int(floor(self._oanda.AvailableUnits() * 0.2)))

    def GetLongPositionSize(self):
        # This is just hardcoded percentage, experts suggest no more then 0.02
        return max(0,int(floor(self._oanda.AvailableUnits() * 0.2)))
