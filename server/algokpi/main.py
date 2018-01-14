import logging
from config.config import Config

#Configuration
conf = Config()

# Logging params
logging.basicConfig(filename=conf.get_config('log_params','log_file'),
                    format=conf.get_config('log_params','log_format'))

logging.warning("Started")


logging.warning("Stopped")

