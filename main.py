from settings import *
from util.mail import Email
from util.ui import CursedUI
from exchange.oanda import Oanda
from exchange.oanda import OandaExceptionCode
from logic.strategy import Strategy
import traceback
import logging
import sys

logging.basicConfig(filename='oandabot.log',
                    level=logging.INFO,
                    format="%(asctime)-15s %(message)s"
                    )

email = Email(EMAIL_FROM,
              EMAIL_RECIPIENT,
              EMAIL_SERVER,
              EMAIL_PORT,
              EMAIL_PASSWORD,
              BOT_NAME)

oa = Oanda(ACCESS_TOKEN,
           ACCOUNT_ID,
           INSTRUMENT,
           ACCOUNT_CURRENCY,
           HOME_BASE_CURRENCY_PAIR,
           HOME_BASE_CURRENCY_PAIR_DEFAULT_EXCHANGE_RATE,
           ENVIRONMENT)

strategy = Strategy(oa,
                    CANDLES_MINUTES,
                    email=email,
                    risk=MAX_PERCENTAGE_ACCOUNT_AT_RISK)

ui = CursedUI(oa, strategy, INSTRUMENT, ACCOUNT_CURRENCY)

def HandleExceptions(e):
    # Do proper curses deinit
    ui.Stop()

    traceback.print_exc()
    logging.critical(traceback.format_exc())

    # Email exception
    txt = "\n\n The bot is exiting \n\n"
    txt += traceback.format_exc()+"\n"+str(e)
    email.Send(txt)

    # Attempt to close positions:
    try:
        strategy.Stop()
    except:
        pass

    # Return exit code
    retCode = OandaExceptionCode(e)
    sys.exit(retCode)

def Main():
    strategy.Start()
    ui.Start()

    # Main UI loop here
    while oa.IsRunning():
        oa.UpdateSubscribers()
        ui.ProcessUserInput()
        if ui.IsExiting():
            break

    ui.Stop()
    try:
        strategy.Stop()
    except:
        pass
    sys.exit(0)

if __name__ == "__main__":
    try:
        Main()
    except Exception as e:
        HandleExceptions(e)
