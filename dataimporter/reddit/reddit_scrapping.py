from urllib import request
from config.config import Config
import requests
from ratelimit import rate_limited
import logging

conf = Config()
URL_REDDITMETRIC = conf.get_config('reddit_params', 'url_redditmetric')
URL_REDDIT_START = conf.get_config('reddit_params', 'url_reddit_start')
URL_REDDIT_END = conf.get_config('reddit_params', 'url_reddit_end')


# region Scraping https://www.reddit.com/r/###SUBREDDIT_NAME###/about.json

@rate_limited(0.01)
def get_reddit_infos_real_time(subreddit):
    url = URL_REDDIT_START + subreddit + URL_REDDIT_END
    try:
        response = requests.get(url, headers={'User-agent': 'algocryptos'}).json()
    except Exception as e:
        logging.error("Error getting information from get_reddit_infos_real_time." + str(e))
        return None
    return response['data']


# endregion

# region Scraping redditmetrics.com

@rate_limited(0.01)
def get_subscribers_histo(subreddit, after_date=None):
    byte_code = __get_page_source(URL_REDDITMETRIC, subreddit)
    return __number_of_subscribers(byte_code, after_date)


def __get_after(data, sub, max_after=0):
    a_index = str(data)
    a_index = a_index.index(sub) + len(sub)
    if max_after == 0:
        return data[a_index:]
    else:
        return data[a_index:(a_index + max_after)]


# Strip anything at the end that's not a number
def __strip_ending(string):
    str_len = len(string) - 1
    counter = 0
    while string[str_len - counter] not in "0123456789":
        counter += 1
    return string[:-counter]


def __number_of_subscribers(bytecode, after_date=None):
    strdate = ''
    start_collecting_date_ok = True
    if after_date is not None:
        strdate = after_date.strftime('%Y-%m-%d')
        start_collecting_date_ok = False

    data = bytecode.rsplit('\\n')
    start_collecting = False
    subscribers_data = []
    dates_data = []
    for i in range(0, len(data)):
        if start_collecting is True:
            if "a" not in data[i]:
                return subscribers_data, dates_data
            elif "data" not in data[i]:
                number = __get_after(data[i], "a: ")
                number = __strip_ending(number)
                year = __get_after(data[i], "y: \\'", 12)
                year = __strip_ending(year)
                if start_collecting_date_ok:
                    dates_data.append(year)
                    subscribers_data.append(int(number))
                if year == strdate:
                    start_collecting_date_ok = True
        elif ("total-subscribers" in data[i]) and ("data" in data[i + 1]):
            start_collecting = True
    return subscribers_data, dates_data


def __get_page_source(url_start, subreddit):
    try:
        r = request.urlopen(url_start + subreddit)
        bytecode = r.read()
    except Exception as e:
        logging.error("Error __get_page_source : " + str(e))
        return ''

    return str(bytecode)

# endregion
