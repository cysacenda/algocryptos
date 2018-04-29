import datetime
import logging
from slack import slack

from kpi_googletrend import calcul_googletrend_kpi
from kpi_reddit import calcul_reddit_kpi
from kpi_market import calcul_volumes_kpi
from alerts import generate_alerts
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

#slack.post_message_to_bot_alert('lol Steven')

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
        parser.add_argument('-v', '--volumes', dest="volumes", help='Calcul KPIs related to market volumes',
                            action='store_true')
        parser.add_argument('-gt', '--googletrend', dest="googletrend", help='Calcul KPIs for googletrend',
                            action='store_true')
        parser.add_argument('-g', '--global', dest="global_data", help='Calcul KPIs related to global data',
                            action='store_true')
        parser.add_argument('-al', '--alerts', dest="alerts", help='Generate alerts and send slack notifications',
                            action='store_true')

        args = parser.parse_args()

        if args.reddit:
            calcul_reddit_kpi.calcul_kpi_subscribers_trend()

        if args.volumes:
            calcul_volumes_kpi.calcul_kpi_volumes_trend()

        if args.googletrend:
            calcul_googletrend_kpi.calcul_kpi_googletrend()

        if args.global_data:
            calcul_volumes_kpi.calcul_kpi_volumes_trend_global()

        if args.alerts:
            generate_alerts.generate_alert_price_variation_1h()
            generate_alerts.generate_alert_volume_variation_1h30d()
            generate_alerts.create_slack_alerts()

except Exception as e:
    procM.setIsError()
    logging.error('Uncatched error :' + str(e))

# Stop process
procM.stop_process(IdCurrentProcess, 'AlgoKPI', sys.argv)

exit(1 if procM.IsError else 0)