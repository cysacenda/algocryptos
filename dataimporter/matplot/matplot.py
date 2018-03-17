from commons.utils import utils
import pandas.io.sql as psql
import numpy as np
from sqlalchemy import create_engine

import matplotlib.pyplot as plt

def generate_prices_volumes_images():
    connection = create_engine(utils.get_connection_string())

    # get data with query
    squery = 'select hi."IdCoinCryptoCompare", close, hi.volume_aggregated, hi.timestamp from histo_ohlcv hi\n'
    squery += 'inner join coins co on (co."IdCryptoCompare" = hi."IdCoinCryptoCompare")\n'
    squery += 'where timestamp > CURRENT_TIMESTAMP - interval \'7 days\''

    df = psql.read_sql_query(squery, connection)

    # set index on column timestamp
    df.set_index('timestamp', inplace = True)

    df2 = df.resample('4H').agg({'close': np.mean, 'volume_aggregated': np.sum})

    #group by crypto
    df2 = df.groupby('IdCoinCryptoCompare')

    #plt.subplots_adjust(left=0.01, right=0.01, top=0.01, bottom=0.01)
    for name, dfgroup in df2:
        fig = plt.figure()
        dfgroup.close.plot(legend=False, color='red', linewidth=5).axis('off')
        dfgroup.volume_aggregated.plot(secondary_y=True, style='grey', linestyle='-', linewidth=2).axis('off')
        fig.set_size_inches(5, 1.2)
        plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
        plt.savefig('../generated_images/' + str(name) + ".png", dpi=30, transparent=True)
        plt.close('all')