from datetime import datetime
from re import S
import time
import utils
import config
from ib_insync import *
import pandas as pd
import os


def write_traded_stock(text=''):
    """
    Write traded data to follow up
    """
    dt =  datetime.now() 
    day = str(dt.day)
    mn = str(dt.month)
    yr = str(dt.year)
    temp = config.traded_data.split('/')
    temp.append(yr+'_'+mn+'_'+day+'.csv')
    file_name = os.path.join('',*temp)
    if not os.path.exists(file_name):
        with open(file_name,'w') as fl:
            fl.write('stock,quantity,price,open,strategy,time\n')
    else:
        if text != '':
            with open(file_name,'a') as fl:
                fl.write(text+'\n')
        else:
            return pd.read_csv(file_name)['stock'].to_list()
    return []

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


def check_todays_file():
    """
    Check the first run was  made and that the data file is present
    """
    dt =  datetime.now() 
    day = str(dt.day)
    mn = str(dt.month)
    yr = str(dt.year)
    temp = config.scrpaed_data.split('/')
    temp.append(yr+'_'+mn+'_'+day+'.csv')
    file_name = os.path.join('',*temp)
    if not os.path.exists(file_name):
        utils.main()

    return file_name

def timer():
    if config.forced_run:
        return True
    else:
        while True:
            dt =  datetime.now() 
            mn = int(dt.minute)
            hour = int(dt.hour)
            if hour == config.start_hour  and mn == config.start_min:
                return True
            else:
                print(f' Waiting for {config.start_hour} h {config.start_min} mn')
def main():
    
    timer()
    write_log_file(text='Code Started')
    traded = write_traded_stock(text='')
    input_file = check_todays_file()
    write_log_file(text='Todays list of stocks created')
    df = pd.read_csv(input_file)

    ib = IB()
    ib.connect('127.0.0.1', config.tws_port, clientId=1)
    if config.allow_delayed_data:
        ib.reqMarketDataType(4)
    tickers={}
    write_log_file(text='Ib opened')
    write_log_file(text='Starting tickers price for stocks')
    for tic in df["symbol"].to_list():
        contract =  Stock(tic,'SMART','USD')
        try:
            tickers[tic] = ib.reqMktData(contract)
            ib.sleep(0.01)
            write_log_file(text="Ticker started for: "+str(tic))
  
        except Exception as e:
            write_log_file(text=f' Error in creating ticker for {tic} : {str(e)}')

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
                is_top_50 = elt['top_50_vol']
                open_ = elt['open_p']
                earnings= elt['earnings']
                price_diff = (float(prices[tic]) -float(elt['open_p']))/float(elt['open_p'])*100
                print(f' stock: {tic}  #price diff :{price_diff} #is top 50: {is_top_50}  #earnings: {earnings}')
                price= prices[tic]
                if config.use_strategy_1:
                    if config.forced_run or mn < config.strat1_minutes_to_consider:
                        if price_diff < config.strat1_decrease and tic not in traded:
                            traded.append(tic)
                            write_log_file(text="Strategy 1 criteria met for : "+str(tic)+" at decrease "+str(price_diff))
                            
                            qty = int(config.budget_pertrade / prices[tic])
                            contract = Stock(tic,'SMART','USD')
                            order_ =MarketOrder('SELL', qty)
                            ib.placeOrder(contract,order_)
                            ib.sleep(0.1)
                            #stock, quantity,price,opens,trategy, time
                            write_traded_stock(text=f'{tic},{qty},{price},{open_},strat 1,'+str(dt))
                 
                
                if config.use_strategy_2:
                    if config.forced_run or mn < config.strat2_minutes_to_consider:
                        if price_diff < config.strat2_decrease:
                            if earnings in config.strat2_earnins and tic not in traded:
                                traded.append(tic)
                                write_log_file(text="Strategy 2 criteria met for : "+str(tic)+" at decrease "+str(price_diff))
                                qty = int(config.budget_pertrade / prices[tic])
                                contract = Stock(tic,'SMART','USD')
                                order_ =MarketOrder('SELL', qty)
                                ib.placeOrder(contract,order_)
                                ib.sleep(0.1)
                                write_traded_stock(text=f'{tic},{qty},{price},{open_},strat 2,'+str(dt))

                if config.use_strategy_3:
                    if config.forced_run or mn < config.strat3_minutes_to_consider:
                        if price_diff < config.strat3_decrease and tic not in traded:
                            if is_top_50:
                                traded.append(tic)
                                write_log_file(text="Strategy 3 criteria met for : "+str(tic)+" at decrease "+str(price_diff))
                                qty = int(config.budget_pertrade / prices[tic])
                                contract = Stock(tic,'SMART','USD')
                                order_ =MarketOrder('SELL', qty)
                                ib.placeOrder(contract,order_)
                                ib.sleep(0.1)
                                write_traded_stock(text=f'{tic},{qty},{price},{open_},strat 3,'+str(dt))
                
            except Exception as e :
                print(e)
main()