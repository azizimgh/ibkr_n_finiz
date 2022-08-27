from datetime import datetime
import config
import scraper
import tws
import pandas as pd
import os

def main():

    print("Code has started at ", datetime.now())

    # List of hot news from finiz
    print('Getting new hot tickers')
    hot_tickers =  scraper.get_hot_tickers()
    symbols = list(hot_tickers.keys())
    print('List of hot symbols from finiz: ','\n     '.join(list(symbols)))

    # Earnings data of  today and yesterday
    print('Getting Earinings data')
    earnings = scraper.get_earnings()

    # Klines data of symbols
    print('Getting klines data')
    klines = tws.get_klines_data(symbols)

    # Top 50 stock by volume
    print('Getting top 50 stocks by volume')
    top_50_by_vol = tws.get_top_volume_stocks()
    print(' ##'.join(top_50_by_vol))

    print('Creating follow up data frame')
    create_data_frame(hot_tickers,earnings,klines,top_50_by_vol)

    


def create_data_frame(tickers,earnings,klines,top_50_by_vol ):
    #stock, exchange, earnings,short_fee, volume_yesterday, Ipo_check, low_day_1,low_day_2,open_p,p_after_5,top_50_vol
    list_for_df = []
 
    for entry in tickers.keys():
        temp = {}
        temp['symbol'] =  entry
        temp['exchange'] =  tickers[entry]
        temp['earnings'] =  'None'
        for type_ in earnings.keys():
            print(type_,earnings[type_])
            if entry in earnings[type_]:
                temp['earnings'] = type_
        temp['short_fee'] =  0.0
        temp['volume_yesterday'] =  klines[entry]["volume_yesterday"]
        temp['Ipo_check'] =  klines[entry]["ipo"]
        temp['low_day_1'] =  klines[entry]["low_yesterday"]
        temp['low_day_2'] =  klines[entry]["low_day_before"]
        temp['open_p'] = klines[entry]["open_today"]
        temp['p_after_5'] =  0.0
        if entry in top_50_by_vol:
            temp['top_50_vol'] =  True
        else:
            temp['top_50_vol'] =  False

        list_for_df.append(temp)

    df = pd.DataFrame(list_for_df)

    # saving data into csv file
    dt =  datetime.now() 
    day = str(dt.day)
    mn = str(dt.month)
    yr = str(dt.year)
    temp = config.scrpaed_data.split('/')
    temp.append(yr+'_'+mn+'_'+day+'.csv')
    file_name = os.path.join('',*temp)
    df.to_csv(file_name,index=False)
    print(df)

