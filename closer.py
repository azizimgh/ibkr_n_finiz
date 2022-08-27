from datetime import datetime
from re import S
import time
import utils
import config
from ib_insync import *
import pandas as pd
import os



def write_log_file(text=''):
    """
    Write logs
    """
    print(text)
    dt =  datetime.now() 
    day = str(dt.day)
    mn = str(dt.month)
    yr = str(dt.year)
    temp = config.log_data.split('/')
    temp.append(yr+'_'+mn+'_'+day+'.csv')
    file_name = os.path.join('',*temp)
    if not os.path.exists(file_name):
        with open(file_name,'w') as fl:
            fl.write('time,logs'+'\n')
    else:
        with open(file_name,'a') as fl:
            fl.write(str(dt)+" :: "+text+'\n')


def main():
    traded =[]

    ib = IB()
    ib.connect('127.0.0.1', config.tws_port, clientId=10)
    if config.allow_delayed_data:
        ib.reqMarketDataType(4)
    

    dt =  datetime.now() 
    day = str(dt.day)
    mn = str(dt.month)
    yr = str(dt.year)
    temp = config.traded_data.split('/')
    temp.append(yr+'_'+mn+'_'+day+'.csv')
    file_name = os.path.join('',*temp)

    df = pd.read_csv(file_name)

    tickers={}
    write_log_file(text='Ib opened for closing')
    write_log_file(text='Starting closing tickers price for stocks')
    for tic in df["symbol"].to_list():
        contract =  Stock(tic,'SMART','USD')
        try:
            tickers[tic] = ib.reqMktData(contract)
            ib.sleep(0.01)
            write_log_file(text="Ticker Closer started for: "+str(tic))
  
        except Exception as e:
            write_log_file(text=f' Error in creating close ticker for {tic} : {str(e)}')

    dt =  datetime.now() 
    mn = int(dt.minute)
    hour = int(dt.hour)

    while config.forced_run or hour == 9 and mn < max(config.strat1_minutes_to_consider,config.strat2_minutes_to_consider,config.strat3_minutes_to_consider):
        time.sleep(1)
        dt =  datetime.now() 
        mn = int(dt.minute)
        hour = int(dt.hour)

        prices = {}
        for tic in tickers.keys():
            try:
                prices[tic] = tickers[tic].last
                ib.sleep(0.1)
                print(f"Price for : {tic} IS {prices[tic]} ")
            except Exception as e:
                print(f' Error in getting price ticker for {tic} : {str(e)}')
                prices[tic] = 100000
        
        for elt in df.to_dict('records'):
            try:
                tic = elt['symbol']
                open_p = elt['open']
                open_trade = elt['price']
                if hour ==9 and mn < 45:
                    if prices[tic] >= 1.02*open_p and tic not in traded:
                        traded.append(tic)
                        write_log_file(text="closing position for {tic} because of first condition ")
                        qty = int(elt['quantity'])
                        contract = Stock(tic,'SMART','USD')
                        order_ =MarketOrder('BUY', qty)
                        ib.placeOrder(contract,order_)
                        ib.sleep(0.1)
                        #stock, quantity,price,opens,trategy, time
              

                if hour ==9 and mn > 45:
                    if prices[tic] >= open_p and tic not in traded:
                        traded.append(tic)
                        write_log_file(text="closing position for {tic} because of second condition ")
                        qty = int(elt['quantity'])
                        contract = Stock(tic,'SMART','USD')
                        order_ =MarketOrder('BUY', qty)
                        ib.placeOrder(contract,order_)
                        ib.sleep(0.1)

                if hour>10:
                    if prices[tic] >= 0.98*open_p and tic not in traded:
                        traded.append(tic)
                        write_log_file(text="closing position for {tic} because of second condition ")
                        qty = int(elt['quantity'])
                        contract = Stock(tic,'SMART','USD')
                        order_ =MarketOrder('BUY', qty)
                        ib.placeOrder(contract,order_)
                        ib.sleep(0.1)
                
            except Exception as e :
                print(e)
main()