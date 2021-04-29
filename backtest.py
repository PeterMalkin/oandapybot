import backtrader
import btplotting
import datetime
import importlib
import settings
import support

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

class KaiDataCSVData(backtrader.feeds.GenericCSVData):
    params = (
        ('nullvalue', float('NaN')),
        ('dtformat', 1),
        ('headers', True),
        ('time', -1),
        ('datetime', 0),
        ('open', 1),
        ('close', 2),
        ('high', 3),
        ('low', 4),
        ('volume', 5),
        ('openinterest', -1),
        ('reverse', True),
    )

def load_backtest_data():

    data = None

    if settings.BACKTESTING_FORMAT == "KAIDATA":
        data = KaiDataCSVData(
            dataname=settings.BACKTESTING_FILENAME,
            separator='\t',
            timeframe=backtrader.TimeFrame.Minutes,
            compression=60,
            fromdate=datetime.datetime(2010,1,1),
            todate=datetime.datetime(2010,12, 1))

    if settings.BACKTESTING_FORMAT == "HISTDATA":
        data = HistDataCSVData(
            dataname=settings.BACKTESTING_FILENAME,
            dtformat="%Y%m%d %H%M%S")

    return data


def strategy_class(class_name):
    module = importlib.import_module("strategy")
    class_ = getattr(module, class_name)
    return class_

def pretty_print(format, *args):
    print(format.format(*args))

def exists(object, *properties):
    for property in properties:
        if not property in object: return False
        object = object.get(property)
    return True

def addTradeAnalyzers(cerebro):
    cerebro.addanalyzer(backtrader.analyzers.TradeAnalyzer, _name='ta')
    cerebro.addanalyzer(backtrader.analyzers.DrawDown, _name='drawdown')
    cerebro.addanalyzer(backtrader.analyzers.SharpeRatio, _name='sharpe', riskfreerate=0.0, annualize=True,
                        timeframe=backtrader.TimeFrame.Minutes)
    cerebro.addanalyzer(backtrader.analyzers.VWR, _name='vwr')
    cerebro.addanalyzer(backtrader.analyzers.SQN, _name='sqn')
    cerebro.addanalyzer(backtrader.analyzers.Transactions, _name='txn')

def printTradeAnalysis(cerebro, startfund, analyzers):
    format = "  {:<24} : {:<24}"
    NA     = '-'

    print('Backtesting Results')
    if hasattr(analyzers, 'ta'):
        ta = analyzers.ta.get_analysis()

        openTotal         = ta.total.open          if exists(ta, 'total', 'open'  ) else None
        closedTotal       = ta.total.closed        if exists(ta, 'total', 'closed') else None
        wonTotal          = ta.won.total           if exists(ta, 'won',   'total' ) else None
        lostTotal         = ta.lost.total          if exists(ta, 'lost',  'total' ) else None

        streakWonLongest  = ta.streak.won.longest  if exists(ta, 'streak', 'won',  'longest') else None
        streakLostLongest = ta.streak.lost.longest if exists(ta, 'streak', 'lost', 'longest') else None

        pnlNetTotal       = ta.pnl.net.total       if exists(ta, 'pnl', 'net', 'total'  ) else None
        pnlNetAverage     = ta.pnl.net.average     if exists(ta, 'pnl', 'net', 'average') else None

        pretty_print(format, 'Open Positions', openTotal   or NA)
        pretty_print(format, 'Closed Trades',  closedTotal or NA)
        pretty_print(format, 'Winning Trades', wonTotal    or NA)
        pretty_print(format, 'Loosing Trades', lostTotal   or NA)
        print('\n')

        pretty_print(format, 'Longest Winning Streak',   streakWonLongest  or NA)
        pretty_print(format, 'Longest Loosing Streak',   streakLostLongest or NA)
        pretty_print(format, 'Strike Rate (Win/closed)', (wonTotal / closedTotal) * 100 if wonTotal and closedTotal else NA)
        print('\n')

        pretty_print(format, 'Inital Portfolio Value', '${}'.format(startfund))
        pretty_print(format, 'Final Portfolio Value', '${}'.format(cerebro.broker.getvalue()))
        pretty_print(format, 'Net P/L', '${}'.format(round(pnlNetTotal, 2)) if pnlNetTotal   else NA)
        pretty_print(format, 'P/L Average per trade', '${}'.format(round(pnlNetAverage, 2)) if pnlNetAverage else NA)
        print('\n')

    if hasattr(analyzers, 'drawdown'):
        pretty_print(format, 'Drawdown', '${}'.format(analyzers.drawdown.get_analysis()['drawdown']))
    if hasattr(analyzers, 'sharpe'):
        pretty_print(format, 'Sharpe Ratio:', analyzers.sharpe.get_analysis()['sharperatio'])
    if hasattr(analyzers, 'vwr'):
        pretty_print(format, 'VRW', analyzers.vwr.get_analysis()['vwr'])
    if hasattr(analyzers, 'sqn'):
        pretty_print(format, 'SQN', analyzers.sqn.get_analysis()['sqn'])
    print('\n')

    print('Transactions')
    format = "  {:<24} {:<24} {:<16} {:<8} {:<8} {:<16}"
    pretty_print(format, 'Date', 'Amount', 'Price', 'SID', 'Symbol', 'Value')
    for key, value in analyzers.txn.get_analysis().items():
        pretty_print(format, key.strftime("%Y/%m/%d %H:%M:%S"), value[0][0], value[0][1], value[0][2], value[0][3],
                     value[0][4])

                
def backtest():
    cerebro = backtrader.Cerebro()
    data = load_backtest_data()
    cerebro.adddata(data)
    cerebro.addstrategy(strategy_class(settings.STRATEGY_NAME))
    cerebro.addsizer(backtrader.sizers.percents_sizer.PercentSizer, percents = settings.MAX_PERCENTAGE_ACCOUNT_AT_RISK)
    cerebro.broker.setcommission(commission=0.001, leverage=50)
    addTradeAnalyzers(cerebro)
    results = cerebro.run()
    printTradeAnalysis(cerebro, 10000, results[0].analyzers)
    plotter = btplotting.BacktraderPlotting(style='bar')
    cerebro.plot(plotter)


if __name__ == "__main__":
    backtest()
