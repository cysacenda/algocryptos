from commons.utils import utils
import pandas.io.sql as psql
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from commons.config import Config
import matplotlib
matplotlib.use('Agg') # Set matplotlib use in backend mode
import matplotlib.pyplot as plt
import logging
from commons.processmanager import ProcessManager
import os

# Configuration
conf = Config()
local_images_path = utils.get_path_for_system(conf.get_config('s3_bucket', 'local_generated_images_path_linux'), conf.get_config('s3_bucket', 'local_generated_images_path'))

def generate_prices_volumes_images():
    logging.warning("generate_prices_volumes_images - start")

    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select hi.id_cryptocompare, close_price, hi.volume_aggregated, hi.timestamp from histo_ohlcv hi\n'
    squery += 'inner join coins co on (co.id_cryptocompare = hi.id_cryptocompare)\n'
    squery += 'where timestamp > CURRENT_TIMESTAMP - interval \'7 days\''
    df = psql.read_sql_query(squery, connection)

    # mandatory when different timezones in database (column not recognized as datetime)
    df['timestamp'] = pd.to_datetime(df.timestamp, utc=True)

    # set index on column timestamp
    df.set_index('timestamp', inplace = True)

    # dropna
    df2 = df.replace(0, pd.np.nan).dropna(axis=0, thresh=2).fillna(0).astype(float)

    # group by crypto
    df2 = df2.groupby('id_cryptocompare')

    # change scale to have more clear charts
    df3 = df2.resample('4H').agg({'close_price': np.mean, 'volume_aggregated': np.sum}).interpolate()
    df3 = df3.groupby('id_cryptocompare')

    # Turn interactive plotting off
    plt.ioff()

    # For each crypto => generate image
    error_count = 0
    for name, dfgroup in df3:
        try:
            fig = plt.figure()
            dfgroup.close_price.plot(legend=False, color='red', linewidth=5).axis('off')
            dfgroup.volume_aggregated.plot(secondary_y=True, style='grey', linestyle='-', linewidth=2).axis('off')
            fig.set_size_inches(5, 1.2)
            plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
            plt.savefig(local_images_path + utils.get_slash_for_system() + str(name) + ".png", dpi=30, transparent=True)
            plt.close('all')
        except Exception as e:
            error_count += 1
            logging.warning('Can''t generate image for crypto :' + str(name) + ' - ' + str(e))

    # There can be some error for some crypto, but if too much erros => process in error
    if error_count > 20:
        # Process manager
        procM = ProcessManager()
        procM.setIsError()

    logging.warning("generate_prices_volumes_images - end")