import argparse
import backtest
import trade

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["backtest", "trade"])
    args = parser.parse_args()
    if args.action == "backtest":
        backtest.backtest()
    if args.action == "trade":
        trade.trade()


if __name__ == "__main__":
    main()
