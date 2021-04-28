import backtrader
import btoandav20
import importlib
import settings
import traceback
import ui


def strategy_class(class_name):
    module = importlib.import_module("strategy")
    class_ = getattr(module, class_name)
    return class_


def handle_exception(e):
    # Email exception
    txt = "\n\n The bot " + settings.BOT_NAME + "is exiting \n\n"
    txt += traceback.format_exc()+"\n"+str(e)
    email.Send(txt)


def trade():

    storekwargs = dict(
        token=settings.ACCESS_TOKEN,
        account=settings.ACCOUNT_ID,
        practice=(settings.ENVIRONMENT == "practice"),
        notif_transactions=True,
        stream_timeout=10,
    )
    store = btoandav20.stores.OandaV20Store(**storekwargs)

    datakwargs = dict(
        timeframe=backtrader.TimeFrame.Minutes,
        compression=1,
        tz='America/Los_Angeles',
        backfill=True,
        backfill_start=True,
    )
    data = store.getdata(dataname=settings.INSTRUMENT, **datakwargs)

    data.resample(
        timeframe=backtrader.TimeFrame.Minutes,
        compression=settings.CANDLES_MINUTES)
    cerebro = backtrader.Cerebro()
    cerebro.adddata(data)
    cerebro.setbroker(store.getbroker())
    cerebro.addsizer(btoandav20.sizers.OandaV20RiskPercentSizer, percents = settings.MAX_PERCENTAGE_ACCOUNT_AT_RISK)
    cerebro.addstrategy(strategy_class(settings.STRATEGY_NAME))
    cursedui = ui.CursedUI(store)
    try:
        cursedui.run()
        cerebro.run()
    except Exception as e:
        handle_exception(e)
    finally:
        cursedui.stop()        

if __name__ == "__main__":
    trade()
