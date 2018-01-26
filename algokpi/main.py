import logging
from config.config import Config
from kpi_reddit import calcul_reddit_kpi
import argparse

#Configuration
conf = Config()

# Logging params
logging.basicConfig(filename='algokpi.log',
                    format=conf.get_config('log_params','log_format'))

logging.warning("Started")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Outil permettant l'analyse des données marchés et réseaux sociaux pour les cryptocurrencies")
    parser.add_argument('-r', '--reddit', dest="reddit", help='Calcul KPIs related to Reddit',
                        action='store_true')
    args = parser.parse_args()

    if (args.reddit):
        calcul_reddit_kpi.calcul_kpi_subscribers_trend()

logging.warning("Stopped")

