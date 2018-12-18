import sys
import datetime
import logging
import argparse
from commons.config import Config
from commons.processmanager import ProcessManager

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

        if args.full:
            # Check that no important traitement running ? last ohlcv just done ? Do it with process management
            # -----------------------------------------------
            # Start program
            # -----------------------------------------------
            toto = 0


except Exception as e:
    procM.setIsError()
    logging.error('Uncatched error :' + str(e))

# Stop process
procM.stop_process(IdCurrentProcess, 'Algo', sys.argv)

exit(1 if procM.IsError else 0)
