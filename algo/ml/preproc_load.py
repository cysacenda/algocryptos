import pandas.io.sql as psql


# Retrieve data from DB
class PreprocLoad:
    @staticmethod
    def get_dataset_ohlcv(connection, id_cryptocompare, str_older_date):
        squery = "select oh.open_price, oh.high_price, oh.low_price, oh.close_price, oh.volume_aggregated as volume_aggregated_1h, oh.timestamp\n"  # re.reddit_subscribers,
        squery += 'from histo_ohlcv oh\n'
        squery += 'where oh.id_cryptocompare = ' + id_cryptocompare + '\n'
        squery += "and oh.timestamp > '" + str_older_date + "'\n"
        squery += 'order by oh.timestamp asc\n'
        print(squery)
        return psql.read_sql_query(squery, connection)

    @staticmethod
    def get_dataset_ohlcv_old(connection, id_cryptocompare, before_date, str_older_date):
        squery = "select oh.open_price, oh.high_price, oh.low_price, oh.close_price, oh.volume_usd as volume_aggregated_1h, oh.timestamp\n"
        squery += 'from histo_ohlcv_old oh\n'
        squery += 'where oh.id_cryptocompare = ' + id_cryptocompare + '\n'
        squery += "and oh.timestamp < '" + str(before_date) + "'\n"
        squery += "and oh.timestamp > '" + str_older_date + "'\n"
        squery += 'order by oh.timestamp desc\n'
        squery += 'limit 60\n'
        print(squery)
        return psql.read_sql_query(squery, connection)

    @staticmethod
    def get_dataset_reddit(connection, id_cryptocompare, str_older_date):
        squery = "select re.reddit_subscribers, date_trunc('day', re.timestamp) + '00:00:00' as timestamp\n"
        squery += 'from social_stats_reddit_histo re\n'
        squery += 'where re.reddit_subscribers <> 0 and re.id_cryptocompare = ' + id_cryptocompare + '\n'
        squery += "and re.timestamp > '" + str_older_date + "'\n"
        squery += 'order by re.timestamp asc\n'
        print(squery)
        return psql.read_sql_query(squery, connection)

    @staticmethod
    def get_dataset_all_cryptos(connection, str_older_date):
        squery = 'select sum(hi.close_price * hi.volume_aggregated) as global_volume_usd_1h, sum(hi.close_price * pr.available_supply) as global_market_cap_usd, hi.timestamp\n'
        squery += 'from histo_ohlcv hi\n'
        squery += 'inner join coins co on (hi.id_cryptocompare = co.id_cryptocompare)\n'
        squery += 'left outer join prices pr on (pr.id_cryptocompare = hi.id_cryptocompare)\n'
        squery += "where timestamp > '" + str_older_date + "'\n"
        squery += 'group by timestamp\n'
        squery += 'order by timestamp'
        print(squery)
        return psql.read_sql_query(squery, connection)

    @staticmethod
    def get_dataset_google_trend(connection, id_cryptocompare, period, str_older_date):
        squery = 'select value_standalone, value_compared_to_standard, timestamp\n'
        squery += 'from social_google_trend' + period + '\n'
        squery += 'where id_cryptocompare = ' + id_cryptocompare + '\n'
        squery += "and timestamp > '" + str_older_date + "'\n"
        squery += 'order by timestamp'
        print(squery)
        return psql.read_sql_query(squery, connection)

    @staticmethod
    def get_dataset_ids_top_n_cryptos(connection, top_n):
        squery = 'select id_cryptocompare from prices where crypto_rank between 1 and ' + str(top_n) + '\n'
        return psql.read_sql_query(squery, connection)
