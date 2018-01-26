import logging
from config.config import Config
from kpi_reddit import calcul_reddit_kpi
import argparse
from processmanager import ProcessManager
import sys


# Configuration
conf = Config()

# Process manager
procM = ProcessManager()

# Logging params
logging.basicConfig(filename='algokpi.log',
                    format=conf.get_config('log_params','log_format'))

logging.warning("AlgoKPI Started")

# If process can't start because other processes running
IdCurrentProcess = conf.get_config('process_params', 'algokpi_process_id')
if(not procM.start_process(IdCurrentProcess, 'AlgoKPI')):
    sys.exit(1)

try:
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
        parser.add_argument('-r', '--reddit', dest="reddit", help='Calcul KPIs related to Reddit',
                            action='store_true')
        args = parser.parse_args()

        if (args.reddit):
            calcul_reddit_kpi.calcul_kpi_subscribers_trend()
except Exception as e:
    logging.error('Uncatched error :' + str(e))

# Stop process
procM.stop_process(IdCurrentProcess)

logging.warning("AlgoKPI ended")

