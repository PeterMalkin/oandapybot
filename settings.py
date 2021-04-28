# Account settings
ACCOUNT_ID = "000-000-00000000-000"
ACCESS_TOKEN = "166acab065f0bd72c33aee2d02037829-00700707adc454f3a0e075cf0351aa8c"
ENVIRONMENT = "practice"

# Pair to trade.
# only one allowed for now - run multiple instances if you want multiple pairs
ACCOUNT_CURRENCY = "USD"
INSTRUMENT = "EUR_USD"

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
BACKTESTING_FILENAME = "data/EURUSD/DAT_ASCII_EURUSD_M1_2015.csv"
