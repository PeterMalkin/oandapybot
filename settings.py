# Account settings
ACCOUNT_ID = "0070070"
ACCESS_TOKEN = "166acab665f0bd72c33aee2d02037829-00700707adc454f3a0e075cf0351aa8c"
ENVIRONMENT = "practice" # change this to "live" for production

# Pair to trade.
# only one allowed for now - run multiple instances if you want multiple pairs
ACCOUNT_CURRENCY = "USD"
INSTRUMENT = "EUR_USD"

# Home / Base exchange rate
# Examples: instrument: "USD_JPY", home: "USD", home/base: "USD_USD"
#           instrument: "EUR_USD", home: "USD", home/base: "EUR_USD"
#           instrument: "AUD_CAD", home: "USD", home/base: "USD_AUD"
HOME_BASE_CURRENCY_PAIR = "EUR_USD"
HOME_BASE_CURRENCY_PAIR_DEFAULT_EXCHANGE_RATE = 0.88

# Size of candles in minutes
CANDLES_MINUTES = 120

#Risk settings
MAX_PERCENTAGE_ACCOUNT_AT_RISK = 2 # NO more then 2% of account per trade

#Email credentials
EMAIL_RECIPIENT = "youremail@gmail.com"
EMAIL_FROM="oandabot@yourserver.com"
EMAIL_SERVER="mail.yourserver.com"
EMAIL_PORT=25
EMAIL_PASSWORD="SuchSecurePasswordStoredUnecrypted"

# Special bot name for identification
# In case you have many and want to distinguish between them 
# Leave default if only running one bot
BOT_NAME = "OANDAPYBOT"

# For backtesting
BACKTESTING_FILENAME = "backtest/data/EURUSD/DAT_ASCII_EURUSD_M1_2015.csv"
