import extractdata
import logging
import argparse
from config.config import Config
from processmanager import ProcessManager
import sys

# Configuration
conf = Config()

# Process manager
procM = ProcessManager()

# Logging params
logging.basicConfig(filename='dataimporter.log',
                    format=conf.get_config('log_params', 'log_format'))

logging.warning("DataImporter started")

# If process can't start because other processes running
IdCurrentProcess = conf.get_config('process_params', 'data_importer_process_id')
if not procM.start_process(IdCurrentProcess, 'DataImporter', sys.argv):
    sys.exit(1)

try:
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(
            description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
        parser.add_argument('-c', '--coins', dest="coins", help='Get coin list from Cryptocompare and insert in BDD',
                            action='store_true')
        parser.add_argument('-p', '--prices', dest="prices", help='Insert current prices into BDD', action='store_true')
        parser.add_argument('-d', '--deleteMeaninglessCoins', dest="deleteMeaninglessCoins",
                            help='Delete coins and prices that are judged useless',
                            action='store_true')
        parser.add_argument('-s', '--socialStats', dest="socialStats", help='Insert current prices into BDD',
                            action='store_true')
        parser.add_argument('-r', '--reddit', dest="reddit", help='Social stats from Redditmetric', action='store_true')
        parser.add_argument('-f', '--full', dest="full", help='Get everything (Useful for first-timer)',
                            action='store_true')
        parser.add_argument('-o', '--histoohlcv', dest="histoohlcv", help='Get historical OHLCV',
                            action='store_true')
        parser.add_argument('-hp', '--histoprices', dest="histoprices",
                            help='Insert current prices into historical database', action='store_true')
        parser.add_argument('-ath', '--athprices', dest="athprices",
                            help='Insert ath prices into db', action='store_true')
        args = parser.parse_args()

        if args.coins:
            # -----------------------------------------------
            # Get coin list from Cryptocompare and insert in BDD
            # -----------------------------------------------
            extractdata.extract_crytopcompare_coins()

        if args.prices:
            # -----------------------------------------------
            # Get prices for coins from CoinMarketCap and insert in BDD
            # -----------------------------------------------
            extractdata.extract_coinmarketcap_prices()

        if args.deleteMeaninglessCoins:
            # -----------------------------------------------
            # Delete coins and prices that are judged useless (market cap to low, no match between CMC
            # & Cryptocompare names)
            # Add CryptoCompare Ids to prices (retrieved from CMC so without Ids)
            # -----------------------------------------------
            extractdata.remove_useless_prices_coins()
            extractdata.add_ids()
            extractdata.delete_excluded_coins()

        if args.socialStats:
            # -----------------------------------------------
            # Social infos & stats from Cryptocompare
            # -----------------------------------------------
            extractdata.extract_cryptocompare_social()

        if args.reddit:
            # -----------------------------------------------
            # Social stats from Redditmetric / reddit/subreddit/about.json
            # -----------------------------------------------
            extractdata.extract_reddit_data()

        if args.histoohlcv:
            # -----------------------------------------------
            # Histo OHLCV (V only for the moment)
            # -----------------------------------------------
            extractdata.extract_histo_ohlcv()

        if args.histoprices:
            # -----------------------------------------------
            # Get prices for coins from CoinMarketCap and insert in histo_prices
            # -----------------------------------------------
            extractdata.extract_coinmarketcap_historical_prices()

        if args.athprices:
            extractdata.extract_athindexes()

        if args.full:
            # -----------------------------------------------
            # Get everything (Useful for first-timer)
            # -----------------------------------------------
            extractdata.extract_crytopcompare_coins()
            extractdata.extract_coinmarketcap_prices()
            extractdata.remove_useless_prices_coins()
            extractdata.add_ids()
            extractdata.extract_cryptocompare_social()
            extractdata.extract_reddit_data()
            extractdata.extract_histo_ohlcv()

except Exception as e:
    logging.error('Uncatched error :' + str(e))

# Stop process
procM.stop_process(IdCurrentProcess)

logging.warning("DataImporter ended")
