import logging
from config.config import Config

#Configuration
conf = Config()

# Logging params
logging.basicConfig(filename='algokpi.log',
                    format=conf.get_config('log_params','log_format'))

logging.warning("Started")

# TODO : Mettre en place parsing des arguments (cf. main de dataimporter)



logging.warning("Stopped")

