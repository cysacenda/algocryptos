import datetime
import logging
from kpi_reddit import calcul_reddit_kpi
import argparse
import sys
from commons.config import Config
from commons.processmanager import ProcessManager

# Configuration
conf = Config()

# Process manager
procM = ProcessManager()

# Logging params
today = datetime.datetime.now().strftime("%Y-%m-%d")
logging.basicConfig(filename='algokpi_' + today + '.log',
                    format=conf.get_config('log_params', 'log_format'))

# If process can't start because other processes running
IdCurrentProcess = conf.get_config('process_params', 'algokpi_process_id')
if not procM.start_process(IdCurrentProcess, 'AlgoKPI', sys.argv):
    sys.exit(1)

try:
    if __name__ == '__main__':
        parser = argparse.ArgumentParser(
            description="Outil permettant l'analyse des donnees marches et reseaux sociaux pour les cryptocurrencies")
        parser.add_argument('-r', '--reddit', dest="reddit", help='Calcul KPIs related to Reddit',
                            action='store_true')
        args = parser.parse_args()

        if args.reddit:
            calcul_reddit_kpi.calcul_kpi_subscribers_trend()
except Exception as e:
    procM.isError()
    logging.error('Uncatched error :' + str(e))

# Stop process
procM.stop_process(IdCurrentProcess, 'AlgoKPI', sys.argv)
