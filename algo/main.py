import sys
import datetime
import logging
import argparse
from commons.config import Config
from commons.processmanager import ProcessManager
from sqlalchemy import create_engine
from commons.utils import utils
from commons.slack import slack

from trading.trading_api_binance import TradingApiBinance
from trading.trading_module import TradingModule
from trading.trading_pair import TradingPair
from ml.preproc_prepare import PreprocPrepare

# Configuration
conf = Config()

# Process manager
procM = ProcessManager()

# Logging params
today = datetime.datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(filename='algo_' + today + '.log',
                    format=conf.get_config('log_params', 'log_format'))

# If process can't start because other processes running
IdCurrentProcess = conf.get_config('process_params', 'algo_process_id')
if not procM.start_process(IdCurrentProcess, 'Algo', sys.argv):
    sys.exit(1)

# connection DB
connection = create_engine(utils.get_connection_string())

try:
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(
            description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
        parser.add_argument('-s', '--std', dest="std", help='Standard program',
                            action='store_true')
        args = parser.parse_args()

        if args.std:
            # TODO : Check that no important traitement running ? last ohlcv just done ? Do it with process management
            # -----------------------------------------------
            # Start program
            # -----------------------------------------------

            # Retrieve algo params
            pct_order_placed = float(conf.get_config('trading_module_params', 'pct_order_placed'))
            bet_size = float(conf.get_config('trading_module_params', 'bet_size'))
            min_bet_size = float(conf.get_config('trading_module_params', 'min_bet_size'))
            pct_order_placed = float(conf.get_config('trading_module_params', 'pct_order_placed'))
            nb_periods_to_hold_position = int(conf.get_config('trading_module_params', 'nb_periods_to_hold_position'))
            cash_asset = conf.get_config('trading_module_params', 'cash_asset')
            threshold = float(conf.get_config('trading_module_params', 'threshold'))
            trading_assets = conf.parse_config_dict(conf.get_config('trading_module_params', 'trading_assets_simple'))
            date_to_retrieve_days_to_add = int(conf.get_config('data_params', 'date_to_retrieve_days_to_add'))

            # Build trading pairs / tresholds / signals for trading_module usage
            trading_pairs = {}
            thresholds = {}
            signals = {}
            for id_crypto, binance_symbol in trading_assets.items():
                trading_pair_str = binance_symbol + cash_asset
                trading_pair = TradingPair(trading_pair_str, binance_symbol, cash_asset)
                trading_pairs[trading_pair_str] = trading_pair
                thresholds[trading_pair_str] = threshold

                # Retrieve data
                older_date = (datetime.datetime.now()
                              - datetime.timedelta(days=date_to_retrieve_days_to_add)).strftime("%Y-%m-%d")
                df_one_crypto = PreprocPrepare.get_global_dataset_for_crypto(connection, str(id_crypto), older_date=older_date)
                df_one_crypto, X_close_prices = PreprocPrepare.get_preprocessed_data_inference(df_one_crypto,
                                                                                               do_scale=True,
                                                                                               do_pca=True,
                                                                                               useless_features=None)

                # TODO : En cours
                # Trick to be on same timezone as Db data (cryptocompare UTC date localized before inserting in DB)
                # import tzlocal
                # from datetime import datetime
                #
                # value = client.get_server_time()['serverTime'] / 1000
                # local_timezone = tzlocal.get_localzone()  # get pytz timezone
                # date_localized = datetime.fromtimestamp(value, local_timezone)
                # date_localized.astimezone(pytz.utc) 

                # TODO : filtre en amont (perfs)
                signals[trading_pair_str] = df_one_crypto

            # TODO : contrôles de cohérence :
                # marché pas en pleine chute de ouf avec acceleration
                # data signaux ok (pas de données manquantes)
                # data server ok vs data signaux ?
                # stop loss

            # trading api binance
            trading_api_binance = TradingApiBinance(pct_order_placed)

            # trading module
            trading_module = TradingModule(trading_api_binance, bet_size, min_bet_size,
                                           pct_order_placed, nb_periods_to_hold_position,
                                           trading_pairs, cash_asset, thresholds, False)

            # TODO : avec date (utile ?) et signaux sur dernières 24h (cf. param), cf. backtesting
            trading_module.do_update(key, signals)


except Exception as e:
    procM.setIsError()
    msg = 'Uncatched error :' + str(e)
    logging.error(msg)
    slack.post_message_to_alert_error_trading(msg)


# Stop process
procM.stop_process(IdCurrentProcess, 'Algo', sys.argv)

exit(1 if procM.IsError else 0)
