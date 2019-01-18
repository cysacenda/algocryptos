from commons.config import Config
from slackclient import SlackClient

conf = Config()
slack_token = conf.get_config('slack', 'slack_api_token')
sc = SlackClient(slack_token)


def post_message(channel_name, message_content, attachments=''):
    if attachments == '':
        sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            text=message_content
        )
    else:
        sc.api_call(
            "chat.postMessage",
            channel=channel_name,
            text=message_content,
            attachments=attachments
        )


def post_message_to_bot_alert(message):
    post_message('bot_alerts', message)


def post_message_to_alert_error_import(message):
    post_message('alert_error_import', message)


def post_message_to_alert_error_trading(message):
    post_message('alert_error_trading', message)


def post_message_to_alert_actions_trading(message):
    post_message('alert_actions_trading', message)

def post_message_to_alert_portfolio(message):
    post_message('alert_portfolio', message)

def post_message_to_alert_log_trading(message):
    post_message('alert_log_trading', message)

def post_message_to_alert_importer_jobs(message):
    post_message('alert_importer_jobs', message)