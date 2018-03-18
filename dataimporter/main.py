import sys
import datetime
import extractdata
import logging
import argparse
from commons.config import Config
from commons.processmanager import ProcessManager
from commons.s3bucket import s3bucket
from commons.utils import utils

# Configuration
conf = Config()

# Process manager
procM = ProcessManager()


# Logging params
today = datetime.datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(filename='dataimporter_' + today + '.log',
                    format=conf.get_config('log_params', 'log_format'))

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
        parser.add_argument('-s', '--socialStats', dest="socialStats", help='Insert infos related to social network (reddit, etc.) into BDD',
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
        parser.add_argument('-gt', '--googletrend', dest="googletrend",
                            help='Extract information from google trend', action='store_true')
        parser.add_argument('-img', '--images', dest="images",
                            help='Generate images from prices / volumes infos', action='store_true')
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
            extractdata.extract_cmc_global_data()

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
            extractdata.extract_lower_higher_prices()

        if args.googletrend:
            # -----------------------------------------------
            # Get information from google trend
            # -----------------------------------------------
            extractdata.extract_google_trend_info()

        if args.images:
            # -----------------------------------------------
            # Generate images from prices and volumes (7d)
            # -----------------------------------------------
            extractdata.generate_images_prices_volumes()

            # -----------------------------------------------
            # Upload on S3 bucket (Angular directory)
            # -----------------------------------------------
            local_generated_images_path = utils.get_path_for_system(conf.get_config('s3_bucket', 'local_generated_images_path_linux'), conf.get_config('s3_bucket', 'local_generated_images_path'))
            s3_dest_path = conf.get_config('s3_bucket', 'assets_path')
            s3bucket.transfer_folder_content_to_s3(utils.get_slash_for_system() + local_generated_images_path, s3_dest_path)

        if args.full:
            # -----------------------------------------------
            # Get everything (Useful for first-timer = virgins)
            # -----------------------------------------------
            extractdata.extract_crytopcompare_coins()
            extractdata.extract_coinmarketcap_prices()
            extractdata.remove_useless_prices_coins()
            extractdata.add_ids()
            extractdata.extract_cryptocompare_social()
            extractdata.extract_reddit_data()
            extractdata.extract_histo_ohlcv()
            extractdata.extract_lower_higher_prices()

except Exception as e:
    procM.setIsError()
    logging.error('Uncatched error :' + str(e))

# Stop process
procM.stop_process(IdCurrentProcess, 'DataImporter', sys.argv)

exit(1 if procM.IsError else 0)
