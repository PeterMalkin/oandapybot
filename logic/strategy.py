import datetime
from exchange.oanda import Oanda
from logic.candle import Candle
from logic import movingaverage
from logic import MarketTrend
from logic.risk import RiskManager
from logic.timestop import TimeStop
import logging
import traceback

class Strategy(object):

    SHORT_EMA_PERIOD = 7
    LONG_EMA_PERIOD = 21
    
    def __init__(self, oanda, candle_size = 120, email = None, risk = 2):
        self._oanda = oanda
        self._oanda.SubscribeTicker(self)
        self._current_candle = None
        self._candle_size = candle_size
        self._risk = RiskManager(oanda, risk)
        self._email = email
        self._short_ema = movingaverage.ExponentialMovingAverage(Strategy.SHORT_EMA_PERIOD)
        self._long_ema = movingaverage.ExponentialMovingAverage(Strategy.LONG_EMA_PERIOD)
        self._timestop = TimeStop()
        self._logging_current_price = 0.0
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

    def PauseTrading(self):
        logging.info("Pausing strategy")
        self.trading_enabled = False

    def ResumeTrading(self):
        logging.info("Resuming strategy")
        self.trading_enabled = True

    def TradingStatus(self):
        return self.trading_enabled

    def SetTradingStatus(self, tstatus):
        self.trading_enabled = tstatus

    def Stop(self):
        logging.info("Stop strategy")
        self.SetTradingStatus(False)
        self._oanda.StopPriceStreaming()

    def Update(self, datapoint):

        if not isinstance(datapoint, Candle):
            if not self._current_candle:
                openTime = datapoint["now"]
                closeTime = datapoint["now"] + datetime.timedelta(minutes=self._candle_size)
                self._current_candle = Candle(openTime, closeTime)
            else:
                self._current_candle.Update(datapoint)
            self._logging_current_price = datapoint["value"]
        else:
            self._current_candle = datapoint
            self._logging_current_price = datapoint.Close

        # Check if it is Friday night and we should seize trading
        self._timestop.Update(datapoint)
        _state = self._timestop.GetState()
        if _state == MarketTrend.STOP_LONG or _state == MarketTrend.STOP_SHORT:
            if (self._oanda.CurrentPosition() > 0):
                logging.info("Timing Stop fired, TGIF!: "+str(_state) + " price: "+ str(self._logging_current_price))
                self.ClosePosition()
                return

        if not self._current_candle.SeenEnoughData():
            return

        self._short_ema.Update(self._current_candle)
        self._long_ema.Update(self._current_candle)

        self._current_candle = None

        if (self._short_ema.value > self._long_ema.value):
            if (self._oanda.CurrentPosition() > 0) and (self._oanda.CurrentPositionSide == MarketTrend.ENTER_LONG):
                return
            else:
                self.ClosePosition()
                self.Buy()
    
        if (self._long_ema.value > self._short_ema.value):
            if (self._oanda.CurrentPosition() > 0) and (self._oanda.CurrentPositionSide == MarketTrend.ENTER_SHORT):
                return
            else:
                self.ClosePosition()
                self.Sell()
                
    def Buy(self):
        
        logging.info("Strategy Buy() called. Going long @ " + str(self._logging_current_price))
        
        if not self.trading_enabled:
            logging.info("Strategy trading disabled, doing nothing")
            return
        
        # Enter the long position on the instrument
        units = self._risk.GetLongPositionSize()
        logging.info("Got the number of units to trade from RiskManager: "+str(units))
        if units == 0:
            logging.info("Cant trade zero units, doing nothing")
            return

        try:
            self._oanda.Buy(units)
        except Exception as e:
            self._catchTradeException(e,"enter long")
        
    def Sell(self):

        logging.info("Strategy Sell() called. Going short @ " + str(self._logging_current_price))
        if not self.trading_enabled:
            logging.info("Trading disabled, doing nothing")
            return

        # Enter the short position on the instrument
        units = self._risk.GetShortPositionSize()
        logging.info("Got the number of units to trade from RiskManager: "+str(units))
        if units == 0:
            logging.info("Cant trade 0 units, doing nothing")
            return

        try:
            self._oanda.Sell(units)
        except Exception as e:
            self._catchTradeException(e,"enter short")

    def ClosePosition(self):

        logging.info("Closing position, and all stops")        
        if not self.trading_enabled:
            logging.info("Trading disabled, doing nothing")
            return

        try:
            self._oanda.ClosePosition()
        except Exception as e:
            self._catchTradeException(e,"close")

    def GetStopLossPrice(self):
        return 0.0
        
    def GetTrailingStopPrice(self):
        return 0.0

    def _catchTradeException(self, e, position):
            logging.critical("Failed to "+position+" position")
            logging.critical(traceback.format_exc())
            if self._email:
                txt = "\n\nError while trying to "+position+" position\n"
                txt += "It was caught, I should still be running\n\n"
                txt += traceback.format_exc()+"\n"+str(e)
                self._email.Send(txt)
