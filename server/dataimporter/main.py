import extractdata
import datetime
import logging
import sys
from config.config import Config

#Configuration
conf = Config()

# Logging params
logging.basicConfig(filename=conf.get_config('log_params','log_file'),
                    format=conf.get_config('log_params','log_format'))

logging.warning("Started")

# ----------------------------------------------- 
# Get coin list from Cryptocompare and insert in BDD
# -----------------------------------------------

extractdata.extract_crytopcompare_coins()

# -----------------------------------------------
# Insert current prices into BDD
# -----------------------------------------------

extractdata.extract_coinmarketcap_prices()

# -----------------------------------------------
# Delete coins and prices that are judged useless (market cap to low, no match between CMC & Cryptocompare names)
# -----------------------------------------------

extractdata.remove_useless_prices_coins()
extractdata.add_ids()


# -----------------------------------------------
# Social stats from Cryptocompare (replace with orginal website info post MVP ?)
# -----------------------------------------------
extractdata.extract_cryptocompare_social()


# -----------------------------------------------
# Social stats from Redditmetric
# -----------------------------------------------
extractdata.import_Reddit_data()

# -----------------------------------------------
# Histo OHLCV
# -----------------------------------------------
#extractdata.extract_histo_ohlcv('BTC')

logging.warning("Stopped")

