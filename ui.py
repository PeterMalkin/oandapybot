import curses
import backtrader
import datetime
import os
import settings
import sys
import threading

class CursedUI(object):
    def __init__(self,store):
        self.store = store
        self._heartbeatTime = ""
        self._instrument = ""
        self._account_currency = ""
        self._position = ""
        self._pricing = ""
        self._cash = ""
        self._leverage = ""
        self._exiting = False


    def _update(self):
        self._instrument = str(self.store.get_instrument(settings.INSTRUMENT)['name'])
        self._account_currency = str(self.store.get_currency())
        self._position = str(self.store.get_positions())
        self._cash = str(self.store.get_value())
        self._leverage = str(self.store.get_leverage())

        _pricing = self.store.get_pricing(settings.INSTRUMENT)
        self._pricing = str(_pricing['bids'][0]['price'])+' bid, '+str(_pricing['asks'][0]['price'])+' ask' # str(_pricing['price'])
        self._heartbeatTime = str(datetime.datetime.fromtimestamp(float(_pricing['time'])))

    def start(self):

        # init curses
        self.stdscr = curses.initscr()
        curses.noecho()
        self.stdscr.keypad(1)
        self.stdscr.nodelay(1)

    def stop(self):
        if not self.stdscr:
            return

        # deinit curses
        self.stdscr.nodelay(0)
        self.stdscr.keypad(0)
        curses.echo()
        curses.endwin()
        self.store.stop()
        self._exiting = True

    def _threadfunc(self):
        while not self._exiting:
            self._update()
            self._render()
            self._userinput()
        self.stop()
        os._exit(0)


    def _userinput(self):
        c = self.stdscr.getch()

        # q - quit
        if c == ord('q'):
            self.stdscr.addstr(14,0,"(now: quitting)",curses.A_STANDOUT)
            self.stdscr.refresh()
            self._exiting = True

    def _render(self):
        self.stdscr.erase()
        self.stdscr.addstr(0,0,settings.BOT_NAME,curses.A_UNDERLINE)

        # Current account status
        self.stdscr.addstr(2,0,"Account currency:   "+self._account_currency)
        self.stdscr.addstr(3,0,"Trading instrument: "+self._instrument)

        # # Ticker and heartbeat
        self.stdscr.addstr(5,0,"Heartbeat: "+self._heartbeatTime)
        self.stdscr.addstr(6,0,"Ticker:    "+str(self._pricing))

        # # Account status
        self.stdscr.addstr(8, 0,"Position:        "+self._position)
        self.stdscr.addstr(11,0,"Cash:   "+self._cash)
        self.stdscr.addstr(12,0,"Leverage:       "+self._leverage)

        # Strategy status
        self.stdscr.addstr(13,0,"(Q)uit - exit")

        self.stdscr.refresh()

    def run(self):
        self.start()
        self._thread = threading.Thread(target=self._threadfunc)
        self._thread.start()
