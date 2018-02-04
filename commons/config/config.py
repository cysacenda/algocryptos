import configparser
import os


class Config:
    config = None

    def __init__(self):
        self.config = configparser.RawConfigParser()
        self.config.read(os.path.join(os.path.dirname(__file__), 'config.ini'))

    def get_config(self, section, key):
        return self.config.get(section, key)
