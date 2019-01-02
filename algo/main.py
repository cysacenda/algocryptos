import sys
import datetime
import logging
import argparse
from commons.config import Config
from commons.processmanager import ProcessManager
from commons.slack import slack

from trading.trading_api_binance import TradingApiBinance
from trading.trading_module import TradingModule

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

try:
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(
            description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
        parser.add_argument('-s', '--std', dest="std", help='Standard program',
                            action='store_true')
        args = parser.parse_args()

        if args.std:
            # Check that no important traitement running ? last ohlcv just done ? Do it with process management
            # -----------------------------------------------
            # Start program
            # -----------------------------------------------

            # Algo params
            pct_order_placed = float(conf.get_config('trading_module_params', 'pct_order_placed'))
            bet_size = float(conf.get_config('trading_module_params', 'bet_size'))
            min_bet_size = float(conf.get_config('trading_module_params', 'min_bet_size'))
            pct_order_placed = float(conf.get_config('trading_module_params', 'pct_order_placed'))
            nb_periods_to_hold_position = float(conf.get_config('trading_module_params', 'nb_periods_to_hold_position'))
            cash_asset = float(conf.get_config('trading_module_params', 'cash_asset'))

            # TODO : trading pairs (cf. backtesting)

            # TODO : tresholds (cf. backtesting)

            # TODO : contrôles de cohérence :
                # marché pas en pleine chute de ouf avec acceleration
                # data signaux ok (pas de données manquantes)
                # data server ok vs data signaux ?

            # trading api binance
            trading_api_binance = TradingApiBinance(pct_order_placed)

            # trading module
            trading_module = TradingModule(trading_api_binance, bet_size, min_bet_size,
                                           pct_order_placed, nb_periods_to_hold_position,
                                                self.trading_pairs, cash_asset, self.thresholds, False)

            # TODO : avec date (utile ?) et signaux sur dernirèes 24h (cf. param), cf. backtesting
            trading_module.do_update(key, signals)


except Exception as e:
    procM.setIsError()
    msg = 'Uncatched error :' + str(e)
    logging.error(msg)
    slack.post_message_to_alert_error_trading(msg)


# Stop process
procM.stop_process(IdCurrentProcess, 'Algo', sys.argv)

exit(1 if procM.IsError else 0)
