from urllib import request
from config.config import Config
import requests
from ratelimit import rate_limited
import logging

conf = Config()
URL_ATHINDEX = conf.get_config('athindex_param', 'url')

# region Scraping athindex.com

def get_athindex():
    byte_code = __get_page_source(URL_ATHINDEX)
    return __parsedata(byte_code)

def __get_page_source(url):
    try:
        r = request.urlopen(url)
        bytecode = r.read()
    except Exception as e:
        logging.error("Error __get_page_source : " + str(e))
        return ''

    return str(bytecode)

def __parsedata(byte_code):
    data = byte_code.rsplit('\\n')
    start_collecting = False
    for i in range(0, len(data)):
        if start_collecting:
            crypto = __get_after(data[i], 'alt="')
            crypto = __get_before(crypto, '"')
            ath = __get_after(data[i+1], '<td data-text="')
            ath = __get_before(ath, '"')
            date_ath = __get_after(data[i+2], '">')
            date_ath = __get_before(date_ath, '<')
            i += 10
        elif ('<td>1</td>' in data[i]):
            start_collecting = True

# TODO : Mutualiser dans utils
def __get_after(data, sub, max_after=0):
    a_index = str(data)
    a_index = a_index.index(sub) + len(sub)
    if max_after == 0:
        return data[a_index:]
    else:
        return data[a_index:(a_index + max_after)]

def __get_before(data, sub):
    a_index = str(data)
    a_index = a_index.index(sub) + len(sub)
    return data[:a_index - 1]