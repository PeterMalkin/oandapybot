from backtest.oanda_backtest import OandaBacktest
from logic.strategy import Strategy
from settings import *
from util.plot import StrategyPlot

def PlotResults(plotData):
    if not plotData:
        return
    splot = StrategyPlot(plotData, 2)
    splot.Plot("RawPrice",1, "r-")
    splot.Plot("Sell", 1, "ro")
    splot.Plot("Buy", 1, "g^")
    splot.Plot("Close", 1, "b*")
    splot.Plot("StopLoss", 1, "y-")
    splot.Plot("TrailingStop", 1, "y-")
    splot.Plot("NetWorth", 2, "r-")
    splot.Show()

def Main():

    oanda_backtest = OandaBacktest(BACKTESTING_FILENAME)
    
    strategy = Strategy(oanda_backtest,
                        CANDLES_MINUTES,
                        email=None,
                        risk=MAX_PERCENTAGE_ACCOUNT_AT_RISK)

    strategy.Start()

    while oanda_backtest.IsRunning():
        oanda_backtest.UpdateSubscribers()

    plotData = oanda_backtest.GetPlotData()
    PlotResults(plotData)

if __name__ == "__main__":
    Main()
