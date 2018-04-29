from commons.slack import slack
import logging
from commons.dbaccess import DbConnection

def create_slack_alerts():
    logging.warning("create_slack_alerts - start")
    # Get coins and associated subreddits id to be retrieved from APIs
    dbconn = DbConnection()
    query_select = 'select\n'
    query_select += 'replace(replace(replace(replace(replace(replace(alt.description, \'#val1_double#\', CAST(COALESCE(al.val1_double, 0) AS text)), \'#val2_double#\', CAST(COALESCE(al.val2_double, 0) AS text)), \'#crypto_name#\',  pr.crypto_name), \'#crypto_symbol#\', pr.symbol), \'#crypto_rank#\', CAST(pr.crypto_rank as text)), \'#val2_double#\', CAST(COALESCE(red.reddit_subscribers, 0) AS text)) as description,\n'
    query_select += 'al.timestamp\n'
    query_select += 'from alerts al\n'
    query_select += 'inner join alert_type alt on (al.id_alert_type = alt.id_alert_type)\n'
    query_select += 'left outer join prices pr on (al.id_cryptocompare = pr.id_cryptocompare)\n'
    query_select += 'left outer join prices co on (al.id_cryptocompare = co.id_cryptocompare)\n'
    query_select += 'left outer join social_stats_reddit red on (al.id_cryptocompare = red.id_cryptocompare)\n'
    query_select += 'where al.timestamp > CURRENT_TIMESTAMP - interval \'5 minutes\'\n'
    query_select += 'order by al.id_alert_type\n'
    rows = dbconn.get_query_result(query_select)

    for row in rows:
        slack.post_message_to_bot_alert(row[0])

    logging.warning("create_slack_alerts - end")

# Alert when abs of a crypto price variation > 10%
def generate_alert_price_variation_1h():
    logging.warning("generate_alert_price_variation_1h - start")
    dbconn = DbConnection()

    squery = 'insert into alerts(id_cryptocompare,id_alert_type,val1_double)\n'
    squery += 'select id_cryptocompare, 1, percent_change_1h from prices where abs(percent_change_1h) > 10 and crypto_rank < 100;'

    dbconn.exexute_query(squery)

    logging.warning("generate_alert_price_variation_1h - end")

# Alert when abs of a crypto price variation > 800%
def generate_alert_volume_variation_1h30d():
    logging.warning("generate_alert_volume_variation_1h30d - start")
    dbconn = DbConnection()

    squery = 'insert into alerts(id_cryptocompare,id_alert_type,val1_double)\n'
    squery += 'select kpv.id_cryptocompare, 2, round(CAST((volume_mean_last_1h_vs_30d * 100) AS numeric), 2)  from kpi_market_volumes kpv\n'
    squery += 'inner join prices pr on (kpv.id_cryptocompare = pr.id_cryptocompare)\n'
    squery += 'where pr.crypto_rank < 100 and abs(volume_mean_last_1h_vs_30d) > 8\n'

    dbconn.exexute_query(squery)

    logging.warning("generate_alert_volume_variation_1h30d - end")

def generate_alert_reddit_subcribers_trend_1d():
    logging.warning("generate_alert_reddit_subcribers_trend_1d - start")
    dbconn = DbConnection()

    squery = 'insert into alerts(id_cryptocompare,id_alert_type,val1_double, val2_double)\n'
    squery += 'select kps.id_cryptocompare, 3, round(CAST(kps.subscribers_1d_trend * 100 AS numeric), 2), sor.reddit_subscribers from kpi_reddit_subscribers kps\n'
    squery += 'inner join social_stats_reddit sor on (kps.id_cryptocompare = sor.id_cryptocompare)\n'
    squery += 'where (kps.subscribers_1d_trend > 0.004 and sor.reddit_subscribers > 50000)\n'
    squery += 'or (kps.subscribers_1d_trend > 0.006 and sor.reddit_subscribers > 10000)\n'
    squery += 'or (kps.subscribers_1d_trend > 0.01 and sor.reddit_subscribers > 5000)\n'
    squery += 'or (kps.subscribers_1d_trend > 0.015 and sor.reddit_subscribers > 1000)\n'
    squery += 'or (kps.subscribers_1d_trend > 0.5 and sor.reddit_subscribers > 500)\n'
    squery += 'or (kps.subscribers_1d_trend > 1 and sor.reddit_subscribers > 100)\n'

    dbconn.exexute_query(squery)

    logging.warning("generate_alert_reddit_subcribers_trend_1d - end")