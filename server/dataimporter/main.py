import extractdata
import datetime
import logging
import sys
import argparse
from config.config import Config

#Configuration
conf = Config()

# Logging params
logging.basicConfig(filename='dataimporter.log',
                    format=conf.get_config('log_params','log_format'))

logging.warning("DataImporter started")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
    parser.add_argument('-c', '--coins', dest="coins", help='Get coin list from Cryptocompare and insert in BDD',
                        action='store_true')
    parser.add_argument('-p', '--prices', dest="prices", help='Insert current prices into BDD', action='store_true')
    parser.add_argument('-d', '--deleteMeaninglessCoins', dest="deleteMeaninglessCoins",
                        help='Delete coins and prices that are judged useless (market cap to low, no match between CMC & Cryptocompare names)',
                        action='store_true')
    parser.add_argument('-s', '--socialStats', dest="socialStats", help='Insert current prices into BDD',
                        action='store_true')
    parser.add_argument('-r', '--reddit', dest="reddit", help='Social stats from Redditmetric', action='store_true')
    parser.add_argument('-f', '--full', dest="full", help='Get everything (Useful for first-timer)',
                        action='store_true')
    parser.add_argument('-o', '--histoohlcv', dest="histoohlcv", help='Get historical OHLCV',
                        action='store_true')
    args = parser.parse_args()

    if (args.coins):
        # -----------------------------------------------
        # Get coin list from Cryptocompare and insert in BDD
        # -----------------------------------------------
        extractdata.extract_crytopcompare_coins()

    if (args.prices):
        # -----------------------------------------------
        # Insert current prices into BDD
        # -----------------------------------------------
        extractdata.extract_coinmarketcap_prices()

    if (args.deleteMeaninglessCoins):
        # -----------------------------------------------
        # Delete coins and prices that are judged useless (market cap to low, no match between CMC & Cryptocompare names)
        # -----------------------------------------------
        extractdata.remove_useless_prices_coins()
        extractdata.add_ids()
        extractdata.delete_excluded_coins()

    if (args.socialStats):
        # -----------------------------------------------
        # Social stats from Cryptocompare (replace with orginal website info post MVP ?)
        # -----------------------------------------------
        extractdata.extract_cryptocompare_social()

    if (args.reddit):
        # -----------------------------------------------
        # Social stats from Redditmetric
        # -----------------------------------------------
        extractdata.import_reddit_histo()

    if (args.histoohlcv):
        # -----------------------------------------------
        # Histo OHLCV
        # -----------------------------------------------
        extractdata.extract_histo_ohlcv()

    if (args.full):
        # -----------------------------------------------
        # Get everything (Useful for first-timer)
        # -----------------------------------------------
        extractdata.extract_crytopcompare_coins()
        extractdata.extract_coinmarketcap_prices()
        extractdata.remove_useless_prices_coins()
        extractdata.add_ids()
        extractdata.extract_cryptocompare_social()
        extractdata.import_reddit_histo()
        extractdata.extract_histo_ohlcv()

logging.warning("DataImporter ended")