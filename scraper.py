
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup as soup
import requests
import yfinance as yf
import config
from finance_calendars import finance_calendars as fc
from datetime import datetime, date, timedelta
import pandas as pd

"""
stock, exchange, earnings,short_fee, volume_yesterday, Ipo_check, low_day_1,low_day_2,open_p,p_after_5,top_50_vol
"""

# Set up scraper
def get_hot_tickers():
    """
    Scrape historical ticker from hot news in finiz website
    returns: a dictionary of symbols and exchange
    """
    to_return = {}
    urls = config.urls
    for url in urls:
        req = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        webpage = req.content
        html = soup(webpage, "html.parser").find_all("td", class_="snapshot-td")

        for elt in html:
            info = elt.get_text()
            if '[' in info:
                ticker = info.split(' [')[0]
                info = info.split(' [')[1].strip(']').split(',')[0]
                #to_add = {"symbol":ticker.strip(),"exchange":info.strip()}
                to_return[ticker.strip()] = info.strip()
    
    return to_return


def get_hot_tickers_main_p():
    """
    Scrape historical ticker from hot news in finiz website
    returns: a dictionary of symbols and exchange
    """
    to_return = {}
    url = config.url
    req = requests.get("https://finviz.com", headers={'User-Agent': 'Mozilla/5.0'})
    webpage = req.content
    html = soup(webpage, "html.parser").find_all("a", class_="tab-link-nw")

    for elt in html:
        if 'quote' in elt['href']:
            info = elt.get_text()
            href = elt['href']
            print(info,href)

    return to_return



def get_earnings():
    """
    Return the earning of the current day and the day before

    """
    # Current day calendar
    try:
        earnings_td =fc.get_earnings_today()
        print(earnings_td)
        before = earnings_td[earnings_td['time']=='time-pre-market']
        after  = earnings_td[earnings_td['time']=='time-pre-market']
        unkown = earnings_td[earnings_td['time']=='time-after-hours']
    except Exception as e:
        print("Error in getting today earining calendar",e)
        before = pd.DataFrame()
        after  = pd.DataFrame()
        unkown  = pd.DataFrame()
        

    # Previous day calendar
    try:
        dt =  datetime.now() -timedelta(days=1)
        day = int(dt.day)
        mn = int(dt.month)
        yr = int(dt.year)
        earnings_yt = fc.get_earnings_by_date(datetime(yr, mn, day, 0, 0))
        before_yt = earnings_yt[earnings_yt['time']=='time-pre-market']
        after_yt  = earnings_yt[earnings_yt['time']=='time-pre-market']
        unkown_yt = earnings_yt[earnings_yt['time']=='time-after-hours']
    except Exception as e:
        print("Error in yesterday's earinings calendar",e)
        before_yt = pd.DataFrame()
        after_yt  = pd.DataFrame()
        unkown_yt  = pd.DataFrame()
    
    return {
        "today_before":before.index,
        "today_after":after.index,
        "today_unkown":unkown.index,
        "yesterday_before":before_yt.index,
        "yesterday_after":after_yt.index, 
        "yesterday_unkown":unkown_yt.index
        }


