import configparser
import os


class Config:
    config = None

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

    def get_config(self, section, key):
        return self.config.get(section, key)

    # allow to parse a config item to type dict
    def parse_config_dict(self, text):
        dict_config = {}
        values = text.split(',')
        for i in range(0, len(values), 2):
            dict_config[values[i]] = values[i+1]
        return dict_config
