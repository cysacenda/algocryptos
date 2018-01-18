import logging
from config.config import Config
from kpi_reddit import calcul_reddit_kpi

#Configuration
conf = Config()

# Logging params
logging.basicConfig(filename='algokpi.log',
                    format=conf.get_config('log_params','log_format'))

logging.warning("Started")

# TODO : Mettre en place parsing des arguments (cf. main de dataimporter)
calcul_reddit_kpi.calcul_kpi_subscribers_trend()


logging.warning("Stopped")

