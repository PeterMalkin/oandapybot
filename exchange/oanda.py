# wrapper around oanda's RESTful api
import datetime
import time
import threading
import Queue
from exchange import oandapy
from logic.candle import Candle 
from math import floor
from logic import MarketTrend

class OandaPriceStreamer(oandapy.Streamer):
    def __init__(self,environment,api_key,account_id,instrument):
        self._api_key = api_key
        self._account_id = account_id
        self._instrument = instrument
        oandapy.Streamer.__init__(self,environment=environment,access_token=api_key)
        self.ticker_subscribers = []
        self.heartbeat_subscribers = []
        self.updates_subscribers = []
        self.update_necessary = True
        self._queue = Queue.Queue()
        self._thread = threading.Thread(target=OandaPriceStreamer._start,
                                       args=(self,)
                                       )
        self._thread.setDaemon(True)

    def SubscribeTicker(self, obj):
        self.ticker_subscribers.append(obj)
        
    def SubscribeHeartbeat(self, obj):
        self.heartbeat_subscribers.append(obj)
        
    def SubscribeUpdates(self, obj):
        self.updates_subscribers.append(obj)
        
    def IsRunning(self):
        return self._thread.isAlive()
        
    def _start(self):
        self.start(accountId=self._account_id,instruments=self._instrument,ignore_heartbeat=False)
        
    def _stop(self):
        self.disconnect()
        
    def Start(self):
        self._thread.start()

    def Stop(self):
        self._stop()
        self._thread.join()

    def on_success(self, data):
        self._queue.put(data)

    def UpdateSubscribers(self):

        if self._queue.empty():
            return

        data = self._queue.get_nowait()

        if not data:
            return

        if self.update_necessary:
            for obj in self.updates_subscribers:
                obj.Update(None)
            self.update_necessary = False

        if "heartbeat" in data:
            for obj in self.heartbeat_subscribers:
                obj.Update(data["heartbeat"])
            return

        if "tick" not in data:
            return

        ask = float(data["tick"]["ask"])
        bid = float(data["tick"]["bid"])
        ts = time.mktime(time.strptime(data["tick"]["time"], '%Y-%m-%dT%H:%M:%S.%fZ')) 
        price = (ask + bid) / 2.0

        datapoint = {}
        datapoint["now"] = datetime.datetime.fromtimestamp(ts)
        datapoint["value"] = price
        for obj in self.ticker_subscribers:
            obj.Update(datapoint)

        return True


class Oanda(object):
    def __init__(self, api_key, account_id, instrument, account_currency, environment="practice"):
        self._api_key = api_key
        self._account_id = account_id
        self._instrument = instrument
        self._account_currency = account_currency
        self._oanda = oandapy.API(environment=environment,access_token=self._api_key)
        self._oanda_price_streamer = OandaPriceStreamer(environment=environment,
                                                        api_key=self._api_key,
                                                        account_id=account_id,
                                                        instrument=instrument
                                                        )

    def SubscribeTicker(self, obj):
        self._oanda_price_streamer.SubscribeTicker(obj)
        
    def SubscribeHeartbeat(self, obj):
        self._oanda_price_streamer.SubscribeHeartbeat(obj)
        
    def SubscribeUpdates(self, obj):
        self._oanda_price_streamer.SubscribeUpdates(obj)
        
    def StartPriceStreaming(self):
        self._oanda_price_streamer.Start()

    def StopPriceStreaming(self):
        self._oanda_price_streamer.Stop()

    def GetNetWorth(self):
        response = self._oanda.get_account(self._account_id)
        return float(response["balance"])

    def ClosePosition(self):
        self._oanda.close_position(self._account_id, instrument=self._instrument)
        self._oanda_price_streamer.update_necessary = True

    def GetBalance(self):
        retValue = {}
        netWorth = self.GetNetWorth()
        retValue[self._account_currency] = netWorth
        response = self._oanda.get_positions(self._account_id)

        if not response or not response["positions"]:
            return retValue

        for item in response["positions"]:
            retValue[item["instrument"]] = float(item["units"])

        return retValue

    def CashInvested(self):
        response = self._oanda.get_positions(self._account_id)
        if not response or not response["positions"]:
            return 0.0

        cash = 0.0
        for item in response["positions"]:
            cash += float(item["units"]) * float(item["avgPrice"])

        return cash

    def CurrentPosition(self):
        try:
            response = self._oanda.get_position(self._account_id, self._instrument)
            return int(response["units"])
        except:
            return 0
        
    def CurrentPositionSide(self):
        try:
            response = self._oanda.get_position(self._account_id, self._instrument)
            if response["side"] == "sell":
                return MarketTrend.ENTER_SHORT
            if response["side"] == "buy":
                return MarketTrend.ENTER_LONG
        except:
            return MarketTrend.NONE

    def AvailableUnits(self):
        response = self._oanda.get_account(self._account_id)
        response["balance"]
        margin_available = response["marginAvail"]
        margin_rate = response["marginRate"]
        response = self._oanda.get_prices(instruments=self._instrument)
        exchange_rate = ( float(response["prices"][0]["ask"]) + float(response["prices"][0]["bid"]) ) / 2.0
        return int(floor( margin_available * margin_rate / exchange_rate )) 

    def Sell(self, units):       
        self._oanda.create_order(self._account_id,
                                 instrument=self._instrument,
                                 units=units,
                                 side='sell',
                                 type='market'
                                )
        self._oanda_price_streamer.update_necessary = True

    def Buy(self, units):
        self._oanda.create_order(self._account_id,
                                 instrument=self._instrument,
                                 units=units,
                                 side='buy',
                                 type='market'
                                )
        self._oanda_price_streamer.update_necessary = True
        
    def GetCandles(self, number_of_last_candles_to_get = 0, size_of_candles_in_minutes = 120):
        Candles = []

        if number_of_last_candles_to_get <= 0 or size_of_candles_in_minutes <= 0:
            return Candles

        _granularity = self._getGranularity(size_of_candles_in_minutes)
        response = self._oanda.get_history(instrument=self._instrument,
                                granularity=_granularity,
                                count=number_of_last_candles_to_get + 1,
                                candleFormat="midpoint"
                                )

        if not response.has_key("candles"):
            return Candles

        for item in response["candles"]:
            if item["complete"] != True:
                continue

            close_ts = datetime.datetime.fromtimestamp(
                        time.mktime(time.strptime(str(item['time']), '%Y-%m-%dT%H:%M:%S.%fZ')))
            open_ts = close_ts - datetime.timedelta(minutes = size_of_candles_in_minutes)

            c = Candle(open_ts, close_ts)
            c.Open  = item["openMid"]
            c.High  = item["highMid"]
            c.Low   = item["lowMid"]
            c.Close = item["closeMid"]
            c._is_closed = True
            Candles.append(c)

        self._oanda_price_streamer.update_necessary = True

        return sorted(Candles, key = lambda candle: candle.CloseTime)

    def IsRunning(self):
        return self._oanda_price_streamer.IsRunning()

    def UpdateSubscribers(self):
        self._oanda_price_streamer.UpdateSubscribers()

    # Dont care about candles that are smaller then one minute
    # Only a few supported. See details here:
    # http://developer.oanda.com/rest-live/rates/#retrieveInstrumentHistory
    def _getGranularity(self, size_in_minutes):
        if size_in_minutes == 2:
            return "M2"
        elif size_in_minutes == 3:
            return "M3"
        elif size_in_minutes == 4:
            return "M4"
        elif size_in_minutes == 5:
            return "M5"
        elif size_in_minutes == 10:
            return "M10"
        elif size_in_minutes == 15:
            return "M15"
        elif size_in_minutes == 30:
            return "M30"
        elif size_in_minutes == 60:
            return "H1"
        elif size_in_minutes == 120:
            return "H2"
        elif size_in_minutes == 240:
            return "H4"
        elif size_in_minutes == 480:
            return "H8"
        elif size_in_minutes == 1440:
            return "D1"
        # default: two hour candles
        return "H2"