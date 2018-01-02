import configparser

#TODO : Faire quelque chose pour que ça n'ouvre pas le fichier à chaque fois
#TODO : enum ou autre pour éviter de passer n'importe quoi
def get_config(section, key):
    config = configparser.ConfigParser()
    config.read('config/config.ini')
    return config.get(section, key)

