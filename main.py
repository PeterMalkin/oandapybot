from settings import *
from util.mail import Email
from util.ui import CursedUI
from exchange.oanda import Oanda
from logic.strategy import Strategy
import traceback
import logging

logging.basicConfig(filename='oandabot.log',
                    level=logging.INFO,
                    format="%(asctime)-15s %(message)s"
                    )

email = Email( EMAIL_FROM,
               EMAIL_RECIPIENT,
               EMAIL_SERVER,
               EMAIL_PORT,
               EMAIL_PASSWORD,
               BOT_NAME
              )

oa = Oanda(ACCESS_TOKEN, ACCOUNT_ID, INSTRUMENT,ACCOUNT_CURRENCY,ENVIRONMENT)
strategy = Strategy(oa, CANDLES_MINUTES)
ui = CursedUI(oa, strategy, INSTRUMENT, ACCOUNT_CURRENCY)

def HandleExceptions():
    # Do proper curses deinit
    ui.Stop()
    
    traceback.print_exc()
    logging.critical(traceback.format_exc())
    
    # Attempt to close positions:
    try:
        oa.ClosePosition()
    except:
        pass
    
    # Email exception
    email.Send(str(e))

def Main():
    strategy.Start()
    ui.Start()

    # Main UI loop here
    while oa.IsRunning():
        ui.ProcessUserInput()
        if ui.IsExiting():
            break

    ui.Stop()
    strategy.Stop()

if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        HandleExceptions()
