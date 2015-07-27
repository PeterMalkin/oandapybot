import datetime
from exchange.oanda import Oanda
from logic.candle import Candle
from logic import movingaverage
from logic import MarketTrend
from logic.risk import RiskManager
import logging


class Strategy(object):

    SHORT_EMA_PERIOD = 7
    LONG_EMA_PERIOD = 21
    
    def __init__(self, oanda, candle_size = 120):
        self._oanda = oanda
        self._oanda.SubscribeTicker(self)
        self._current_candle = None
        self._candle_size = candle_size
        self._risk = RiskManager(oanda)
        self._short_ema = movingaverage.ExponentialMovingAverage(Strategy.SHORT_EMA_PERIOD)
        self._long_ema = movingaverage.ExponentialMovingAverage(Strategy.LONG_EMA_PERIOD)
        self.trading_enabled = False

    def Start(self):
        logging.info("Starting strategy")
        # Prefeed the strategy with historic candles
        candle_count = self._long_ema.AmountOfDataStillMissing() + 1
        Candles = self._oanda.GetCandles(candle_count, self._candle_size)
        for c in Candles:
            self._short_ema.Update(c)
            self._long_ema.Update(c)
        self._oanda.StartPriceStreaming()
        self.trading_enabled = True

    def Pause(self):
        logging.info("Pausing strategy")
        self.trading_enabled = False
        
    def Resume(self):
        logging.info("Resuming strategy")
        self.trading_enabled = True
        
    def TradingStatus(self):
        return self.trading_enabled
    
    def SetTradingStatus(self, tstatus):
        self.trading_enabled = tstatus

    def Stop(self):
        logging.info("Stop strategy")
        self.Pause()
        self._oanda.StopPriceStreaming()

    def Update(self, datapoint):

        logging.info("Strategy update. Got datapoint: "+str(datapoint))

        if not isinstance(datapoint, Candle):
            if not self._current_candle:
                openTime = datapoint["now"]
                closeTime = datapoint["now"] + datetime.timedelta(minutes=self._candle_size)
                self._current_candle = Candle(openTime, closeTime)
            else:
                self._current_candle.Update(datapoint)
        else:
            self._current_candle = datapoint

        if not self._current_candle.SeenEnoughData():
            return

        logging.info("Feeding candle to Thanasis: "+self._current_candle.__dict__)

        self._short_ema.Update(self._current_candle)
        self._long_ema.Update(self._current_candle)

        self._current_candle = None

        if (self._short_ema.value > self._long_ema.value):
            if (self._oanda.CurrentPosition() > 0) and (self._oanda.CurentPositionSide == MarketTrend.ENTER_LONG):
                return
            else:
                self.ClosePosition()
                self.Buy()
    
        if (self._long_ema.value > self._short_ema.value):
            if (self._oanda.CurrentPosition() > 0) and (self._oanda.CurentPositionSide == MarketTrend.ENTER_SHORT):
                return
            else:
                self.ClosePosition()
                self.Sell()
                
    def Buy(self):
        
        logging.info("Strategy Buy() called. Going long")
        
        if not self.trading_enabled:
            logging.info("Strategy trading disabled, doing nothing")
            return
        
        # Enter the long position on the instrument
        units = self._risk.GetLongPositionSize()
        logging.info("Got the number of units to trade from RiskManager: "+str(units))
        if units == 0:
            logging.info("Cant trade zero units, doing nothing")
            return

        self._oanda.Buy(units)
        
    def Sell(self):

        logging.info("Strategy Sell() called. Going short")
        if not self.trading_enabled:
            logging.info("Trading disabled, doing nothing")
            return
        
        # Enter the short position on the instrument
        units = self._risk.GetShortPositionSize()
        logging.info("Got the number of units to trade from RiskManager: "+str(units))
        if units == 0:
            logging.info("Cant trade 0 units, doing nothing")
            return

        self._oanda.Sell(units)
        
    def ClosePosition(self):

        logging.info("Closing position, and all stops")        
        if not self.trading_enabled:
            logging.info("Trading disabled, doing nothing")
            return
        
        self._oanda.ClosePosition()
        
    def GetStopLossPrice(self):
        return 0.0
        
    def GetTrailingStopPrice(self):
        return 0.0