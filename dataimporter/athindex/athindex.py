from urllib import request
from commons.config import Config
import logging

conf = Config()
URL_ATHINDEX = conf.get_config('athindex_param', 'url')

# region Scraping athindex.com

def get_athindex_query():
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
    update_query = ''
    num_current_crypto = 1
    data = byte_code.rsplit('\\n')
    start_collecting = False
    for i in range(0, len(data)):
        if start_collecting:
            crypto = __get_after(data[i], 'alt="')
            crypto = __get_before(crypto, '"')
            ath = __get_after(data[i+1], '<td data-text="')
            ath = __get_before(ath, '"')
            date_ath = __get_after(data[i+2], '">')
            date_ath = __get_before(date_ath.strip(), '<')
            num_current_crypto += 1
            start_collecting = False
            update_query += createQueryUpdate(crypto, ath, date_ath)
        elif ('<td>' + str(num_current_crypto) + '</td>' in data[i]):
            start_collecting = True
    return update_query

def createQueryUpdate(crypto, ath, date_ath):
    update_query = 'UPDATE public.ath_prices SET\n'
    update_query += 'prices_ath_usd = ' + ath + ',\n'
    update_query += 'ath_date = ' + "'" + date_ath + "',\n"
    update_query += 'last_updated = current_timestamp\n'
    update_query += 'WHERE "Name" = ' + "'" + crypto + "';\n"
    return update_query

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