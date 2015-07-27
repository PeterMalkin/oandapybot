import sys
sys.path.append("..")
from settings import *
from exchange.oanda import Oanda
import unittest

class TestOanda(unittest.TestCase):
    def setUp(self):
        self.oa = Oanda(ACCESS_TOKEN, ACCOUNT_ID, INSTRUMENT,ACCOUNT_CURRENCY,ENVIRONMENT)
    
    def test_GetNetWorth(self):
        r = self.oa.GetNetWorth()
        self.assertGreaterEqual(r, 0.0)

    def test_GetBalance(self):
        r = self.oa.GetBalance()
        self.assertGreaterEqual(r, 0.0)

    def test_CashInvested(self):
        r = self.oa.CashInvested()
        self.assertGreaterEqual(r, 0.0)
    
    def test_CurrentPosition(self):
        r = self.oa.CurrentPosition()
        self.assertGreaterEqual(r, 0.0)

    def test_AvailableUnits(self):
        r = self.oa.AvailableUnits()
        print r
        self.assertGreaterEqual(r, 0)
        
    def test_GetCandles(self):
        number_of_last_candles_to_get = 10
        size_of_candles_in_minutes = 60
        candles = self.oa.GetCandles(number_of_last_candles_to_get, size_of_candles_in_minutes)
        self.assertEqual(len(candles), 10)
    
if __name__ == '__main__':
    unittest.main()