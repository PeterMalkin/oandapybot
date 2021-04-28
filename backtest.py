import backtrader
import importlib
import settings


class HistDataCSVData(backtrader.feeds.GenericCSVData):
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', 1),
        ('headers', False),
        ('time', -1),
        ('datetime', 0),
        ('open', 1),
        ('close', 2),
        ('high', 3),
        ('low', 4),
        ('volume', 5),
        ('openinterest', -1),
        ('reverse', True),
        ('separator', ';'),
    )


def strategy_class(class_name):
    module = importlib.import_module("strategy")
    class_ = getattr(module, class_name)
    return class_
                
def backtest():
    cerebro = backtrader.Cerebro()
    data = HistDataCSVData(dataname=settings.BACKTESTING_FILENAME,dtformat="%Y%m%d %H%M%S")
    cerebro.adddata(data)
    cerebro.addstrategy(strategy_class(settings.STRATEGY_NAME))
    cerebro.broker.setcommission(commission=0.001)
    cerebro.run()
    cerebro.plot()


if __name__ == "__main__":
    backtest()
