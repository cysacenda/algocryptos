import sys
from datetime import datetime, timedelta
import logging
import argparse
from commons.config import Config
from commons.processmanager import ProcessManager
from sqlalchemy import create_engine
from commons.utils import utils
from commons.slack import slack
from ml.utils_ml import get_last_dates_per_trading_pair, calcul_signals_for_crypto, load_obj

from trading.trading_api_binance import TradingApiBinance
from trading.trading_module import TradingModule
from trading.trading_pair import TradingPair
from ml.preproc_prepare import PreprocPrepare

# region config / process manager / logging / sql connexion
# Configuration
conf = Config()

# Process manager
procM = ProcessManager()

# Logging params
today = datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(filename='algo_' + today + '.log',
                    format=conf.get_config('log_params', 'log_format'))

# If process can't start because other processes running
IdCurrentProcess = conf.get_config('process_params', 'algo_process_id')
if not procM.start_process(IdCurrentProcess, 'Algo', sys.argv):
    sys.exit(1)

# connection DB
connection = create_engine(utils.get_connection_string())
#endregion

try:
    if __name__ == '__main__':

        # region instanciate parser
        parser = argparse.ArgumentParser(
            description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
        parser.add_argument('-s', '--std', dest="std", help='Standard program',
                            action='store_true')
        args = parser.parse_args()
        #endregion

        if args.std:
            # -----------------------------------------------
            # Start program
            # -----------------------------------------------

            # region retrieve algo params
            pct_order_placed = float(conf.get_config('trading_module_params', 'pct_order_placed'))
            bet_size = float(conf.get_config('trading_module_params', 'bet_size'))
            min_bet_size = float(conf.get_config('trading_module_params', 'min_bet_size'))
            pct_order_placed = float(conf.get_config('trading_module_params', 'pct_order_placed'))
            nb_periods_to_hold_position = int(conf.get_config('trading_module_params', 'nb_periods_to_hold_position'))
            cash_asset = conf.get_config('trading_module_params', 'cash_asset')
            threshold = float(conf.get_config('trading_module_params', 'threshold'))
            trading_assets = conf.parse_config_dict(conf.get_config('trading_module_params', 'trading_assets_all'))
            date_to_retrieve_days_to_add = int(conf.get_config('data_params', 'date_to_retrieve_days_to_add'))
            model_file_name = conf.get_config('trading_module_params', 'model_file_name')
            useless_features_file_name = conf.get_config('trading_module_params', 'useless_features_file_name')
            model = load_obj(model_file_name)
            useless_features = load_obj(useless_features_file_name)
            # endregion Retrieve algo params

            # region build trading pairs / tresholds / signals for trading_module usage
            trading_pairs = {}
            thresholds = {}
            signals = {}
            dict_last_dates = {}
            for id_crypto, binance_symbol in trading_assets.items():
                trading_pair_str = binance_symbol + cash_asset
                trading_pair = TradingPair(trading_pair_str, binance_symbol, cash_asset)
                trading_pairs[trading_pair_str] = trading_pair
                thresholds[trading_pair_str] = threshold

                # filter to retrieve only needed data to calcul all features
                older_date = (datetime.now()
                              - timedelta(days=date_to_retrieve_days_to_add)).strftime("%Y-%m-%d")

                # retrieve data
                df_one_crypto = PreprocPrepare.get_global_dataset_for_crypto(connection, str(id_crypto), nb_periods_to_hold_position, older_date=older_date)
                df_one_crypto, X_close_prices = PreprocPrepare.get_preprocessed_data_inference(df_one_crypto,
                                                                                               do_scale=True,
                                                                                               do_pca=True,
                                                                                               useless_features=useless_features)

                # keep only last rows (number = nb_periods_to_hold_position)
                df_one_crypto = df_one_crypto.tail(nb_periods_to_hold_position)

                # get the last date of the dataset on which predictions are made for each trading pair
                dict_last_dates[trading_pair_str] = get_last_dates_per_trading_pair(df_one_crypto)

                # use model to calcul predictions
                signals[trading_pair_str] = calcul_signals_for_crypto(model, df_one_crypto)

            #endregion

            # trading api binance
            trading_api_binance = TradingApiBinance(pct_order_placed)

            # trading module
            trading_module = TradingModule(trading_api_binance, bet_size, min_bet_size,
                                           pct_order_placed, nb_periods_to_hold_position,
                                           trading_pairs, cash_asset, thresholds, False, is_simulation=True)

            # performs algo actions
            trading_module.do_update(datetime.now(), signals, dict_last_dates)

            # TODO V2 : contrôles de cohérence :
            # marché pas en pleine chute de ouf avec acceleration ?
            # STOP LOSS (après mise en prod pour tests) /!\
                # Look at orderTypes="STOP_LOSS_LIMIT"
                # Infos utiles:
                # https://api.binance.com/api/v1/exchangeInfo

# region exception management / exit
except Exception as e:
    procM.setIsError()
    msg = 'Uncatched error :' + str(e)
    logging.error(msg)
    slack.post_message_to_alert_error_trading(msg)


# Stop process
procM.stop_process(IdCurrentProcess, 'Algo', sys.argv)

exit(1 if procM.IsError else 0)
# endregion