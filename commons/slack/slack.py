from commons.config import Config
from slackclient import SlackClient

conf = Config()
slack_token = conf.get_config('slack', 'slack_api_token')
sc = SlackClient(slack_token)

def post_message(channel_name, message_content):
    sc.api_call(
        "chat.postMessage",
        channel=channel_name,
        text=message_content
    )

def post_message_to_bot_alert(message):
    post_message('bot_alerts', message)