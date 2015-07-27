import curses
from exchange.oanda import Oanda
from logic.strategy import Strategy 
from logic import ValidateDatapoint

class CursedUI(object):
    def __init__(self, oanda, strategy, instrument, account_currency):
        self._oanda = oanda
        self._strategy = strategy
        self._account_currency = account_currency
        self._instrument = instrument
        self.stdscr = None
        # The stats to show
        self._netWorth = ""
        self._balance = ""
        self._cashInvested = ""
        self._currentPosition = ""
        self._currentPositionSide = ""
        self._availableUnits = ""
        self._currentPrice = ""
        self._heartbeatTime = ""
        self._stoploss_price = ""
        self._trailingstop_price = ""
        self._is_exiting = False
        
    def Start(self):
        self._oanda.SubscribeHeartbeat(self)
        self._oanda.SubscribeTicker(self)
        self._oanda.SubscribeUpdates(self)
        
        # init curses
        self.stdscr = curses.initscr()
        curses.noecho()
        self.stdscr.keypad(1)

        self.Update(None)
        self.Render()
        
    def Stop(self):
        if not self.stdscr:
            return
        
        # deinit curses
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()

    def Update(self, datapoint):

        if not datapoint:
            # Pull balances and positions
            self._netWorth = self._oanda.GetNetWorth()
            self._balance = self._oanda.GetBalance()
            self._cashInvested = self._oanda.CashInvested()
            self._currentPosition = self._oanda.CurrentPosition()
            self._currentPositionSide = str(self._oanda.CurrentPositionSide())
            self._availableUnits = self._oanda.AvailableUnits()

        if ValidateDatapoint(datapoint):
            self._currentPrice = datapoint["value"]

        if self._isHeartbeatUpdate(datapoint):
            self._heartbeatTime = datapoint["time"] 

        self._stoploss_price = str(self._strategy.GetStopLossPrice())
        self._trailingstop_price = str(self._strategy.GetTrailingStopPrice())

        self.Render()

    def ProcessUserInput(self):
        c = self.stdscr.getch()

        # b - buy current instrument
        if c == ord('b'):
            self.stdscr.addstr(18,22,"(now: buying)",curses.A_STANDOUT)
            self.stdscr.refresh()
            tstatus = self._strategy.TradingStatus()
            self._strategy.Resume()
            self._strategy.Buy()
            self._strategy.SetTradingStatus(tstatus)
        
        # s - sell current instrument
        if c == ord('s'):
            self.stdscr.addstr(18,22,"(now: selling)",curses.A_STANDOUT)
            self.stdscr.refresh()
            tstatus = self._strategy.TradingStatus()
            self._strategy.Resume()
            self._strategy.Sell()
            self._strategy.SetTradingStatus(tstatus)
            
        # c - close open position
        if c == ord('c'):
            self.stdscr.addstr(18,22,"(now: closing positions)",curses.A_STANDOUT)
            self.stdscr.refresh()
            tstatus = self._strategy.TradingStatus()
            self._strategy.Resume()
            self._strategy.ClosePosition()
            self._strategy.SetTradingStatus(tstatus)
        
        # p - pause strategy
        if c == ord('p'):
            self.stdscr.addstr(18,22,"(now: pausing strategy)",curses.A_STANDOUT)
            self.stdscr.refresh()
            self._strategy.Pause()

        # r - resume strategy
        if c == ord('r'):
            self.stdscr.addstr(18,22,"(now: resuming strategy)",curses.A_STANDOUT)
            self.stdscr.refresh()
            self._strategy.Resume()

        # q - quit
        if c == ord('q'):
            self.stdscr.addstr(18,22,"(now: quitting)",curses.A_STANDOUT)
            self.stdscr.refresh()
            self._is_exiting = True
        
    def IsExiting(self):
        return self._is_exiting

    def _isHeartbeatUpdate(self, datapoint):
        if not datapoint:
            return False
        if "time" not in datapoint:
            return False
        return True

    def Render(self):
        self.stdscr.erase()
        self.stdscr.addstr(0,0,"OANDA bot",curses.A_UNDERLINE)

        # Current account status        
        self.stdscr.addstr(2,0,"Account currency:   "+self._account_currency)
        self.stdscr.addstr(3,0,"Trading instrument: "+self._instrument)
        
        # Ticker and heartbeat
        self.stdscr.addstr(5,0,"Heartbeat: "+self._heartbeatTime)
        self.stdscr.addstr(6,0,"Ticker:    "+str(self._currentPrice))

        # Account status
        self.stdscr.addstr(8, 0,"Position:        "+str(self._currentPosition) + " " + str(self._currentPositionSide))
        self.stdscr.addstr(9, 0,"Balance:         "+str(self._balance))
        self.stdscr.addstr(10,0,"Available units: "+str(self._availableUnits))
        self.stdscr.addstr(11,0,"Cash invested:   "+str(self._cashInvested))
        self.stdscr.addstr(12,0,"Net Worth:       "+str(self._netWorth))
        
        # Strategy status
        self.stdscr.addstr(14,0,"Stop Loss price:     "+str(self._stoploss_price))
        self.stdscr.addstr(15,0,"Trailing Stop price: "+str(self._trailingstop_price))
        if self._strategy.TradingStatus():
            status = "running"
        else:
            status = "paused" 
        self.stdscr.addstr(16,0,"Strategy status:     "+status)
        
        self.stdscr.addstr(18,0,"Available actions:", curses.A_UNDERLINE)
        if self._strategy.TradingStatus():
            command = "(P)ause - pause strategy. Disable trading, but keep tickers coming"
        else:
            command = "(R)esume - resume strategy. Reenable trading" 
        
        self.stdscr.addstr(19,0,command)
        self.stdscr.addstr(20,0,"(B)uy - take long position on instrument")
        self.stdscr.addstr(21,0,"(S)ell - take short position on instrument")
        self.stdscr.addstr(22,0,"(C)lose - close position on instrument")
        self.stdscr.addstr(23,0,"(Q)uit - exit")
        
        self.stdscr.refresh()